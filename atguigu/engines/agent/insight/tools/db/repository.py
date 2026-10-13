import asyncio
from typing import Dict, Any
from datetime import datetime
from atguigu.engines.agent.insight.tools.db.sql_statement import db_sql_statement, topic_keys_sql_statement
from atguigu.engines.contract.evidence import SourceDocument, ENGAGEMENT_FIELDS
from atguigu.engines.infra.mysql import connection_manager


async def call_db(
        topic_key: str,
        query_term: str,
        limit: int = 100
) -> list[SourceDocument]:
    """
    职责：从数据库中根据主题进行词项内容的模糊查询
    :param topic_key:
    :param query_term:
    :param limit:
    :return:
    """

    # 1. 获取SQL语句
    sql_statement = db_sql_statement()

    # 2. 构建查询参数
    query_params: Dict[str, Any] = {
        "topic_key": topic_key,
        "search_term": f'%{query_term}%',  # 包含模糊查询字符串
        "raw_search_term": query_term,
        "prefix_search_term": f'{query_term}%',  # 前缀模糊查询字符串
        "limit": limit
    }

    # 3. 执行SQL语句(list[dict[str,Any]])

    rows: list[Dict[str, Any]] = await _get_db_rows(sql_statement, query_params)

    # 4. 结果处理
    return [_mapping_row_to_document(row) for row in rows]


async def list_topic_keys() -> list[str]:
    """读取原帖采集关键词"""
    rows = await _get_db_rows(topic_keys_sql_statement(), {})
    return [row["topic_key"] for row in rows]


async def _get_db_rows(sql_statement: Any,
                       query_params: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    职责：执行SQL语句查询 返回数据库的字典对象列表
    :param sql_statement:
    :param query_params:
    :return:
    """
    # 1. 获取session工厂
    session_factory = connection_manager.get_async_session_factory()
    async with session_factory() as session:  # 别漏掉async
        cursor_result = await session.execute(sql_statement, query_params)
        return [dict(row_mapping) for row_mapping in cursor_result.mappings().all()]


def _mapping_row_to_document(row: Dict[str, Any]) -> SourceDocument:
    return SourceDocument(
        platform=row['platform'],
        source_type=row['source_type'],
        source_id=row['mysql_primary_key'],
        content=row.get('content') or '',
        published_at=datetime.fromtimestamp(int(row['published_at'])),
        engagement_counts={
            filed: float(row[f'eng_{filed}']) for filed in ENGAGEMENT_FIELDS
        },
        hotness=float(row['hotness']),
        url=row.get('url') or '',
        title=row.get('title') or ''
    )


if __name__ == '__main__':
    async def main():
        topic_key = "高考"
        query_term = "难不难"

        docs = await call_db(topic_key, query_term)

        print(f"查询到文档的个数：{len(docs)}")
        for i, doc in enumerate(docs[:5], start=1):
            print(f"第{i}条文档:")
            print(f"文档平台: {doc.platform}")
            print(f"文档数据来源: {doc.source_type}")
            print(f"文档ID: {doc.source_id}")
            print(f"文档内容: {doc.content}")

        await connection_manager.dispose_engine()


    asyncio.run(main())
