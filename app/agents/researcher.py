from typing import Any

from langchain_tavily import TavilySearch

from app.config import load_settings
from app.state import AgentState


def _format_search_results(response: Any) -> str:
    if not isinstance(response, dict):
        return str(response)

    answer = response.get("answer")
    results = response.get("results") or []
    formatted_results = []

    if answer:
        formatted_results.append(f"Search summary: {answer}")

    for index, result in enumerate(results, start=1):
        title = result.get("title", "Untitled source")
        url = result.get("url", "No URL")
        content = result.get("content") or result.get("raw_content") or ""
        formatted_results.append(
            f"[{index}] {title}\nURL: {url}\nExcerpt: {content[:1200]}"
        )

    return "\n\n".join(formatted_results) if formatted_results else str(response)


def research_node(state: AgentState):
    settings = load_settings()
    search = TavilySearch(max_results=settings.search_max_results)
    query = state["task"]

    if state.get("critique"):
        query = f"{query}\n\nImprove the research using this critique: {state['critique']}"

    results = search.invoke({"query": query})

    return {
        "research_data": [_format_search_results(results)],
        "revision_count": state.get("revision_count", 0) + 1,
    }
