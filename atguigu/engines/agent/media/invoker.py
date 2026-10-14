from atguigu.engines.agent.media.graph import build_graph
from atguigu.engines.common.llm import LLMClient
from atguigu.engines.contract.context import ResearchRunContext
from atguigu.engines.contract.role import RoleId


async def invoke_media_agent(
        role: RoleId,
        query: str,
        task_id: str,
        llm_client: LLMClient,
        output_dir: str
):
    # 驱动mediaAgent定义的LanGraph图

    context = ResearchRunContext(
        task_id=task_id,
        query=query,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir
    )
    # state 只装节点间流转的中间结果，外部输入全在 context 里，所以初始状态为空
    await build_graph(context).ainvoke({})


import asyncio
from atguigu.engines.common.llm import LLMClient
from atguigu.engines.contract.role import RoleId


async def main():
    role: RoleId = "media"
    query = "高考难不难"
    task_id = "task_test_001"
    output_dir = "./test_output_001"
    llm_client = LLMClient.from_role(role)

    await invoke_media_agent(
        role=role,
        query=query,
        task_id=task_id,
        llm_client=llm_client,
        output_dir=output_dir
    )


if __name__ == "__main__":
    asyncio.run(main())
