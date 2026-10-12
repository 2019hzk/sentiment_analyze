"""进程内共享的 Milvus 客户端。"""

from pymilvus import MilvusClient

from atguigu.engines.contract.config import get_config_settings

_milvus_client: MilvusClient | None = None


def get_milvus_client() -> MilvusClient:
    """加载Milvus 客户端"""
    global _milvus_client
    if _milvus_client is None:
        settings = get_config_settings()
        _milvus_client = MilvusClient(
            uri=settings.MILVUS_URI,
            db_name=settings.MILVUS_DB_NAME,
        )
    return _milvus_client


def close_milvus_client():
    """释放客户端"""
    global _milvus_client
    if _milvus_client is not None:
        try:
            _milvus_client.close()
        finally:
            _milvus_client = None
