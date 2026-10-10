"""
自定义日志处理器(记录到日志文件中[日志格式：时间日期、日志级别、模块、内容])
insight---->insight.log
media--->media.log
loguru完成
"""
from contextlib import contextmanager

from loguru import logger
from pathlib import Path
from atguigu.engines.contract.config import PROJECT_ROOT


@contextmanager
def execute_logger(role: str):
    log_dir = PROJECT_ROOT / "var"
    log_dir.mkdir(parents=True, exist_ok=True)
    with logger.contextualize(role=role):
        try:
            handler_id = logger.add(
                str(Path(log_dir) / f"{role}.log"),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | 【{extra[role]}】 {name} - {message}",
                level="INFO",
                encoding="utf-8",
                rotation="1 MB",
                filter=lambda record: record["extra"].get("role") == role
            )
            yield  # 控制权交给业务方（with 里面的逻辑）
        finally:
            logger.remove(handler_id)


if __name__ == '__main__':
    with execute_logger(role="insight"):
        # logger.info("hello2", role="insight")
        logger.info("hello3")
