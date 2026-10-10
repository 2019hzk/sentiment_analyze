from typing import Callable, Awaitable

from atguigu.engines.agent.insight.invoker import invoke_insight_agent
from atguigu.engines.agent.media.invoker import invoke_media_agent
from atguigu.engines.common.llm import LLMClient
from atguigu.engines.common.log import execute_logger
from atguigu.engines.common.task import ResearchTask, task_manager
from atguigu.engines.common.utils import get_report_dir
from atguigu.engines.contract.role import RoleId

AGENT_INVOKER: Callable[[str, str, str, LLMClient, str], Awaitable[None]]


class ResearchOrchestrator:
    def __init__(self):
        self.agent_invoker: dict[RoleId, AGENT_INVOKER] = {
            "insight": invoke_insight_agent,
            'media': invoke_media_agent
        }

    def dispatch_task(self, research_task: ResearchTask):
        """
        职责：将研究任务转发给两个研究Agent 并发执行
        :param research_task:
        :return:
        """
        for role in self.agent_invoker:
            task_manager.create_background_task(self.invoke_research_agent(role, research_task))

    async def invoke_research_agent(self, role: RoleId, research_task: ResearchTask):
        llm_client = LLMClient.from_role(role)
        output_dir = get_report_dir(research_task.task_id, role)
        with execute_logger(role):
            self.agent_invoker[role](
                role,
                research_task.query,
                research_task.task_id,
                llm_client,
                output_dir
            )
