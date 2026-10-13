"""四张业务表的统一投影及检索 SQL。

MySQL 是原始数据源；MySQL的关键词检索和 Milvus 同步使用同查询字段列。
"""

from sqlalchemy import text


def db_sql_statement():
    """使用冒号具名参数的 SQL；仅按记录自身内容检索。

    title 不参与匹配：微博两张表在投影里没有标题（表本身就没这个列），
    抖音原帖的 content 已经退化成 title，而评论的 title 是父帖的，
    拿它匹配会把整条评论区都捞进来。title 只作为展示用的上下文。
    """
    return text(f"""
        SELECT * FROM ({_source_sql()}) AS candidates
        WHERE topic_key = :topic_key
          AND TRIM(content) <> ''
          AND content LIKE :search_term
        ORDER BY CASE
            WHEN content = :raw_search_term THEN 0
            WHEN content LIKE :prefix_search_term THEN 1
            ELSE 2
        END ASC,
        published_at DESC, mysql_primary_key DESC
        LIMIT :limit
    """)

def vector_sql_statement():
    """全量读取可用于语义检索的四表记录。"""
    return text(f"SELECT * FROM ({_source_sql()}) AS documents")


def _number(column: str) -> str:
    """采集表的互动量是 TEXT，计算前显式转为数值"""
    return f"COALESCE(CAST(NULLIF(TRIM({column}), '') AS DECIMAL(20, 2)), 0)"


def _source_sql() -> str:
    dy_likes = _number("a.liked_count")
    dy_comments = _number("a.comment_count")
    dy_shares = _number("a.share_count")
    dy_collects = _number("a.collected_count")
    dy_comment_likes = _number("c.like_count")
    dy_replies = _number("c.sub_comment_count")
    wb_likes = _number("n.liked_count")
    wb_comments = _number("n.comments_count")
    wb_shares = _number("n.shared_count")
    wb_comment_likes = _number("c.comment_like_count")
    wb_replies = _number("c.sub_comment_count")

    return f"""
        SELECT 'douyin' AS platform, 'douyin_aweme' AS source_type,
            a.id AS mysql_primary_key,
            COALESCE(NULLIF(a.`desc`, ''), a.title, '') AS content,
            COALESCE(a.title, '') AS title,
            TRIM(COALESCE(a.source_keyword, '')) AS topic_key,
            COALESCE(a.aweme_url, '') AS url,
            a.create_time AS published_at,
            {dy_likes} AS eng_likes, {dy_comments} AS eng_comments,
            {dy_shares} AS eng_shares, {dy_collects} AS eng_collects,
            0 AS eng_replies,
            ({dy_likes} + 4 * {dy_comments} + 5 * {dy_shares}
                + 2 * {dy_collects}) AS hotness
        FROM douyin_aweme AS a
        UNION ALL
        SELECT 'douyin', 'douyin_aweme_comment', c.id,
            COALESCE(c.content, ''), COALESCE(a.title, ''),
            TRIM(COALESCE(a.source_keyword, '')),
            COALESCE(a.aweme_url, ''),
            c.create_time,
            {dy_comment_likes}, 0, 0, 0, {dy_replies},
            ({dy_comment_likes} + 3 * {dy_replies})
        FROM douyin_aweme_comment AS c
        LEFT JOIN douyin_aweme AS a ON a.id = (
            SELECT parent.id FROM douyin_aweme AS parent
            WHERE parent.aweme_id = c.aweme_id
        )
        UNION ALL
        SELECT 'weibo', 'weibo_note', n.id,
            COALESCE(n.content, ''), '', TRIM(COALESCE(n.source_keyword, '')),
            COALESCE(n.note_url, ''), n.create_time,
            {wb_likes}, {wb_comments}, {wb_shares}, 0, 0,
            ({wb_likes} + 4 * {wb_comments} + 5 * {wb_shares})
        FROM weibo_note AS n
        UNION ALL
        SELECT 'weibo', 'weibo_note_comment', c.id,
            COALESCE(c.content, ''), '', TRIM(COALESCE(n.source_keyword, '')),
            COALESCE(n.note_url, ''), c.create_time,
            {wb_comment_likes}, 0, 0, 0, {wb_replies},
            ({wb_comment_likes} + 3 * {wb_replies})
        FROM weibo_note_comment AS c
        LEFT JOIN weibo_note AS n ON n.id = (
            SELECT parent.id FROM weibo_note AS parent
            WHERE parent.note_id = c.note_id
        )
    """


def topic_keys_sql_statement():
    """仅从原帖读取非空事件标签；评论沿用所属原帖的标签。"""
    return text("""
        SELECT DISTINCT topic_key FROM (
            SELECT TRIM(source_keyword) AS topic_key FROM douyin_aweme
            UNION ALL
            SELECT TRIM(source_keyword) AS topic_key FROM weibo_note
        ) AS source_topics
        WHERE topic_key IS NOT NULL AND topic_key <> ''
        ORDER BY topic_key
    """)