from dataclasses import dataclass
from enum import Enum


@dataclass(slots=True)
class ReportInput:
    """综合报告生成所需的输入"""
    query: str
    insight_report: str
    media_report: str
    host_judgements: str


class ReportGenerationStatus(str, Enum):
    """综合报告生成状态"""

    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(slots=True)
class ReportGeneration:
    """单次综合报告生成过程"""

    generation_id: str
    task_id: str
    report_input: ReportInput
    markdown_content: str = ""
    status: ReportGenerationStatus = ReportGenerationStatus.RUNNING
    error_message: str = ""

    def complete(self, markdown_content: str):
        """记录报告 Markdown 内容并标记生成完成"""
        self.markdown_content = markdown_content
        self.status = ReportGenerationStatus.COMPLETED

    def fail(self, message: str):
        """记录错误并标记生成失败"""
        self.error_message = message
        self.status = ReportGenerationStatus.ERROR
