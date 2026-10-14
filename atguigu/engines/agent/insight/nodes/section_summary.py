from atguigu.engines.common.section_summary import BaseSectionSummaryNode
from atguigu.engines.prompts.insight import INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT


class SectionSummaryNode(BaseSectionSummaryNode):
    """私域章节摘要节点:基类实现具体逻辑"""
    system_prompt =  INSIGHT_SECTION_SUMMARY_SYSTEM_PROMPT
    fallback_body = "当前检索结果缺少与本章节相关的可核验证据，暂不作进一步推断。"

