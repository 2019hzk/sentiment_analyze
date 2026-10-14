from typing import Any

from langgraph.graph import END, START, StateGraph

from atguigu.engines.agent.media.nodes.plan_search import PlanSearchNode
from atguigu.engines.agent.media.nodes.section_search import SearchNode
from atguigu.engines.agent.media.nodes.section_summary import SectionSummaryNode
from atguigu.engines.agent.media.state import MediaState
from atguigu.engines.common.report_generate import ReportGenerateNode
from atguigu.engines.common.report_persistent import ReportPersistentNode
from atguigu.engines.contract.context import ResearchRunContext, route_after_section_summary, \
    SECTION_SUMMARY_LOOP_MAPPING


def build_graph(ctx: ResearchRunContext) -> Any:
    """编排规划、检索、摘要、排版与落盘节点"""
    graph = StateGraph(MediaState)  # type: ignore
    graph.add_node("plan_search", PlanSearchNode(ctx))  # type: ignore
    graph.add_node("search", SearchNode(ctx))  # type: ignore
    graph.add_node("summarize_sections", SectionSummaryNode(ctx))  # type: ignore
    graph.add_node("generate_report", ReportGenerateNode(ctx))  # type: ignore
    graph.add_node("persist_report", ReportPersistentNode(ctx))  # type: ignore
    graph.add_edge(START, "plan_search")
    graph.add_edge("plan_search", "search")
    graph.add_edge("search", "summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING
    )
    graph.add_edge("generate_report", "persist_report")
    graph.add_edge("persist_report", END)
    return graph.compile()
