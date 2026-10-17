"""MySQL 异步引擎与会话工厂的生命周期管理"""
from typing import Optional

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from atguigu.engines.contract.config import get_config_settings


class DataBaseConnectionManager:
    """封装 MySQL 异步引擎与会话工厂与释放"""

    def __init__(self):
        """初始化数据库配置及异步连接资源"""
        self._settings = get_config_settings()
        self._async_engine: Optional[AsyncEngine] = None
        self._async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def get_async_engine(self) -> AsyncEngine:
        """返回 MySQL 异步引擎"""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                url=self._build_db_url(),
                echo=False
            )
        return self._async_engine

    def get_async_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """返回异步引擎的会话工厂"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                self.get_async_engine(),
                expire_on_commit=False
            )
        return self._async_session_factory

    async def dispose_engine(self):
        """释放异步引擎与会话工厂"""
        self._async_session_factory = None
        if self._async_engine is not None:
            try:
                await self._async_engine.dispose()
            finally:
                self._async_engine = None

    def _build_db_url(self) -> URL:
        """依据配置项拼接 MySQL 异步连接 URL"""
        return URL.create(
            drivername="mysql+aiomysql",
            username=self._settings.DB_USER,
            password=self._settings.DB_PASSWORD,
            host=self._settings.DB_HOST,
            port=self._settings.DB_PORT,
            database=self._settings.DB_NAME
        )


connection_manager = DataBaseConnectionManager()
