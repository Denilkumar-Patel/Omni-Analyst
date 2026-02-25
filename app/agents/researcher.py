from langchain_tavily import TavilySearch  # <-- Corrected class name!
from app.state import AgentState

def research_node(state: AgentState):
    # Initialize the updated TavilySearch class
    search = TavilySearch(max_results=3)
    query = state['task']
    
    # Execute the search
    results = search.invoke({"query": query})
    formatted_results = str(results)
    
    return {
        "research_data": [formatted_results],
        "revision_count": state.get("revision_count", 0) + 1
    }