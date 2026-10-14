from pydantic import BaseModel, Field

from atguigu.engines.agent.media.tools.catalog import SearchTool


class MediaSearchPlanItem(BaseModel):
    """LLM 为单个固定章节生成的公域搜索策略"""

    search_tool: SearchTool = Field(
        description=(
            "从提供的可用搜索工具中为当前索引章节选择一个工具"
            "根据章节 title、section_guidance 和工具描述进行匹配,不得假设工具具备描述之外的能力。"
        )
    )
    search_keywords: list[str] = Field(
        min_length=1,
        max_length=3,
        description=(
            "字符串数组,包含当前索引章节使用的 1-3 个中文补充查询短语,每个查询短语只表达一个明确检索侧重点,供后续形成一次独立搜索。"
            "不要使用同义重复、宽泛空词、完整问句"
        )
    )


class MediaSearchPlanOutput(BaseModel):
    """Media Agent 搜索策略的顶层结构化输出"""

    sections: list[MediaSearchPlanItem] = Field(
        min_length=5,
        max_length=5,
        description=(
            "按用户提供的章节职责列表原始顺序生成的 5 项搜索计划;"
            "每项与索引章节一一对应,不得增删或重排。"
        )
    )
