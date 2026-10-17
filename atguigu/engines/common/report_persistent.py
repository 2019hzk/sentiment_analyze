from typing import Any

from loguru import logger

from atguigu.engines.common.utils import save_report
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.state import ResearchGraphState


class ReportPersistentNode(ResearchBaseNode):
    """将 Agent 独立报告落盘"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """将研究状态中的独立报告保存到文件"""
        agent_name = get_role_display_name(self.context.role)
        final_report = state["final_report"]

        md_path = save_report(
            self.context.output_dir,
            "report.md",
            final_report
        )
        self.report_progress(f"{agent_name} 独立报告保存完成", 100)
        logger.info(f"【{agent_name}】报告落盘完成: {md_path}")
        return {}
