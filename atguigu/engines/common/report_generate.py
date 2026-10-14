import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger

from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.state import ResearchGraphState
from atguigu.engines.prompts.report import RESEARCH_AGENT_REPORT_GENERATION_SYSTEM_PROMPT, \
    RESEARCH_AGENT_REPORT_GENERATION_USER_PROMPT


class ReportGenerateNode(ResearchBaseNode):
    """将 Agent 的章节正文整合为独立研究报告"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """调用研究状态中的章节并生成独立报告"""
        agent_name = get_role_display_name(self.context.role)

        query = self.context.query
        sections = state["sections"]
        logger.info(f"开始生成独立报告,舆论话题: {query},待整合章节数: {len(sections)}")

        report_context = json.dumps(
            [{"title": section["title"], "body": section["body"]} for section in sections],
            ensure_ascii=False
        )

        report_md = await self._generate_report(report_context, query)
        logger.info(f"{agent_name} 独立报告生成完成")

        return {"final_report": report_md}

    async def _generate_report(self, report_context: str, query: str) -> str:
        """调用大模型生成独立研究报告正文"""
        prompt_template = PromptTemplate.from_template(template=RESEARCH_AGENT_REPORT_GENERATION_USER_PROMPT)

        user_prompt = prompt_template.format(
            research_topic=query,
            report_context=report_context
        )

        report_md = await self.context.llm_client.generate_text(
            system_prompt=RESEARCH_AGENT_REPORT_GENERATION_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        return report_md
