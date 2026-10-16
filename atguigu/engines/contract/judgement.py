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
        description="Jev 裁决概率分布",
    )
    aligned_points: list[str] = Field(
        default_factory=list,
        description="两个 Agent 输出中相互一致的要点列表",
    )
    conflicts: list[str] = Field(
        default_factory=list,
        description="双方对同一事实、成因或趋势提出的不兼容实质性分歧列表；无实质冲突时为空列表",
    )
    evidence_review: str = Field(
        description="可核验性、来源限制与单方数据缺口说明",
    )
    host_judgement: str = Field(
        description="主持人对该章节的综合研判结论",
    )
