import json
from langchain_core.prompts import PromptTemplate
from loguru import logger

from atguigu.engines.common.llm import LLMClient
from atguigu.engines.common.utils import get_report_dir, save_report
from atguigu.engines.contract.section import SECTION_DEFINITIONS
from atguigu.engines.prompts.report import (
    FINAL_REPORT_GENERATION_SYSTEM_PROMPT,
    FINAL_REPORT_GENERATION_USER_PROMPT
)
from atguigu.engines.report_engine.models import ReportGeneration, ReportInput

_llm_client = LLMClient.from_role("report")


async def generate_report(generation: ReportGeneration) -> str:
    """生成综合报告 Markdown 并保存到本地磁盘"""
    markdown = await _generate_markdown(generation.report_input)

    report_dir = get_report_dir(generation.task_id, "report")
    markdown_path = save_report(report_dir, f"{generation.generation_id}.md", markdown)
    logger.info(f"报告已落盘: {markdown_path}")

    return markdown


async def _generate_markdown(report_input: ReportInput) -> str:
    """根据结构化 Host 研判和双 Agent 报告生成最终 Markdown。"""

    # 1. 提取固定章节定义，构建最终报告的章节上下文
    section_contexts = [
        {
            "section_key": section.key,
            "title": section.title
        }
        for section in SECTION_DEFINITIONS.values()
    ]

    # 2. 将章节上下文序列化为提示词所需的 JSON
    section_contexts_json = json.dumps(
        section_contexts,
        ensure_ascii=False,
        indent=2
    )

    # 3. 结合研究主题、结构化上下文和双 Agent 原始报告构建用户提示词
    user_prompt_template = PromptTemplate.from_template(
        FINAL_REPORT_GENERATION_USER_PROMPT
    )
    user_prompt = user_prompt_template.format(
        research_topic=report_input.query,
        section_contexts=section_contexts_json,
        host_judgements=report_input.host_judgements,
        insight_report=report_input.insight_report,
        media_report=report_input.media_report
    )

    # 4. 调用报告角色的 LLM 生成最终 Markdown
    return await _llm_client.generate_text(
        FINAL_REPORT_GENERATION_SYSTEM_PROMPT,
        user_prompt
    )
