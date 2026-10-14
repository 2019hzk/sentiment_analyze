"""Web 搜索 Provider 的契约：三个检索方法及其返回类型。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from atguigu.engines.infra.http import BaseHttpClient


@dataclass(frozen=True, slots=True)
class WebpageResult:
    """单条网页检索结果的领域模型"""

    title: str
    url: str
    content: str
    date: str | None
    score: float


@dataclass(frozen=True, slots=True)
class SearchProviderResponse:
    """Provider 检索结果的统一响应模型"""
    query: str
    webpages: list[WebpageResult] = field(default_factory=list)


class BaseSearchClient(BaseHttpClient, ABC):
    """
    Web 搜索 Provider 的抽象能力基类
    三个方法名就是 SearchTool 的三个取值，属于 Media 的领域约定
    """

    @abstractmethod
    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """综合检索某主题的全面公开媒体信息"""

    @abstractmethod
    async def source_search(self, query: str) -> SearchProviderResponse:
        """溯源检索可核查的原始网页出处"""

    @abstractmethod
    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """实时检索最新报道与传播动态"""
