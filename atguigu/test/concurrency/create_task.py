import asyncio

async def fetch_data(id, delay):
    print(f"任务 {id} 开始...")
    await asyncio.sleep(delay)  # 模拟耗时 I/O 操作
    print(f"任务 {id} 完成!")
    return f"数据 {id}"

async def main():
    # 1. 创建 Task（将协程加入事件循环，后台开始运行）
    task1 = asyncio.create_task(fetch_data(1, 2))
    task2 = asyncio.create_task(fetch_data(2, 1))

    print("主程序继续执行其他逻辑...")

    # 2. 等待 Task 运行结束并获取结果
    result1 = await task1
    result2 = await task2

    print(f"获取到的结果: {result1}, {result2}")

asyncio.run(main())