from typing import Any

from langgraph.graph import END, START, StateGraph

from atguigu.engines.agent.insight.nodes.evidence_merge import EvidenceMergedNode
from atguigu.engines.agent.insight.nodes.evidence_retrieval import EvidenceRetrievalNode
from atguigu.engines.agent.insight.nodes.section_evidence_route import SectionEvidenceRouteNode
from atguigu.engines.agent.insight.nodes.section_preparation import SectionPreparationNode
from atguigu.engines.agent.insight.nodes.section_summary import SectionSummaryNode
from atguigu.engines.agent.insight.nodes.topic_route import TopicRouteNode
from atguigu.engines.agent.insight.state import InsightState
from atguigu.engines.common.report_generate import ReportGenerateNode
from atguigu.engines.common.report_persistent import ReportPersistentNode
from atguigu.engines.contract.context import ResearchRunContext, route_after_section_summary, \
    SECTION_SUMMARY_LOOP_MAPPING


def build_insight_graph(ctx: ResearchRunContext) -> Any:
    """构建并编译私域检索Agent LangGraph 工作流"""

    graph = StateGraph(InsightState)  # type: ignore
    graph.add_node("resolve_topic", TopicRouteNode(ctx))  # type: ignore
    graph.add_node("retrieve_evidence", EvidenceRetrievalNode(ctx))  # type: ignore
    graph.add_node("merge_evidence", EvidenceMergedNode(ctx))  # type: ignore
    graph.add_node("route_section_evidence", SectionEvidenceRouteNode(ctx))  # type: ignore
    graph.add_node("prepare_sections", SectionPreparationNode(ctx))  # type: ignore
    graph.add_node("summarize_sections", SectionSummaryNode(ctx))  # type: ignore
    graph.add_node("generate_report", ReportGenerateNode(ctx))  # type: ignore
    graph.add_node("persist_report", ReportPersistentNode(ctx))  # type: ignore

    graph.add_edge(START, "resolve_topic")
    graph.add_edge("resolve_topic", "retrieve_evidence")
    graph.add_edge("retrieve_evidence", "merge_evidence")
    graph.add_edge("merge_evidence", "route_section_evidence")
    graph.add_edge("route_section_evidence", "prepare_sections")
    graph.add_edge("prepare_sections", "summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING
    )
    graph.add_edge("generate_report", "persist_report")
    graph.add_edge("persist_report", END)

    return graph.compile()
