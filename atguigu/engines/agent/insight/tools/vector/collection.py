"""Insight 证据集合的 schema 定义与创建"""
from typing import Any

from loguru import logger
from pymilvus import DataType, MilvusClient

from atguigu.engines.contract.evidence import ENGAGEMENT_FIELDS
from atguigu.engines.contract.config import get_config_settings
from atguigu.engines.infra.milvus import get_milvus_client

MILVUS_OUTPUT_FIELDS: list[str] = [
    "doc_id",
    "platform",
    "source_type",
    "mysql_primary_key",
    "content",
    "title",
    "url",
    "topic_key",
    "published_at",
    *ENGAGEMENT_FIELDS,
    "hotness"
]


def get_collection_name() -> str:
    """获取集合名"""
    return get_config_settings().MILVUS_INSIGHT_COLLECTION


def ensure_collection(collection_name: str, drop_existing: bool = False):
    """确保 Milvus 集合存在"""
    client = get_milvus_client()
    if drop_existing and client.has_collection(collection_name):
        client.drop_collection(collection_name)
    if client.has_collection(collection_name):
        return
    client.create_collection(
        collection_name=collection_name,
        schema=build_collection_schema(client, get_config_settings().INSIGHT_DENSE_DIM),
        index_params=build_index_parameters(client),
    )
    logger.info(f"创建 Milvus 集合 {collection_name}")


def build_collection_schema(client: MilvusClient, dense_vector_dimension: int) -> Any:
    """定义 Milvus 集合字段与稠密向量列。"""
    collection_schema = client.create_schema(
        auto_id=False, enable_dynamic_field=False,
    )
    collection_schema.add_field("doc_id", DataType.VARCHAR, is_primary=True, max_length=256)
    collection_schema.add_field("platform", DataType.VARCHAR, max_length=32)
    collection_schema.add_field("source_type", DataType.VARCHAR, max_length=64)
    collection_schema.add_field("mysql_primary_key", DataType.INT64)
    collection_schema.add_field("content", DataType.VARCHAR, max_length=65535)
    collection_schema.add_field("title", DataType.VARCHAR, max_length=8192)
    collection_schema.add_field("url", DataType.VARCHAR, max_length=4096)
    collection_schema.add_field("topic_key", DataType.VARCHAR, max_length=256)
    collection_schema.add_field("published_at", DataType.INT64)
    for metric_name in ENGAGEMENT_FIELDS:
        collection_schema.add_field(metric_name, DataType.FLOAT)
    collection_schema.add_field("hotness", DataType.FLOAT)
    collection_schema.add_field(
        "dense_vector",
        DataType.FLOAT_VECTOR,
        dim=dense_vector_dimension,
    )
    return collection_schema


def build_index_parameters(client: MilvusClient) -> Any:
    """配置稠密向量索引"""
    index_parameters = client.prepare_index_params()
    index_parameters.add_index(
        field_name="dense_vector",
        index_type="AUTOINDEX",
        metric_type="COSINE"
    )
    return index_parameters
