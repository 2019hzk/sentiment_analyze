"""SSE 实时事件流服务"""

import asyncio
import json

from loguru import logger

from atguigu.engines.contract.events import EventType, subscribe, unsubscribe


class EventStream:
    """订阅外部事件，并通过 SSE 实时推送给在线客户端"""

    FORWARDED_EVENT_TYPES = (
        EventType.EXTERNAL_RESEARCH_AGENT_PROGRESS,
        EventType.EXTERNAL_RESEARCH_AGENT_RESULT,
        EventType.EXTERNAL_HOST_DISCUSSION_MESSAGE
    )
    _event_queue: asyncio.Queue[str] = asyncio.Queue()

    def start(self):
        """向全局事件总线注册外部事件监听"""
        for event_type in self.FORWARDED_EVENT_TYPES:
            subscribe(event_type, self._on_event)

        logger.info("EventStream：已启动SSE三种实时事件推送")

    def stop(self):
        """注销事件监听"""
        unsubscribe(self._on_event)

    def _on_event(
            self,
            event_type: EventType,
            data: dict
    ):
        """将事件总线中的外部事件放入 SSE 队列"""
        payload = json.dumps({"event": event_type, "data": data}, ensure_ascii=False)
        self._event_queue.put_nowait(payload)

    async def stream_events(self, request):
        """管理 SSE 客户端连接并持续推送实时事件"""
        logger.debug("SSE 客户端已连接")
        yield {"event": "connected", "data": json.dumps({"status": "connected"})}

        while not await request.is_disconnected():
            payload = await self._event_queue.get()
            yield {"data": payload}

        logger.debug("SSE 客户端已断开")


event_stream = EventStream()
