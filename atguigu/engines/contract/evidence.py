from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


ENGAGEMENT_FIELDS = ("likes", "comments", "shares", "collects", "replies")


def build_doc_id(platform: str, source_type: str, source_id: str) -> str:
    return f"{platform}:{source_type}:{source_id}"


@dataclass(slots=True)
class SourceDocument:
    """Insight 与 Media 共用的文档对象[检索结果的归一化]。
    source_type 是 platform 之下的来源细分，与 source_id 一起构成 doc_id：
    Insight 填采集表名(douyin_aweme / douyin_aweme_comment ...)，Media 固定 "webpage"。
    hotness 是互动量的加权和，无上界，不是归一化分数；Media 侧没有互动数据，保持为 0。
    """
    # 侧重的 Insight 从本地上检索到的结果做映射
    platform: str
    source_type: str
    source_id: str
    content: str
    published_at: datetime | None
    engagement_counts: dict[str, float] = field(default_factory=dict)
    hotness: float = 0.0

    # 侧重的 Media 从网络上检索到的结果做映射
    url: str = ""
    title: str = ""

    @property
    def doc_id(self) -> str:
        """根据来源字段生成稳定文档标识"""
        return build_doc_id(self.platform, self.source_type, self.source_id)


@dataclass(slots=True)
class RetrievedEvidence:
    """被某次召回命中、作为证据。

    channel_scores 以召回通道为键。Insight 两路(db_call / vector_call)存的是检索
    服务自己按名次换算的 1/rank，并非通道原始分——MySQL 没有相关度分数，Milvus 的
    余弦距离也刻意不采用；Media(web_call)存的是搜索 Provider 返回的分数。两者分属
    独立流水线，不会放在一起比较。
    """

    document: SourceDocument
    channel_scores: dict[str, float] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """快捷获取对应证据文档的唯一标识"""
        return self.document.doc_id


