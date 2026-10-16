import json
from typing import Any
from loguru import logger
from atguigu.engines.agent.host.discussion import build_agent_discussion_event, build_judgement_discussion_event
from atguigu.engines.agent.host.section.judge import judge_section
from atguigu.engines.agent.host.section.output import AgentSectionOutput
from atguigu.engines.agent.host.state import HostState
from atguigu.engines.common.utils import get_report_dir, save_report
from atguigu.engines.contract.role import get_role_display_name


class HostNodes:
    """Host LangGraph 的章节收集、研判与持久化节点"""

    async def collect_agent_output(self, state: HostState) -> dict[str, Any]:
        """保存当前 Agent 章节输出并生成对应讨论事件"""
        agent_output = AgentSectionOutput.from_section_ready_event(
            state["event_payload"]
        )
        state["section_pair_store"].store_output(agent_output)

        discussion_events = [
            build_agent_discussion_event(state["task_id"], agent_output)
        ]
        return {"discussion_events": discussion_events}

    async def generate_section_judgement(
            self,
            state: HostState,
    ) -> dict[str, Any]:
        """调用 Host LLM 研判当前已齐备章节，并记录研判结果与讨论事件"""
        section_pair = state["section_pair_store"].get_ready_pair()
        logger.info(f"【{get_role_display_name('host')}】双Agent章节已齐备,开始研判 章节={section_pair.section_key}")
        section_judgement = await judge_section(section_pair)

        state["section_pair_store"].mark_judged(section_judgement.section_key)
        judgements = [*state["judgements"], section_judgement]
        discussion_events = [
            *state["discussion_events"],
            build_judgement_discussion_event(
                state["task_id"],
                section_judgement
            )
        ]
        logger.info(f"【{get_role_display_name('host')}】章节研判完成 章节={section_judgement.section_key}")
        return {
            "judgements": judgements,
            "discussion_events": discussion_events
        }

    async def save_judgements(self, state: HostState) -> dict[str, Any]:
        """保存 Host 结构化研判"""
        output_dir = get_report_dir(state["task_id"], "host")

        structured_content = json.dumps(
            [judgement.model_dump() for judgement in state["judgements"]],
            ensure_ascii=False,
            indent=2
        )
        json_path = save_report(
            output_dir,
            "judgements.json",
            structured_content
        )
        logger.info(f"Host 结构化研判已保存 {json_path}")
        return {}
