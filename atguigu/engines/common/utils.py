from pathlib import Path

from atguigu.engines.contract.role import RoleId
from atguigu.engines.contract.config import get_config_settings


def get_report_dir(task_id: str, role: RoleId) -> str:
    config = get_config_settings()
    log_dir = config.RUNTIME_DIR
    return str(Path(log_dir) / f"{task_id}" / f"{role}" / "report.md")


def save_report(
        output_dir: str | Path,
        filename: str,
        content: str
) -> Path:
    """使用明确文件名将报告内容写入指定目录"""
    path = Path(output_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
