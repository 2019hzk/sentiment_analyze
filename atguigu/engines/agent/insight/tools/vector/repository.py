"""Milvus 稠密向量检索仓储：数据插入、检索与结果映射。"""
from datetime import datetime
from typing import Any, Mapping
from loguru import logger

from atguigu.engines.contract.evidence import ENGAGEMENT_FIELDS, SourceDocument, build_doc_id
from atguigu.engines.infra.milvus import close_milvus_client, get_milvus_client
from atguigu.engines.agent.insight.tools.vector.embedder import encode_dense
from atguigu.engines.agent.insight.tools.vector.collection import (
    MILVUS_OUTPUT_FIELDS,
    ensure_collection,
    get_collection_name
)


# ==================== 1. 写操作====================

def upsert_rows(rows: list[Mapping[str, Any]]) -> int:
    """批量向量化数据，并把 Insight 采集关键词写入索引字段。"""

    if not rows:
        return 0
    collection_name = get_collection_name()
    ensure_collection(collection_name)
    embeddings = encode_dense(row["content"] for row in rows)

    milvus_entities = [
        _row_to_entity(row, dense_vector=dense)
        for row, dense in zip(rows, embeddings)
        if dense
    ]
    if not milvus_entities:
        logger.warning(f"插入 Milvus 集合数据失败: {len(milvus_entities)}")
        return 0

    get_milvus_client().upsert(
        collection_name=collection_name, data=milvus_entities
    )
    logger.info(f"成功插入 Milvus 集合数据: {len(milvus_entities)}")
    return len(milvus_entities)


# ==================== 2. 读操作 ====================

def call_vector(
        query: str,
        limit: int,
        filter_expression: str | None = None
) -> list[SourceDocument]:
    """按查询内容执行稠密向量检索。"""
    collection_name = get_collection_name()
    client = get_milvus_client()
    if not client.has_collection(collection_name):
        logger.warning(f"Milvus 集合不存在，跳过检索: {collection_name}")
        return []
    embeddings = encode_dense([query])
    if not embeddings:
        return []
    raw_result = client.search(
        collection_name=collection_name,
        data=[embeddings[0]],
        anns_field="dense_vector",
        search_params={"metric_type": "COSINE"},
        filter=filter_expression or "",
        limit=limit,
        output_fields=MILVUS_OUTPUT_FIELDS
    )
    return _search_result_to_documents(raw_result)


def _row_to_entity(row: Mapping[str, Any], dense_vector: list[float]) -> dict[str, Any]:
    """把的数据行行映射成Milvus 实体。

    不绕道 SourceDocument：那样会把 epoch 和主键各转换两次，而且 topic_key 只进索引、
    不属于共享素材，还得靠元组另外拎着。代价是本函数和 row_to_document 都依赖投影的列名。
    """
    platform = row["platform"]
    source_type = row["source_type"]
    source_id = str(row["mysql_primary_key"])
    return {
        "platform": platform,
        "source_type": source_type,
        "doc_id": build_doc_id(platform, source_type, source_id),
        "mysql_primary_key": int(row["mysql_primary_key"]),
        "content": row["content"],
        "title": row.get("title") or "",
        "url": row.get("url") or "",
        "topic_key": str(row.get("topic_key") or ""),
        "published_at": int(row["published_at"]),
        **{
            metric_name: float(row[f"eng_{metric_name}"])
            for metric_name in ENGAGEMENT_FIELDS
        },
        "hotness": float(row["hotness"]),
        "dense_vector": dense_vector
    }


def _search_result_to_documents(raw_result: Any) -> list[SourceDocument]:
    """返回Milvus 检索结果，排序由上层按名次统一换算"""
    if not raw_result:
        return []
    documents: list[SourceDocument] = []
    for hit_dict in raw_result[0]:
        entity = hit_dict.get("entity") or {}
        documents.append(
            SourceDocument(
                platform=entity["platform"],
                source_type=entity["source_type"],
                source_id=str(entity["mysql_primary_key"]),
                content=entity["content"],
                published_at=datetime.fromtimestamp(int(entity["published_at"])),
                engagement_counts={
                    metric_name: float(entity.get(metric_name) or 0)
                    for metric_name in ENGAGEMENT_FIELDS
                },
                hotness=float(entity.get("hotness") or 0),
                title=entity.get("title") or "",
                url=entity.get("url") or ""
            )
        )
    return documents


if __name__ == "__main__":
    try:
        test_query = "高考难不难"
        top_k = 6
        documents = call_vector(query=test_query, limit=top_k)
        for idx, doc in enumerate(documents, start=1):
            print(f"[{idx}] 平台: {doc.platform} | 数据库主键: {doc.source_id}")
            print(f"    发布时间: {doc.published_at}")
            print(f"    热度得分: {doc.hotness}")
            print(f"    内容摘要: {doc.content[:50]}...")
            print("-" * 50)
    finally:
        close_milvus_client()
        logger.info("已关闭 Milvus 客户端连接")
