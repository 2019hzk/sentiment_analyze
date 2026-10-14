"""固定报告章节定义"""
from dataclasses import dataclass

from atguigu.engines.contract.role import RoleId

BACKGROUND_OVERVIEW = "background_overview"
HEAT_AND_SPREAD = "heat_and_spread"
SENTIMENT_AND_OPINION = "sentiment_and_opinion"
PLATFORM_AND_GROUP_DIFF = "platform_and_group_diff"
DEEP_CAUSES_AND_IMPACT = "deep_causes_and_impact"


@dataclass(slots=True)
class SectionDefinition:
    """固定章节key、标题、角色写作指导"""

    key: str
    title: str
    insight_section_guidance: str
    media_section_guidance: str
    insight_routing_keywords: tuple[str, ...] = ()

    def section_guidance_by_role(self, role: RoleId) -> str:
        """返回研究角色对应的章节写作指导"""
        if role == "insight":
            return self.insight_section_guidance
        if role == "media":
            return self.media_section_guidance
        raise ValueError(f"角色不支持章节写作指导: {role}")

    def section_context_by_role(self, role: RoleId) -> dict[str, str]:
        """返回章节职责供提示词使用"""
        return {
            "section_key": self.key,
            "title": self.title,
            "section_guidance": self.section_guidance_by_role(role)
        }


SECTION_DEFINITIONS: dict[str, SectionDefinition] = {
    BACKGROUND_OVERVIEW: SectionDefinition(
        key=BACKGROUND_OVERVIEW,
        title="事件背景与概览",
        insight_section_guidance=(
            "基于当前可见的微博、抖音帖子和评论样本梳理事件主线、讨论范围和"
            "关键时间点；仅概括材料中明确陈述的信息，不将用户表达视为已核实事实。"
        ),
        media_section_guidance=(
            "基于公开网页梳理事件主线、关键时间点、主要信源和事实框架，"
            "区分信源直接陈述、媒体转述与尚未核实的信息。"
        ),
        insight_routing_keywords=(
            "通报",
            "公告",
            "声明",
            "官方回应",
            "事发",
            "经过",
            "时间线",
            "调查",
            "进展",
            "结果",
            "现场"
        ),
    ),
    HEAT_AND_SPREAD: SectionDefinition(
        key=HEAT_AND_SPREAD,
        title="舆情热度与传播",
        insight_section_guidance=(
            "结合点赞、评论、转发等互动数据，分析微博和抖音样本中的"
            "高热内容与传播特征；不同平台指标口径不一致时避免直接比较绝对数值。"
        ),
        media_section_guidance=(
            "梳理公开报道中可识别的传播时间线、扩散节点和平台热度描述；"
            "缺少量化数据时不推断实际传播规模。"
        ),
        insight_routing_keywords=(
            "热搜",
            "热度",
            "话题榜",
            "传播",
            "阅读量",
            "播放量",
            "转发量",
            "讨论量",
            "发酵",
            "刷屏",
            "扩散",
            "引爆",
            "冲上热搜"
        )
    ),
    SENTIMENT_AND_OPINION: SectionDefinition(
        key=SENTIMENT_AND_OPINION,
        title="公众情感与观点",
        insight_section_guidance=(
            "提炼微博、抖音帖子及评论样本中的主要情绪、观点类型和典型表达，"
            "归纳重复出现或相互冲突的观点，不将当前样本视为总体民意。"
        ),
        media_section_guidance=(
            "分析公开报道的叙事倾向及其引用的公众反馈，"
            "区分媒体表述、受访者观点和用户意见。"
        ),
        insight_routing_keywords=(
            "支持",
            "反对",
            "赞同",
            "质疑",
            "吐槽",
            "愤怒",
            "担心",
            "理解",
            "争议",
            "不满",
            "失望",
            "焦虑",
            "同情",
            "谴责",
            "抵制",
            "期待",
            "嘲讽"
        )
    ),
    PLATFORM_AND_GROUP_DIFF: SectionDefinition(
        key=PLATFORM_AND_GROUP_DIFF,
        title="平台与群体差异",
        insight_section_guidance=(
            "比较微博帖子及评论、抖音作品文案及评论的讨论重点和表达差异；"
            "任一平台样本不足时明确说明，不推断缺乏证据支持的用户画像。"
        ),
        media_section_guidance=(
            "比较不同媒体网站和信源类型的选题重点、叙事角度与表达差异，"
            "说明比较范围和证据限制。"
        ),
        insight_routing_keywords=(
            "微博",
            "抖音",
            "不同平台",
            "群体差异",
            "专家",
            "大V",
            "粉丝",
            "消费者",
            "家长",
            "学生",
            "年轻人",
            "从业者",
            "当地居民"
        )
    ),
    DEEP_CAUSES_AND_IMPACT: SectionDefinition(
        key=DEEP_CAUSES_AND_IMPACT,
        title="深层原因与影响",
        insight_section_guidance=(
            "基于微博、抖音可见样本分析争议成因、潜在影响和后续舆情风险，"
            "区分用户归因、材料陈述与分析性推断。"
        ),
        media_section_guidance=(
            "基于公开报道分析社会背景、争议成因、潜在影响和传播风险，"
            "区分信源结论与媒体分析，避免将相关性表述为因果关系。"
        ),
        insight_routing_keywords=(
            "原因",
            "根源",
            "机制",
            "制度",
            "结构性",
            "利益",
            "治理",
            "风险",
            "危机",
            "信任",
            "后果",
            "隐患",
            "公信力",
            "连锁反应",
            "长期影响",
            "监管",
            "问责"
        )
    ),
}


def get_insight_routing_rules() -> dict[str, tuple[str, ...]]:
    """提取各章节的私域证据路由关键词"""
    return {
        section.key: section.insight_routing_keywords
        for section in SECTION_DEFINITIONS.values()
    }


def get_section_definitions_for_role(role: RoleId) -> list[dict[str, str]]:
    """返回指定研究角色全部章节的职责投影"""
    return [
        section.section_context_by_role(role)
        for section in SECTION_DEFINITIONS.values()
    ]


def get_section_definition_for_key(key: str) -> SectionDefinition:
    """按键名查找固定章节定义,键不存在直接 KeyError"""
    return SECTION_DEFINITIONS[key]
