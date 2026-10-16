from typing import Any, TypedDict

from atguigu.engines.agent.host.section.pair_store import SectionPairStore
from atguigu.engines.contract.events import HostDiscussionMessageEvent
from atguigu.engines.contract.judgement import SectionJudgement


class HostState(TypedDict, total=False):
    """Host LangGraph 的事件输入、章节配对与研判状态"""

    task_id: str  # 某一次研究任务
    event_payload: dict[str, Any]  # 一个章节 一个研究Agent发送的摘要
    section_pair_store: SectionPairStore  # 操作章节对的对象[读写操作] 一个章节 一个Agent发送的摘要
    judgements: list[SectionJudgement]  # 五个章节的研判后的结果【结构化对象】    # 对内给报告引擎【综合报告、（五个章节的研判后的结果）】
    discussion_events: list[HostDiscussionMessageEvent]  # 15个讨论区要展示的结果【结构化对象】  # 对外给讨论区用的
