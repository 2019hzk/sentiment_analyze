from typing import Any
from uuid import uuid4

from loguru import logger

from atguigu.app.services.report.input_loader import (
    get_report_input_status,
    load_report_input
)
from atguigu.engines.common.task import task_manager
from atguigu.engines.report_engine.engine import generate_report
from atguigu.engines.report_engine.models import (
    ReportGeneration,
    ReportGenerationStatus
)


class ReportService:
    """综合报告服务：协调输入加载、任务状态跟踪与报告引擎生成报告"""

    _report_generations: dict[str, ReportGeneration] = {}

    def get_report_status(self, task_id: str) -> dict[str, Any]:
        """获取最终报告输入文件的准备状态"""
        return get_report_input_status(task_id)

    def generate_report(self, task_id: str) -> str:
        """创建并异步启动报告生成过程"""

        # 1. 加载报告输入并创建生成记录
        report_input = load_report_input(task_id)
        generation = ReportGeneration(
            generation_id=f"generation_{uuid4().hex}",
            task_id=task_id,
            report_input=report_input
        )
        self._report_generations[generation.generation_id] = generation

        # 2. 丢到后台事件循环中异步执行生成逻辑(纳入统一任务登记)
        task_manager.create_background_task(self._run_report_generation(generation))

        # 3. 立即返回生成记录 ID 供前端轮询
        return generation.generation_id

    def get_report_result(self, generation_id: str) -> str:
        """获取已完成报告生成过程的 Markdown 内容"""
        generation = self._report_generations.get(generation_id)
        if generation is None:
            raise LookupError("报告生成记录不存在")
        if generation.status == ReportGenerationStatus.ERROR:
            raise RuntimeError(f"报告生成失败: {generation.error_message}")
        if generation.status != ReportGenerationStatus.COMPLETED:
            raise RuntimeError("报告尚未完成")
        return generation.markdown_content

    async def _run_report_generation(self, generation: ReportGeneration):
        """在后台异步执行报告生成的完整工作流"""
        try:
            # 1. 调用综合报告引擎生成最终 Markdown 报告
            markdown_content = await generate_report(generation)
            # 2. 将生成结果绑定到本次报告生成过程并标记完成
            generation.complete(markdown_content)

        except Exception as e:
            # 3. 记录日志并更新任务状态为失败
            logger.exception(f"报告生成失败: {str(e)}")
            generation.fail(str(e))
