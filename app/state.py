from typing import Annotated, List, TypedDict
import operator


class AgentState(TypedDict, total=False):
    task: str
    plan: str
    research_data: Annotated[List[str], operator.add]
    content: str
    critique: str
    revision_count: int
    is_satisfactory: bool
