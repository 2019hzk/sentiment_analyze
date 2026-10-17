import asyncio


# 1. stream_events（异步生成器：负责源源不断产生数据）
async def stream_events_test():
    # 刚连上，先吐出一条连接成功事件
    yield {"event": "connected", "data": "连接成功"}

    # 模拟持续产生 3 条实时进度
    for i in range(1, 4):
        await asyncio.sleep(1)  # 模拟等待后台队列来数据（期间挂起，不占CPU）
        yield {"event": "progress", "data": f"当前研究进度 {i * 30}%"}


# 2. EventSourceResponse 内部干的活（消费者：负责抽数据并推给浏览器）
async def event_source_response_test(async_gen):
    print("HTTP 长连接已建立")

    # 用 async for 不断从生成器里把字典“抽取”出来
    async for item in async_gen:
        # 把字典格式化成 SSE 标准文本，发送给浏览器
        sse_text = f"event: {item['event']}\ndata: {item['data']}\n\n"
        print(f"推送给浏览器:\n{sse_text.strip()}\n")

    print("HTTP 长连接已关闭")


# 启动测试
asyncio.run(event_source_response_test(stream_events_test()))
