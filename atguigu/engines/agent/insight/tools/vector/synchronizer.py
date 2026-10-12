"""Milvus 知识库同步器：从 MySQL 全量拉取并写入 Milvus 集合。"""

import asyncio
from typing import Any

from loguru import logger

from atguigu.engines.infra.mysql import (
    DataBaseConnectionManager,
    connection_manager,
)
from atguigu.engines.agent.insight.tools.db.sql_statement import vector_sql_statement
from atguigu.engines.agent.insight.tools.vector.collection import ensure_collection, get_collection_name
from atguigu.engines.agent.insight.tools.vector.repository import upsert_rows


async def full_sync(drop_existing: bool = False) -> int:
    """全量同步 MySQL 文档到 Milvus，返回入库文档数。"""
    all_rows = await read_all_rows()

    ensure_collection(get_collection_name(), drop_existing=drop_existing)

    return upsert_rows(all_rows)


async def read_all_rows(
        con_manager: DataBaseConnectionManager = connection_manager,
) -> list[dict[str, Any]]:
    """读取全部可索引行,正文为空的不进索引。"""
    async with con_manager.get_async_engine().connect() as connection:
        result = await connection.execute(vector_sql_statement())
        rows = result.mappings().all()
    return [
        dict(row) for row in rows
        if (row.get("content") or "").strip()
    ]


async def main():
    """执行 Milvus 知识库全量同步测试"""
    logger.info("开始启动 Milvus 知识库全量同步测试...")
    try:
        count = await full_sync(drop_existing=True)
        logger.success(f"知识库全量同步测试完成，共插入 {count} 条记录。")
    finally:
        await connection_manager.dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
