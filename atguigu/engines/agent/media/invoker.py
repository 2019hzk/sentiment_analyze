from atguigu.engines.common.llm import LLMClient


async def invoke_media_agent(
        role: str,
        query: str,
        task_id: str,
        llm_client: LLMClient,
        output_dir: str
):
    # 驱动mediaAgent定义的langraph图
    pass
