import asyncio
import uuid
from dataclasses import dataclass
from typing import Coroutine


@dataclass(slots=True)
class ResearchTask:
    query: str
    task_id: str


class TaskManager:
    def __init__(self):
        self.research_tasks: dict[str, ResearchTask] = {}
        self.backgrounds: set[asyncio.Task] = set()

    def create_research_task(self, query: str) -> ResearchTask:
        # 1. 创建ResearchTask
        task_id = uuid.uuid4().hex
        research_task = ResearchTask(query=query, task_id=task_id)

        # 2. 保存研究任务ID和研究任务对象(未来可以根据任务ID查询到了研究任务结果md文件)
        self.research_tasks[task_id] = research_task

        # 3. 返回
        return research_task

    def get_research_task(self, task_id: str) -> ResearchTask:
        return self.research_tasks[task_id]

    def create_background_task(self, coro: Coroutine):
        """
        职责：将携程对象，交给事件循环线程在后台并发执行
        特点："一个"事件循环线程并发执行两个异步任务【IO：读写数据库。 网络调用【发送请求】】
        :param coro:
        :return:
        """
        task = asyncio.create_task(coro)
        self.backgrounds.add(task)
        task.add_done_callback(self.backgrounds.discard)  # 优雅


task_manager = TaskManager()
