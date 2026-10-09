from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"


class ConfigSettings(BaseSettings):
    """全局配置(.env 加载的服务/模型/检索参数)"""

    HOST: str = Field("0.0.0.0", description="监听地址")
    PORT: int = Field(5000, description="监听端口")

    DB_HOST: str = Field("localhost", description="数据库主机")
    DB_PORT: int = Field(3306, description="数据库端口")
    DB_USER: str = Field("root", description="数据库用户名")
    DB_PASSWORD: str = Field("root", description="数据库密码")
    DB_NAME: str = Field("media_crawler", description="数据库名称")

    INSIGHT_AGENT_API_KEY: Optional[str] = Field(None, description="Insight 角色 API 密钥")
    INSIGHT_AGENT_BASE_URL: Optional[str] = Field(
        "https://api.moonshot.cn/v1", description="Insight 角色 BaseUrl"
    )
    INSIGHT_AGENT_MODEL_NAME: str = Field("kimi-k2-0711-preview", description="Insight 角色模型名")
    INSIGHT_AGENT_MODEL_PROVIDER: str = Field(
        "openai", description="Insight 角色厂商(langchain provider)"
    )

    MEDIA_AGENT_API_KEY: Optional[str] = Field(None, description="Media 角色 API 密钥")
    MEDIA_AGENT_BASE_URL: Optional[str] = Field(
        "https://aihubmix.com/v1", description="Media 角色 BaseUrl"
    )
    MEDIA_AGENT_MODEL_NAME: str = Field("gemini-2.5-pro", description="Media 角色模型名")
    MEDIA_AGENT_MODEL_PROVIDER: str = Field(
        "openai", description="Media 角色厂商(langchain provider)"
    )

    REPORT_ENGINE_API_KEY: Optional[str] = Field(None, description="报告引擎 API 密钥")
    REPORT_ENGINE_BASE_URL: Optional[str] = Field(
        "https://aihubmix.com/v1", description="报告引擎 BaseUrl"
    )
    REPORT_ENGINE_MODEL_NAME: str = Field("gemini-2.5-pro", description="报告引擎模型名")
    REPORT_ENGINE_MODEL_PROVIDER: str = Field(
        "openai", description="报告引擎厂商(langchain provider)"
    )

    HOST_AGENT_API_KEY: Optional[str] = Field(None, description="HostAgent API 密钥")
    HOST_AGENT_BASE_URL: Optional[str] = Field(None, description="HostAgent BaseUrl")
    HOST_AGENT_MODEL_NAME: Optional[str] = Field(None, description="HostAgent 模型名")
    HOST_AGENT_MODEL_PROVIDER: str = Field("openai", description="HostAgent 厂商(langchain provider)")

    ANSPIRE_API_KEY: Optional[str] = Field(None, description="Anspire API 密钥")
    ANSPIRE_BASE_URL: Optional[str] = Field(
        "https://plugin.anspire.cn/api/ntsearch/search", description="Anspire BaseUrl"
    )

    RUNTIME_DIR: str = Field(str(PROJECT_ROOT / "var"), description="运行时数据根目录")
    LOG_DIR: str = Field(str(PROJECT_ROOT / "var" / "logs"), description="角色日志目录")

    INSIGHT_VECTOR_ENABLED: bool = Field(
        False, description="是否为 InsightAgent 启用 Milvus 向量检索"
    )
    MILVUS_URI: str = Field("http://localhost:19530", description="Milvus 服务器地址(URI)")
    MILVUS_DB_NAME: str = Field("default", description="Milvus 数据库名称")
    MILVUS_INSIGHT_COLLECTION: str = Field(
        "insight_evidence", description="Milvus 证据集合(Collection)名称"
    )
    INSIGHT_EMBEDDING_MODEL: str = Field(
        "BAAI/bge-m3", description="Insight 检索所使用的 Embedding 模型名称/路径"
    )
    INSIGHT_EMBEDDING_DEVICE: Optional[str] = Field(
        None, description="Embedding 模型运行设备，例如 'cuda' 或 'cpu'"
    )
    INSIGHT_DENSE_DIM: int = Field(1024, description="BGE-M3 稠密向量维度")
    INSIGHT_VECTOR_FILTER_DAYS: int = Field(
        365, description="Milvus 检索的时间窗口天数限制；小于等于0则禁用时间过滤"
    )
    INSIGHT_SEMANTIC_ROUTING_ENABLED: bool = Field(
        True, description="是否为 InsightAgent 启用章节语义路由"
    )
    INSIGHT_SEMANTIC_ROUTING_MODEL: Optional[str] = Field(
        "BAAI/bge-small-zh-v1.5", description="用于章节语义路由的 SentenceTransformer 模型路径或名称"
    )
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_config_settings():
    return ConfigSettings()


def reload_config_settings() -> ConfigSettings:
    """
    1.清除缓存
    2. 重新加载新的ConfigSettings对象
    :return:
    """
    get_config_settings.cache_clear()

    return get_config_settings()
