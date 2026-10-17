"""研究 Agent 图的共享上下文、节点基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Callable
from atguigu.engines.common.llm import LLMClient
from atguigu.engines.contract.events import publish_role_progress, RoleProgressEvent
from atguigu.engines.contract.role import RoleId


@dataclass(slots=True)
class ResearchRunContext:
    """单次 Insight/Media 研究运行所需的共享外部数据"""
    task_id: str
    query: str
    role: RoleId
    llm_client: LLMClient
    output_dir: str


class ResearchBaseNode(ABC):
    """研究 Agent 图节点抽象基类"""

    def __init__(self, context: ResearchRunContext):
        """初始化研究节点的共享运行上下文"""
        self.context = context

    def report_progress(self, message: str, progress_pct: int):
        """上报当前节点执行进度"""
        publish_role_progress(
            RoleProgressEvent(
                task_id=self.context.task_id,
                role=self.context.role,
                message=message,
                progress_pct=progress_pct
            )
        )

    @abstractmethod
    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """节点执行入口"""


def route_after_section_summary(state: Mapping[str, Any]) -> str:
    """按游标判断继续下一章节摘要或全部完成"""
    cursor = state.get("cursor", 0)
    sections = state.get("sections")
    return "next_section" if cursor < len(sections) else "all_done"


SECTION_SUMMARY_LOOP_MAPPING = {
    "next_section": "summarize_sections",
    "all_done": "generate_report"
}
