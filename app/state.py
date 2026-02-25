from typing import Annotated, List, TypedDict
import operator

class AgentState(TypedDict):
    # 'operator.add' allows agents to append to the list rather than overwrite it
    task: str
    plan: str
    research_data: Annotated[List[str], operator.add] 
    content: str
    revision_count: int
    is_satisfactory: bool