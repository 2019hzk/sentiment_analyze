"""Media Web 检索编排与证据标准化"""

import hashlib
from datetime import datetime
from urllib.parse import urlparse

from atguigu.engines.agent.media.tools.anspire_client import AnspireSearchClient
from atguigu.engines.agent.media.tools.base import SearchProviderResponse, BaseSearchClient
from atguigu.engines.agent.media.tools.catalog import SearchTool
from atguigu.engines.contract.evidence import SourceDocument, RetrievedEvidence


async def retrieve_evidence(
        tool_name: SearchTool,
        query: str
) -> list[RetrievedEvidence]:
    """按工具执行 Web 检索并返回标准化证据"""
    response = await _search_webpage(tool_name, query)
    if response is None:
        print("xxxxx")
        return []    # 兜底
    return _map_to_evidence_records(response)


async def _search_webpage(
        tool_name: SearchTool,
        query: str
) -> SearchProviderResponse:
    """按工具类型分派综合、溯源或实时检索"""

    client = AnspireSearchClient()

    match tool_name:
        case "source_search":
            return await client.source_search(query)
        case "realtime_search":
            return await client.realtime_search(query)
        case _:
            return await client.comprehensive_search(query)


def _map_to_evidence_records(
        response: SearchProviderResponse
) -> list[RetrievedEvidence]:
    """将网页结果映射为带稳定哈希 ID 的证据记录"""

    records: list[RetrievedEvidence] = []
    for page in response.webpages:
        content = page.content
        url = page.url
        records.append(
            RetrievedEvidence(
                document=SourceDocument(
                    platform=_extract_source_name(page.url),
                    source_type="webpage",
                    source_id=_extract_source_id(content),
                    content=content,
                    published_at=_extract_published_at(page.date),
                    url=url,
                    title=page.title
                ),
                channel_scores={"web_call": page.score}
            )
        )
    return records


def _extract_source_name(url: str) -> str:
    """从网页 URL 提取标准化来源域名"""
    return urlparse(url).hostname


def _extract_published_at(date_text: str | None) -> datetime | None:
    if not date_text:
        return None
    try:
        return datetime.fromisoformat(date_text.strip()).replace(tzinfo=None)
    except ValueError:
        return None


def _extract_source_id(content: str) -> str:
    """对标准化内容生成证据唯一标识"""
    raw_key = " ".join(content.split())
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()  # type: ignore

# #
# async def main() -> None:
#     query = "g高考难不难高考讨论热度 近期传播节点"
#     tools: list[SearchTool] = ["realtime_search"]
#
#     for tool in tools:
#         print(f"测试工具: {tool} \n")
#         records = await retrieve_evidence(tool_name=tool, query=query)
#
#         print(f"共获取 {len(records)} 条证据：\n")
#         for i, rec in enumerate(records, start=1):
#             doc = rec.document
#             score = rec.channel_scores.get("web_call")
#
#             print(f"[{i}] 站点: {doc.platform}")
#             print(f"    记录唯一ID: {doc.source_id}")
#             print(f"    标题: {doc.title}")
#             print(f"    url: {doc.url}")
#             print(f"    时间: {doc.published_at}")
#             print(f"    得分: {score}")
#             print(f"    摘要: {doc.content}...\n")
#
#
# asyncio.run(main())
