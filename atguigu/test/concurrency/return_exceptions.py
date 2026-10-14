import asyncio


async def task_success():
    await asyncio.sleep(1)
    return "成功的数据"


async def task_fail():
    await asyncio.sleep(1)
    raise ValueError("任务出错了！")


async def main():
    # 设置 return_exceptions=True
    results = await asyncio.gather(
        task_success(),
        task_fail(),
        return_exceptions=True
    )

    print("返回结果列表:", results)



asyncio.run(main())