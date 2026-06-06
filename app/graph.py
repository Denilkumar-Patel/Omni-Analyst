from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.critic import critic_node
from app.agents.researcher import research_node
from app.agents.writer import writer_node
from app.config import load_settings
from app.state import AgentState


def _route_after_critic(state: AgentState) -> str:
    settings = load_settings(validate_keys=False)
    if state.get("is_satisfactory"):
        return "writer"
    if state.get("revision_count", 0) >= settings.max_revisions:
        return "writer"
    return "researcher"


def create_research_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", research_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "critic")
    workflow.add_conditional_edges(
        "critic",
        _route_after_critic,
        {"writer": "writer", "researcher": "researcher"},
    )
    workflow.add_edge("writer", END)

    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["writer"],
    )
