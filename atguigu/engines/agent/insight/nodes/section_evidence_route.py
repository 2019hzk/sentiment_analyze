from typing import Any

from loguru import logger

from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name


class SectionEvidenceRouteNode(ResearchBaseNode):
    """
    按证据用途分流
    特点：同一证据记录可以支持多个章节
    """

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """前四章按结构规则归属，深层原因章由嵌入模型判定"""

        agent_name = get_role_display_name(self.context.role)
        logger.info(f"{agent_name} 开始进行章节证据路由")

        logger.info(f"{agent_name} 章节证据路由完成")
        return {"record_ids_by_section": ""}
