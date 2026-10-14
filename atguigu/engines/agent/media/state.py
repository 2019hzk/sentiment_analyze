from atguigu.engines.agent.media.tools.catalog import SearchTool
from atguigu.engines.contract.evidence import RetrievedEvidence
from atguigu.engines.contract.state import SectionState, ResearchGraphState


class MediaSectionState(SectionState):
    """公域搜索策略的研究章节状态"""

    search_tool: SearchTool
    search_keywords: list[str]


class MediaState(ResearchGraphState[MediaSectionState], total=False):  # type: ignore
    """公域搜索智能体 LangGraph 全局状态定义"""
    section_evidence_records: list[list[RetrievedEvidence]]
    section_queries: list[str]
