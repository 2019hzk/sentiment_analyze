from typing import Any

from langgraph.graph import END, START, StateGraph

from atguigu.engines.agent.host.nodes import HostNodes
from atguigu.engines.agent.host.state import HostState


def build_graph() -> Any:
    """构建并编译 Host 章节研判 LangGraph"""
    nodes = HostNodes()
    graph = StateGraph(HostState)  # type: ignore
    graph.add_node("collect_agent_output", nodes.collect_agent_output)  # type: ignore
    graph.add_node("generate_section_judgement", nodes.generate_section_judgement)  # type: ignore
    graph.add_node("save_judgements", nodes.save_judgements)  # type: ignore

    graph.add_edge(START, "collect_agent_output")
    graph.add_conditional_edges(
        "collect_agent_output",
        _route_after_output_collection,
        {
            "ready": "generate_section_judgement",
            "waiting": END,   # 一次graph图的驱动结束了，等下一个事件过来（END）
        },
    )
    graph.add_conditional_edges(
        "generate_section_judgement",
        _route_after_judgement,
        {
            "save": "save_judgements",
            "waiting": END,   # # 一次graph图的驱动结束了，等下一个事件过来(END)
        },
    )
    graph.add_edge("save_judgements", END)
    return graph.compile()


def _route_after_output_collection(state: HostState) -> str:
    """章节配对齐备时进入研判，否则结束本次事件处理"""
    return (
        "ready"
        if state["section_pair_store"].has_ready_pair()
        else "waiting"
    )


def _route_after_judgement(state: HostState) -> str:
    """全部章节研判完成时保存结构化结果，否则等待后续事件"""
    return (
        "save"
        if state["section_pair_store"].all_sections_judged()
        else "waiting"
    )
