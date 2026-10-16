from enum import Enum
from typing import Any, Callable, Literal, Mapping

from loguru import logger
from pydantic import BaseModel

from atguigu.engines.contract.judgement import SectionJudgement
from atguigu.engines.contract.role import RoleId, get_role_display_name


class EventType(str, Enum):
    """研究流程中可发布的事件类型"""

    INTERNAL_SECTION_READY = "internal_section_ready"
    EXTERNAL_HOST_DISCUSSION_MESSAGE = "external_host_discussion_message"


class SectionReadyEvent(BaseModel):
    task_id: str
    source: str       # insight/media
    section_key: str  # 章节唯一标识
    body: str         # 章节摘要内容


class HostDiscussionMessageEvent(BaseModel):
    task_id: str
    source: Literal["insight", "media", "host"]
    content: str
    section_key: str
    judgement: SectionJudgement | None = None


EventCallback = Callable[[EventType, dict[str, Any]], None]
_subscribers: dict[EventType, set[EventCallback]] = {}


def subscribe(event_type: EventType, callback: EventCallback):
    """为指定事件类型注册订阅回调"""
    _subscribers.setdefault(event_type, set()).add(callback)


def publish(event_type: EventType, data: dict[str, Any]):
    """向指定事件类型的所有订阅者发布数据"""
    for callback in _subscribers.get(event_type, set()):
        try:
            callback(event_type, data)
        except Exception as exc:
            logger.error(f"事件订阅者执行失败：{exc}")


def unsubscribe(callback: EventCallback):
    """从所有事件类型中移除指定订阅回调"""
    for subscribers in _subscribers.values():
        subscribers.discard(callback)


def publish_section_ready(
        section: Mapping[str, Any],
        role: RoleId,
        task_id: str
):
    """从研究 Agent 图状态构造章节就绪事件"""
    agent_name = get_role_display_name(role)
    event = SectionReadyEvent(
        task_id=task_id,
        source=role,
        section_key=section["section_key"],
        body=section.get("body")
    )
    publish(EventType.INTERNAL_SECTION_READY, event.model_dump())
    logger.info(f"【章节就绪 · {agent_name}】章节={event.section_key} 内容={event.body[:20]}...")


def publish_host_discussion_message(event: HostDiscussionMessageEvent):
    """发布主持人讨论消息事件"""
    publish(EventType.EXTERNAL_HOST_DISCUSSION_MESSAGE, event.model_dump())
    speaker = get_role_display_name(event.source)
    logger.info(f"【讨论区 · {speaker}】章节={event.section_key} 内容={event.content[:20]}...")
