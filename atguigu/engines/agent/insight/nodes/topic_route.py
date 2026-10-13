"""在 Insight 检索前确定已有事件标签。"""
import asyncio
from typing import Any

from typesafe_sdk import AsyncTypeSafeClient, Choice

from atguigu.engines.contract.context import ResearchBaseNode
from atguigu.engines.contract.config import get_config_settings
from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.agent.insight.tools.db.repository import list_topic_keys


class TopicRouteNode(ResearchBaseNode):
    """读取 MySQL 事件标签，并用 Jev 选择本次研究范围"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        topics = await list_topic_keys()

        topic_key = await select_topic(self.context.query, topics)

        if topic_key not in topics:
            raise ValueError("Insight 主题选择结果不在 MySQL主题中")

        return {"topic_key": topic_key}


async def select_topic(query: str, topics: list[str]) -> str:
    """用 Jev 从已有标签中选一个，返回已有标签"""

    topic_keys = list(dict.fromkeys(topic.strip() for topic in topics if topic.strip()))
    if not topic_keys:
        raise ValueError("MySQL 中没有可供研究的主题")
    if len(topic_keys) == 1:
        return topic_keys[0]
    if len(topic_keys) > 255:
        raise ValueError(f"主题超过 Jev 单次选择上限")

    choices = {f"topic_{index}": topic for index, topic in enumerate(topic_keys)}

    async with AsyncTypeSafeClient(api_key=get_config_settings().TYPESAFE_API_KEY,
                                   model="jev-latest",
                                   timeout=30.0) as client:

        response = await client.system_one(
            state=query,
            questions={
                "topic": Choice(
                    instructions="从候选主题中选出用户希望研究的一个主要主题。",
                    criteria=choices
                ),
            },
        )

    try:
        selected = response.choices["topic"].choice

        return choices[selected]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Jev 没有返回有效的事件标签") from exc


if __name__ == '__main__':
    async def main_test():
        topics = await list_topic_keys()
        print(f"两个平台现有主题:{topics}")
        # query = "2026年NBA什么时候开打"
        query = "高考"
        selected_topic = await select_topic(query, topics)

        print(selected_topic)


    asyncio.run(main_test())
