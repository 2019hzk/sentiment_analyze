import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger
from typesafe_sdk import AsyncTypeSafeClient, Choice, ChoiceAnswer

from atguigu.engines.agent.host.section.output import AgentSectionPair
from atguigu.engines.common.llm import LLMClient
from atguigu.engines.contract.config import get_config_settings
from atguigu.engines.contract.judgement import SectionJudgement
from atguigu.engines.prompts.host import (
    HOST_SECTION_JUDGE_SYSTEM_PROMPT,
    HOST_SECTION_JUDGE_USER_PROMPT,
)

_JEV_MODEL = "jev-latest"

_VERDICT_CRITERIA: dict[str, str] = {
    "aligned": "双方核心事实与结论基本一致，仅侧重点或细节详略不同",
    "complementary": "一方有具体分析而另一方声明数据缺口/缺乏支撑/无法构建，或双方观察的时间窗口、平台、层面不同，属互补而非冲突",
    "conflicting": "双方均掌握相关数据，但对同一事实、成因或趋势提出了相互矛盾、无法同时成立的实质性主张"
}

_llm_client: LLMClient = LLMClient.from_role("host")


async def judge_section(section_pair: AgentSectionPair) -> SectionJudgement:
    """先由 Jev 单选裁决双方关系，再由 Host LLM 生成单章节结构化研判"""

    judgement_context = _build_judgement_context(section_pair)

    answer = await select_jev_verdict(judgement_context)

    jev_verdict = ""
    confidence = 0.0
    probabilities: dict[str, float] = {}
    if answer is not None:
        jev_verdict = answer.choice
        confidence = round(answer.confidence, 4)
        probabilities = {k: round(v, 4) for k, v in answer.probabilities.items()}
        logger.info(
            f"【主持人】Jev 章节裁决 章节={section_pair.section_key} "
            f"结果={jev_verdict} 置信度={confidence:.2%} 概率分布={probabilities}"
        )
        judgement_context["jev_verdict"] = {
            "verdict": jev_verdict,
            "description": _VERDICT_CRITERIA[jev_verdict],
            "confidence": confidence,
            "probabilities": probabilities
        }

    prompt = PromptTemplate.from_template(HOST_SECTION_JUDGE_USER_PROMPT).format(
        judgement_evidence=json.dumps(judgement_context, ensure_ascii=False)
    )

    judgement = await _llm_client.generate_object(
        HOST_SECTION_JUDGE_SYSTEM_PROMPT,
        prompt,
        SectionJudgement
    )

    return judgement.model_copy(
        update={
            "section_key": section_pair.section_key,
            "jev_verdict": jev_verdict,
            "confidence": confidence,
            "probabilities": probabilities
        }
    )


def _build_judgement_context(section_pair: AgentSectionPair) -> dict[str, Any]:
    """组装当前双 Agent 的同章节输出"""
    return {
        "section": {
            "key": section_pair.section_key,
            "title": section_pair.title
        },
        "insight": {"body": section_pair.insight.body[:3000]},
        "media": {"body": section_pair.media.body[:3000]}
    }


async def select_jev_verdict(
        judgement_context: dict[str, Any],
) -> ChoiceAnswer | None:
    """用 Jev 对双 Agent 同章节输出做三选一裁决；失败时降级返回 None。"""
    api_key = get_config_settings().TYPESAFE_API_KEY
    try:
        async with AsyncTypeSafeClient(api_key=api_key, model=_JEV_MODEL, timeout=30.0) as client:
            response = await client.system_one(
                state=judgement_context,
                questions={
                    "jev_verdict": Choice(
                        instructions=(
                            "判断私域舆情研究员(insight)与公开媒体研究员(media)在同一章节的结论关系。"
                            "注意：只要有一方表示'未检索到相关内容/缺乏支撑证据/无法判断或构建'，或双方观察的是不同时间窗口/不同平台/不同层面，"
                            "一律属于 complementary（单方缺口或视角互补），严禁判为 conflicting！"
                            "只有双方都给出了正面结论且彼此针锋相对、无法同时成立时才属于 conflicting。"
                        ),
                        criteria=_VERDICT_CRITERIA
                    )
                }
            )
        answer = response.choices["jev_verdict"]
        if answer.choice in _VERDICT_CRITERIA:
            return answer
    except Exception as exc:
        logger.warning(f"Jev 章节裁决失败，降级为仅由 LLM 研判: {exc}")
    return None
