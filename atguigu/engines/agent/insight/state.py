from atguigu.engines.contract.evidence import RetrievedEvidence
from atguigu.engines.contract.state import ResearchGraphState, SectionState


class InsightState(ResearchGraphState[SectionState], total=False):  # type: ignore
    """全局状态：证据处理结果、章节列表与游标"""
    topic_key: str  # jev判定的主题
    retrieved_records: list[RetrievedEvidence]  # 检索节点返回的数据，接收检索到的证据记录
    relevance_scores: dict[str, float]  # 合并节点算出的 证据记录ID → 相关性分
    record_ids_by_section: dict[str, list[str]]  # 章节路由节点算出的 章节key → 该章节的证据记录ID
    records_by_id: dict[str, RetrievedEvidence]  # 合并节点算出的 证据记录ID → 证据记录对象
    section_evidence_records: list[list[RetrievedEvidence]]  # 章节准备节点算出 五个章节的最终证据记录
