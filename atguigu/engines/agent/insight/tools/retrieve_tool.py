import asyncio
import logging

import jieba.analyse

from atguigu.engines.agent.insight.tools.db.repository import call_db
from atguigu.engines.agent.insight.tools.vector.repository import call_vector
from atguigu.engines.contract.evidence import RetrievedEvidence, SourceDocument
from atguigu.engines.contract.config import get_config_settings


async def retrieval_evidence(query: str,
                             topic_key: str
                             ) -> list[RetrievedEvidence]:
    """
    职责：从两个通道查询检索的结果，并且返回检索证据对象列表(下游图中某个节点使用的)
    :param query:
    :param topic_key:
    :return:
    两个通道的检索并发执行[asyncio.gather()]，不要串行执行
    """
    # 1. 分词
    query_terms = _extract_query_terms(query)

    # 2. 并发执行MySQL通道、Milvus通道查询，获取两个通道结果
    db_evidence, vector_evidence = await asyncio.gather(
        _retrieval_db_evidence(query_terms, topic_key),
        _retrieval_vector_evidence(query, topic_key)
    )

    # 3. 将两个通道的结果组装一起，最终返回
    return [*db_evidence, *vector_evidence]


async def _retrieval_db_evidence(query_terms: list[str],
                                 topic_key: str
                                 ) -> list[RetrievedEvidence]:
    """
    职责：从MySQL通道中获取检索结果，基于模糊查询
    :param query_terms:
    :param topic_key:
    :return:
    """
    try:
        # 1. 获取词项查询结果
        db_docs = await  _query_terms(query_terms, topic_key)

        # 2. 遍历
        documents_score: dict[str, float] = dict()
        document_by_id: dict[str, SourceDocument] = {}
        for term_docs in db_docs:
            for rank, term_doc in enumerate(term_docs, start=1):
                doc_id = term_doc.doc_id
                documents_score[doc_id] = documents_score.get(doc_id, 0.0) + _compute_rank(rank)
                document_by_id.setdefault(doc_id, term_doc)

        return [
            RetrievedEvidence(
                document=document_by_id[doc_id],
                channel_scores={"db_channel": rank}
            )
            for doc_id, rank in documents_score.items()
        ]
    except Exception as  exc:
        raise  ValueError(f"MySQL通道检索失败，原因{exc}")


async def _retrieval_vector_evidence(query: str, topic_key: str) -> list[RetrievedEvidence]:
    """
    职责：从Milvus通道中获取检索结果，基于相似性检索结果
    :param query:
    :param topic_key:
    :return:
    """
    # 1. 获取Milvus通道检索的开关
    config_settings = get_config_settings()
    if not config_settings.INSIGHT_VECTOR_ENABLED:
        return []
    try:
        # 2. 异步查询Milvus获取检索结果
        vector_docs = await asyncio.to_thread(call_vector, query, 100, _build_filter_expr(topic_key))

        # 3. 返回RetrievedEvidence 对象列表
        return [
            RetrievedEvidence(document=doc,
                              channel_scores={"vector_channel": _compute_rank(rank)}
                              )
            for rank, doc in enumerate(vector_docs, start=1)
        ]
    except Exception as exc:
        logging.warning(f"Milvus向量通道检索查询失败:{str(exc)},回退到MySQL通道查询")
        return []


def _extract_query_terms(query: str) -> list[str]:
    """
    职责：对query(原始问题进行分词)
    query:高考难不难，我的孩子今年参加2026年高考    content like '%query%'-0条
    query:高考       content like '%query%'----100
    高 考  jieba（分词器：可以结合语义、了、啊、的。。。语气词切掉）：
    query:高考难不难，我的孩子今年参加2026年高考
    分词： 高考  难不难  2026高考 。。。
    :param query:
    :return:
    """

    terms: list[str] = []
    terms.append(query)  # 原始问题保留

    for term in jieba.analyse.extract_tags(query, topK=4):

        if 2 <= len(term) <= 6 and term not in terms:
            terms.append(term)

    return terms


def _build_filter_expr(topic_key: str) -> str:
    return f"topic_key=='{topic_key}'"


def _compute_rank(rank: int) -> float:
    return 1.0 / rank


async def _query_terms(query_terms: list[str], topic_key: str) -> list[list[SourceDocument]]:
    db_docs = await asyncio.gather(
        *[call_db(topic_key=topic_key, query_term=query_term)
          for query_term in query_terms]
    )
    return db_docs


if __name__ == '__main__':
    async def main():
        query = "高考难不难"
        topic_key = "高考"
        evidences = await retrieval_evidence(query=query, topic_key=topic_key)
        print(f"两个通道共检索到证据记录数:{len(evidences)}")
        for i, evidence in enumerate(evidences[:10], start=1):
            print(f"\n第{i}条:")
            print(f"记录平台: {evidence.document.platform}")
            print(f"记录来源: {evidence.document.source_type}")
            print(f"记录内容: {evidence.document.content}")
            print(f"记录所在通道得分: {evidence.channel_scores}")


    asyncio.run(main())
