from collections import defaultdict
from functools import lru_cache
from typing import Any

import numpy as np
from loguru import logger

from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.contract.config import get_config_settings
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.evidence import RetrievedEvidence
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.section import HEAT_AND_SPREAD, PLATFORM_AND_GROUP_DIFF, BACKGROUND_OVERVIEW, \
    SENTIMENT_AND_OPINION, DEEP_CAUSES_AND_IMPACT, get_insight_routing_rules, SECTION_DEFINITIONS


class SectionEvidenceRouteNode(ResearchBaseNode):
    """
    按证据用途分流
    特点：同一证据记录可以支持多个章节
    """

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """前四章按结构规则归属，深层原因章由嵌入模型判定"""

        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始进行章节证据路由")

        evidences = list((state.get('records_by_id') or {}).values())

        record_ids_by_section = _group_section_evidence_ids(evidences)

        logger.info(f"{agent_name} 章节证据路由完成")
        return {"record_ids_by_section": record_ids_by_section}  # dict[str,list[str]]


def _group_section_evidence_ids(evidences: list[RetrievedEvidence]) -> dict[str, list[str]]:
    """
    职责：为不同的章节选择对应的证据记录ID
    :param evidences:
    :return:
    """
    record_ids_by_section: dict[str, list[str]] = defaultdict(list)
    for evidence in evidences:
        section_ids: list[str] = _find_evidence_section(evidence)
        for section_id in section_ids:
            record_ids_by_section[section_id].append(evidence.id)
    return record_ids_by_section


def _find_evidence_section(evidence: RetrievedEvidence) -> list[str]:
    """
    职责：为单条记录查找章节ID
    :param evidence:
    :return:
    """
    sections: list[str] = []

    # 结构化规则
    # 1. 任意一条记录一定进入到热度与传播以及平台分类章节下
    sections.append(HEAT_AND_SPREAD)
    sections.append(PLATFORM_AND_GROUP_DIFF)

    # 2.根据记录的来源类型判定进入到背景与概览章节或者公众情感
    source_type = _record_source_type(evidence.document.source_type)
    if source_type == "content":
        sections.append(BACKGROUND_OVERVIEW)
    else:
        sections.append(SENTIMENT_AND_OPINION)

    # 语义判定规则(深层原因与影响)
    if _find_similarity_section(evidence) == DEEP_CAUSES_AND_IMPACT:
        sections.append(DEEP_CAUSES_AND_IMPACT)

    return sections


def _find_similarity_section(evidence: RetrievedEvidence) -> str:
    """
    职责：判定记录是否和原因与影响相似，如果相似返回原因与影响字符串
    机制：
    1. 记录内容---->计算向量
    2. 每一个章节的信息---->计算向量
    3. 点乘---->相似性
    :param evidence:
    :return:
    """
    # 1. 获取模型
    embedding_model = _get_embedding_model()

    # 2. 获取记录的内容
    content = (evidence.document.content or "").strip()
    evidence_vector = embedding_model.encode(content, normalize_embeddings=True)

    # 3. 获取各个章节的向量
    section_keys, section_vectors = _get_sections_vector()

    # 4. 计算二者相似
    similarity = np.dot(section_vectors, evidence_vector)

    # 5.返回最相似的章节key
    return section_keys[np.argmax(similarity)]



@lru_cache
def _get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name_or_path=get_config_settings().INSIGHT_SEMANTIC_ROUTING_MODEL)


def _get_sections_vector():
    # 1. 获取所有章节的路由关键词字典
    rules = get_insight_routing_rules()

    # 2. 获取所有章节要嵌入的内容
    section_text = [
        f"{SECTION_DEFINITIONS[key].title} {''.join(keywords)}"
        for key, keywords in rules.items()
    ]

    # 3. 调用嵌入模型
    embedding_model = _get_embedding_model()

    section_vector = embedding_model.encode(section_text, normalize_embeddings=True)

    section_keys = list(rules.keys())
    return section_keys, section_vector


def _record_source_type(source_type: str) -> str:
    return "comment" if source_type.endswith("comment") else "content"
