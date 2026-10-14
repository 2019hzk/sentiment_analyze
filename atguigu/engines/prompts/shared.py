SECTION_SUMMARY_USER_PROMPT = """
【写作任务】
请按照当前章节职责,基于下方实际可见的证据材料撰写本章正文。

[章节职责]
{section_context}

[实际检索请求]
{query}

[章节证据]
以下证据是本次提供的检索样本,不代表全部信息范围。
只能引用以下提供的证据。
{evidence_context}
"""
