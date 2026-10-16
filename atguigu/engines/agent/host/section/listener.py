import asyncio
from typing import Any

from loguru import logger

from atguigu.engines.agent.host.graph import build_graph
from atguigu.engines.agent.host.section.pair_store import SectionPairStore
from atguigu.engines.agent.host.state import HostState
from atguigu.engines.common.task import task_manager
from atguigu.engines.contract.events import (
    EventType,
    publish_host_discussion_message,
    subscribe,
    unsubscribe
)


class SectionReadyListener:
    """串行消费章节就绪事件并驱动 Host LangGraph"""

    def __init__(self):
        """初始化 Host 图及任务状态存储"""
        self._graph = build_graph()
        self._host_states: dict[str, HostState] = {}
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    def start(self):
        """订阅章节就绪事件并启动消费任务"""
        subscribe(EventType.INTERNAL_SECTION_READY, self._enqueue_event)
        task_manager.create_background_task(self._process_events())
        logger.info("SectionReadyListener: 已启动 Host 章节研判")

    def stop(self):
        """取消事件订阅并释放运行状态"""
        unsubscribe(self._enqueue_event)
        self._host_states.clear()
        logger.info("SectionReadyListener: 已停止")

    def _enqueue_event(
            self,
            _event_type: EventType,
            event_payload: dict[str, Any]
    ):
        """将章节就绪事件加入串行消费队列"""
        self._event_queue.put_nowait(event_payload)


    async def _process_events(self):
        """持续消费章节就绪事件并发布 Host 讨论事件"""

        while True:
            # =================获取到数据=======================
            event_payload = await self._event_queue.get()

            # ==================内部用=====================
            task_id = event_payload["task_id"]
            host_state = self._host_states.setdefault(
                task_id,
                {
                    "task_id": task_id,
                    "section_pair_store": SectionPairStore(),
                    "judgements": []
                },
            )
            updated_state: HostState = await self._graph.ainvoke(
                {**host_state, "event_payload": event_payload}
            )
            host_state["judgements"] = updated_state["judgements"]
            discussion_events = updated_state["discussion_events"]

            # ===========外部讨论区要展示【内部产生】=============
            for discussion_event in discussion_events:
                publish_host_discussion_message(discussion_event)


section_ready_listener = SectionReadyListener()
