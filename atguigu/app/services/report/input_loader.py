from pathlib import Path
from typing import Any

from atguigu.engines.common.task import task_manager
from atguigu.engines.common.utils import get_report_dir
from atguigu.engines.contract.role import RoleId
from atguigu.engines.report_engine.models import ReportInput

_EXPECTED_REPORT_FILES: dict[RoleId, str] = {
    "insight": "report.md",
    "media": "report.md",
    "host": "judgements.json"
}


def load_report_input(task_id: str) -> ReportInput:
    """读取双 Agent 报告与 Host 研判，封装最终报告输入"""
    files = _get_expected_files(task_id)
    return ReportInput(
        query=task_manager.get_research_task(task_id).query,
        insight_report=files["insight"].read_text(encoding="utf-8"),
        media_report=files["media"].read_text(encoding="utf-8"),
        host_judgements=files["host"].read_text(encoding="utf-8")
    )


def get_report_input_status(task_id: str) -> dict[str, Any]:
    """检查所有必需角色的报告文件是否已就绪"""
    found_files = [
        f"{role}: {path.name}"
        for role, path in _get_expected_files(task_id).items()
        if path.exists()
    ]
    return {
        "task_id": task_id,
        "prepared": len(found_files) == len(_EXPECTED_REPORT_FILES),
        "found_files": found_files
    }


def _get_expected_files(task_id: str) -> dict[RoleId, Path]:
    return {
        role: Path(get_report_dir(task_id, role)) / filename
        for role, filename in _EXPECTED_REPORT_FILES.items()
    }
