from typing import Any
from loguru import logger
from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.evidence import RetrievedEvidence
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.section import SECTION_DEFINITIONS, HEAT_AND_SPREAD
from atguigu.engines.contract.state import SectionState


class SectionPreparationNode(ResearchBaseNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始固定章节与证据准备")

        sections_state: list[SectionState] = []
        section_evidence_records: list[list[RetrievedEvidence]] = []
        for section_key, section_definition in SECTION_DEFINITIONS.items():
            # 1. 构建SectionState对象
            sections_state.append({
                "section_key": section_key,
                "title": section_definition.title
            })

            # 2. 选择该章节的证据列表
            section_evidences: list[RetrievedEvidence] = _select_section_evidences(section_key, state)
            section_evidence_records.append(section_evidences[:20])

        logger.info(f"{agent_name} 固定章节与证据准备完成")
        return {
            "sections": sections_state,  # 五个章节对象list[SectionSate]
            "section_evidence_records": section_evidence_records  # 章节对应的真正证据(LLM(最终参考的上下文信息))
        }


def _select_section_evidences(section_key: str,
                              state: InsightState) -> list[RetrievedEvidence]:
    """
    职责：为章节选择证据（根据分数选择一定的证据）
    分数: 热度传播章节 先用热度分数 再用相关性检索分数
    分数：通道得分（相关性检索分数）---留给剩下四个章节用

    :param section_key:
    :param state:
    :return:
    """
    # 1. 获取基础信息
    record_ids_by_section = state['record_ids_by_section']
    records_by_id = state['records_by_id']
    relevance_scores: dict[str, float] = state['relevance_scores']
    # 2. 获取章节的证据记录对象
    section_evidences: list[RetrievedEvidence] = [
        records_by_id[doc_id]
        for doc_id in record_ids_by_section[section_key]
    ]
    relevance_score = lambda record: relevance_scores[record.id]
    if section_key == HEAT_AND_SPREAD:
        return sorted(
            section_evidences,
            key=lambda record: (record.document.hotness, relevance_score(record)),
            reverse=True
        )
    return sorted(
        section_evidences,
        key=relevance_score,
        reverse=True
    )
