"""SSE 实时事件流路由"""

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from atguigu.app.services.event_stream import event_stream

router = APIRouter(tags=["SSE实时事件流路由"])


@router.get("/api/events/stream")
async def stream_events(request: Request):
    """推送研究进度与讨论区实时 SSE 事件流"""

    # EventSourceResponse 把一个持续产生事件的生成器转换为浏览器能够接收的SSE长连接。
    return EventSourceResponse(
        event_stream.stream_events(request)
    )
