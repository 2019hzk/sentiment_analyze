from atguigu.engines.orchestrator import ResearchOrchestrator
from atguigu.engines.common.task import task_manager


class ResearchService:

    def __init__(self):
        self.orchestrator = ResearchOrchestrator()

    def start_research(self, query: str) -> str:
        """
        职责：
        1. 创建研究任务[任务管理组件]
        2. 利用协调器将本次研究任务转发走【协调器组件】
        3. 返回研究任务ID
        :param query:
        :return:
        """

        # 1.创建研究任务
        research_task = task_manager.create_research_task(query)

        # 2.  利用协调器将本次研究任务转发走【协调器组件】
        self.orchestrator.dispatch_task(research_task)

        # 3. 返回研究任务ID
        return research_task.task_id
