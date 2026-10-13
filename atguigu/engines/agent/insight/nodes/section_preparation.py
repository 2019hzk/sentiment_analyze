from typing import Any
from loguru import logger
from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name


class SectionPreparationNode(ResearchBaseNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始固定章节与证据准备")


        logger.info(f"{agent_name} 固定章节与证据准备完成")

        return {
            "sections": "",
            "section_evidence_records": ""
        }

