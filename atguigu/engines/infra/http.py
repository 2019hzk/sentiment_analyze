"""第三方 HTTP API 客户端的传输层基类"""

from typing import Any, TypedDict

import httpx


class HttpRequestOptions(TypedDict, total=False):
    """统一 HTTP 请求的参数选项类型"""

    headers: dict[str, str]
    params: dict[str, Any]
    json: dict[str, Any]


class BaseHttpClient:
    """只管发请求：组 Bearer 头、发 httpx 请求、返回 JSON"""

    @staticmethod
    def build_request_headers(api_key: str, *, accept: str = "application/json") -> dict[str, str]:
        """构造 Bearer JSON 请求头"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": accept
        }
        return headers

    async def send_request(
            self,
            method: str,
            url: str,
            kwargs: HttpRequestOptions,
    ) -> dict[str, Any]:
        """用 httpx 异步发起请求并返回 JSON"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=kwargs.get("headers"),
                params=kwargs.get("params"),
                json=kwargs.get("json")
            )
            response.raise_for_status()
            data = response.json()
        return data
