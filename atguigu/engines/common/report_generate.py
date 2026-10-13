from typing import Any
from loguru import logger

from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.state import ResearchGraphState


class ReportGenerateNode(ResearchBaseNode):
    """将 Agent 的章节正文整合为独立研究报告"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """调用研究状态中的章节并生成独立报告"""
        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始生成独立报告")
        return {}
