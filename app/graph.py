from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # <-- Add this import
from app.state import AgentState
from app.agents.researcher import research_node
from app.agents.critic import critic_node
from app.agents.writer import writer_node

def create_research_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", research_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("writer", writer_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "critic")

    workflow.add_conditional_edges(
        "critic",
        lambda state: "writer" if state["is_satisfactory"] else "researcher",
        {"writer": "writer", "researcher": "researcher"}
    )
    workflow.add_edge("writer", END)

    # Initialize memory
    memory = MemorySaver() # <-- Create the checkpointer

    # Compile with memory and interrupt before the writer acts
    return workflow.compile(
        checkpointer=memory, 
        interrupt_before=["writer"] # <-- Pause for human approval
    )