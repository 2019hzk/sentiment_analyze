"""Insight/Media 共享的章节摘要节点基类"""
import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger
from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.events import publish_section_ready
from atguigu.engines.contract.evidence import render_evidence_context
from atguigu.engines.contract.role import get_role_display_name
from atguigu.engines.contract.section import get_section_definition_for_key
from atguigu.engines.prompts.shared import SECTION_SUMMARY_USER_PROMPT


class BaseSectionSummaryNode(ResearchBaseNode):
    """章节摘要节点基类:游标推进、证据组装、LLM 生成摘要与事件发布"""
    system_prompt: str = ""
    fallback_body: str = ""

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """按游标取证据包生成章节正文并发布就绪事件"""
        agent_name = get_role_display_name(self.context.role)
        self.report_progress(f"{agent_name} 开始生成章节摘要", 50)

        cursor = state.get("cursor", 0)
        sections = state["sections"]
        section = sections[cursor]
        section_records = state["section_evidence_records"][cursor]

        if not section_records:
            logger.info(f"【章节 {section['section_key']}】证据上下文为空,跳过生成。")
            section["body"] = self.fallback_body
        else:
            section["body"] = await self._generate_section_body(
                section,
                query=self._query(state, cursor),
                evidence_context=render_evidence_context(section_records),
            )
        self.report_progress(f"{agent_name} 生成章节摘要完成", 60)
        publish_section_ready(section, self.context.role, self.context.task_id)
        return {"sections": sections, "cursor": cursor + 1}

    def _query(self, state: dict[str, Any], cursor: int) -> str:
        """章节证据对应的检索请求,默认取用户最初的研究问题"""
        return self.context.query

    async def _generate_section_body(
            self,
            section: dict[str, Any],
            query: str,
            evidence_context: str
    ) -> str:
        """调用 LLM 生成章节正文"""
        section_definition = get_section_definition_for_key(section["section_key"])
        section_context = section_definition.section_context_by_role(self.context.role)

        user_prompt = PromptTemplate.from_template(template=SECTION_SUMMARY_USER_PROMPT).format(
            section_context=json.dumps(section_context, ensure_ascii=False, indent=2),
            query=query,
            evidence_context=evidence_context
        )
        return await self.context.llm_client.generate_text(self.system_prompt, user_prompt)
