from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AgentSectionOutput:
    """单个研究 Agent 发布的章节输出"""
    source: str
    section_key: str
    body: str

    @classmethod
    def from_section_ready_event(
            cls,
            event_payload: dict[str, Any]
    ) -> "AgentSectionOutput":
        """从章节就绪事件载荷构造 Agent 章节输出"""
        return cls(
            source=event_payload["source"],
            section_key=event_payload["section_key"],
            body=event_payload["body"]
        )


@dataclass(slots=True)
class AgentSectionPair:
    """同一章节的 Insight 与 Media 输出配对"""
    section_key: str
    title: str
    insight: AgentSectionOutput
    media: AgentSectionOutput
