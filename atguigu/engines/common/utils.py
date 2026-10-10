from pathlib import Path

from atguigu.engines.contract.role import RoleId
from atguigu.engines.contract.config import get_config_settings


def get_report_dir(task_id: str, role: RoleId) -> str:
    config = get_config_settings()
    log_dir = config.RUNTIME_DIR
    return str(Path(log_dir) / f"{task_id}" / f"{role}" / "report.md")
