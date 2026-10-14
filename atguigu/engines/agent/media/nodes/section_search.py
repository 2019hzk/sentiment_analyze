import asyncio
from itertools import zip_longest
from typing import Any
from loguru import logger
from atguigu.engines.agent.media.state import MediaState, MediaSectionState
from atguigu.engines.agent.media.tools.retrieval_tool import retrieve_evidence
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.evidence import RetrievedEvidence
from atguigu.engines.contract.role import get_role_display_name


class SearchNode(ResearchBaseNode):
    """遍历章节组合关键词检索并聚合去重证据"""

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """遍历章节执行检索并去重"""
        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始执行公域信息搜索")

        query = self.context.query
        sections: list[MediaSectionState] = state.get("sections")
        section_evidence_records = []
        section_queries: list[str] = []

        for section in sections:
            tool = section.get("search_tool")
            keywords = section.get("search_keywords")
            queries = [f"{query}{keyword}".strip() for keyword in keywords]

            query_results = await asyncio.gather(
                *(
                    retrieve_evidence(tool, search_query)
                    for search_query in queries
                ),
                return_exceptions=True
            )
            section_records = _merge_query_results(query_results)
            section_evidence_records.append(section_records)
            section_queries.append(
                "\n".join([f"{search_query}" for search_query in queries])
            )
        logger.info(f"{agent_name} 执行公域信息搜索完成")

        return {
            "section_evidence_records": section_evidence_records,
            "section_queries": section_queries
        }


def _merge_query_results(
        query_results: list[list[RetrievedEvidence]],
) -> list[RetrievedEvidence]:
    """轮询合并各查询的结果并按证据 ID 去重"""
    selected_records: list[RetrievedEvidence] = []
    seen_ids: set[str] = set()
    for ranked_records in zip_longest(*query_results):
        for record in ranked_records:
            if record is None or record.id in seen_ids:
                continue
            seen_ids.add(record.id)
            selected_records.append(record)
    return selected_records[:10]


if __name__ == '__main__':

    list_container1 = [1, 2, 3]
    # list_container2=[4,5]

    # for a,b in zip_longest(list_container1,list_container2):
    #     print(a,b)

    list_container1.append(None)

    for x in list_container1:
        print(x)
