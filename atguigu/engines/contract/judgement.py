"""主持人结构化裁决契约：Host 与 Report 引擎共享的裁决模型"""

from typing import Literal
from pydantic import BaseModel, Field

JevVerdict = Literal["aligned", "complementary", "conflicting"]


class SectionJudgement(BaseModel):
    """主持人对单个章节的结构化裁决"""

    section_key: str = Field(default="", description="当前研判的章节标识")
    jev_verdict: str = Field(default="", description="Jev 预判的双 Agent 观点关系")
    confidence: float = Field(default=0.0, description="Jev 裁决置信度")
    probabilities: dict[str, float] = Field(
        default_factory=dict,
        description="Jev 裁决概率分布"
    )
    key_points: list[str] = Field(
        default_factory=list,
        description="围绕 Jev 预判关系提炼的核心要点（一致共识、互补维度或冲突焦点，2~4条）"
    )
    evidence_review: str = Field(
        description="双方数据来源差异、样本局限与单方数据缺口说明",
    )
    host_judgement: str = Field(
        description="主持人对该章节的综合研判结论（直接面向读者陈述结论，不要提及 Jev、字段名或内部规则）"
    )
