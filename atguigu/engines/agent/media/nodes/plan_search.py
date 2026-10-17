import json
from typing import Any
from loguru import logger
from langchain_core.prompts import PromptTemplate

from atguigu.engines.agent.media.output import MediaSearchPlanOutput
from atguigu.engines.agent.media.state import MediaState, MediaSectionState
from atguigu.engines.agent.media.tools.catalog import SEARCH_TOOL_DESCRIPTIONS
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.section import (
    SECTION_DEFINITIONS,
    get_section_definitions_for_role
)
from atguigu.engines.prompts.media import MEDIA_SEARCH_PLAN_USER_PROMPT, MEDIA_SEARCH_PLAN_SYSTEM_PROMPT


class PlanSearchNode(ResearchBaseNode):
    """为固定 Media 章节生成搜索工具与关键词"""

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """调用 LLM 生成搜索策略，并与固定章节定义合并为运行状态"""
        agent_name = get_role_display_name(self.context.role)
        self.report_progress(f"{agent_name} 开始规划公域搜索策略", 10)

        planned_output = await self._generate_search_plan(self.context.query)

        sections: list[MediaSectionState] = [
            MediaSectionState(
                section_key=section_definition.key,
                title=section_definition.title,
                search_tool=planed_section.search_tool,
                search_keywords=[keyword.strip() for keyword in planed_section.search_keywords]
            )
            for section_definition, planed_section in zip(
                SECTION_DEFINITIONS.values(),
                planned_output.sections
            )
        ]
        self.report_progress(f"{agent_name} 公域搜索策略规划完成", 20)
        return {"sections": sections}

    async def _generate_search_plan(
            self,
            research_topic: str
    ) -> MediaSearchPlanOutput:
        """组装搜索规划提示词并调用 LLM 返回结构化搜索计划"""

        search_tools = [
            {"name": tool, "description": description}
            for tool, description in SEARCH_TOOL_DESCRIPTIONS.items()
        ]

        user_prompt = PromptTemplate.from_template(MEDIA_SEARCH_PLAN_USER_PROMPT).format(
            research_topic=research_topic,
            section_contexts=json.dumps(
                get_section_definitions_for_role("media"),
                ensure_ascii=False,
                indent=2
            ),
            search_tools=json.dumps(
                search_tools,
                ensure_ascii=False,
                indent=2
            )
        )

        return await self.context.llm_client.generate_object(
            system_prompt=MEDIA_SEARCH_PLAN_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            structed_object=MediaSearchPlanOutput
        )
