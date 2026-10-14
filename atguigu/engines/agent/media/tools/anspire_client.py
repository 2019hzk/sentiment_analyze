import datetime
from typing import Any
from loguru import logger

from atguigu.engines.agent.media.tools.base import (
    BaseSearchClient,
    SearchProviderResponse,
    WebpageResult
)
from atguigu.engines.common.retryer import with_retry
from atguigu.engines.contract.config import get_config_settings

AUTHORITATIVE_SOURCES = (
    "www.gov.cn,"
    "news.cn,"
    "xinhuanet.com,"
    "people.com.cn,"
    "news.cctv.com,"
    "chinanews.com.cn"
)
SOCIAL_SOURCES = "weibo.com,zhihu.com,toutiao.com"


class AnspireSearchClient(BaseSearchClient):
    """Anspire Web 检索 Provider 实现"""

    def __init__(self):
        """读取 Anspire 密钥与地址并构建请求头"""
        super().__init__()
        self.api_key = get_config_settings().ANSPIRE_API_KEY
        self.base_url = get_config_settings().ANSPIRE_BASE_URL
        self.headers = self.build_request_headers(self.api_key)

    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """全量检索,不限站点"""
        return await self._execute_search(query=query, top_k=15)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """在官方媒体站点执行溯源检索"""
        return await self._execute_search(query=query, top_k=10, insite=AUTHORITATIVE_SOURCES)

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """在近一周社交站点范围内执行时效性检索"""
        to_time = datetime.datetime.now()
        from_time = to_time - datetime.timedelta(weeks=1)
        return await self._execute_search(
            query=query,
            top_k=5,
            insite=SOCIAL_SOURCES,
            from_time=from_time.strftime("%Y-%m-%d %H:%M:%S"),
            to_time=to_time.strftime("%Y-%m-%d %H:%M:%S")
        )

    @with_retry
    async def _execute_search(
            self,
            query: str,
            top_k: int,
            insite: str = "",
            from_time: str = "",
            to_time: str = ""
    ) -> SearchProviderResponse:
        """组装参数发起 GET 并解析响应"""

        params = {
            "query": query,
            "top_k": top_k,
            "Insite": insite,
            "FromTime": from_time,
            "ToTime": to_time
        }

        response = await self.send_request(
            "GET",
            self.base_url,
            {"headers": self.headers, "params": params}
        )

        return self._process_response(response, query)

    @staticmethod
    def _process_response(response_dict: dict[str, Any], query: str) -> SearchProviderResponse:
        """将 Anspire 原始结果映射为网页模型"""
        results = response_dict.get("results")
        webpages: list[WebpageResult] = []
        for result in results:
            webpages.append(
                WebpageResult(
                    title=result.get("title"),
                    url=result.get("url"),
                    content=result.get("content"),
                    date=result.get("date"),
                    score=result.get("score")
                )
            )
        return SearchProviderResponse(
            query=query,
            webpages=webpages
        )
