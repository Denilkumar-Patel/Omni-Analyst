from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import load_settings
from app.state import AgentState


def critic_node(state: AgentState):
    settings = load_settings()
    llm = ChatGroq(
        model=settings.critic_model,
        temperature=0,
        groq_api_key=settings.groq_api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a senior fact-checker for an autonomous research system.
Respond strictly as JSON:
{
  "is_satisfactory": true/false,
  "feedback": "Specific feedback for improving evidence quality, source coverage, and answer readiness."
}

Approve only when the data is relevant, source-backed, and sufficient for a concise executive report.""",
            ),
            ("human", "TASK: {task}\n\nCURRENT DATA:\n{data}"),
        ]
    )

    chain = prompt | llm | JsonOutputParser()
    data_to_review = "\n\n".join(state.get("research_data", []))
    result = chain.invoke({"task": state["task"], "data": data_to_review})

    return {
        "is_satisfactory": bool(result.get("is_satisfactory", False)),
        "critique": result.get("feedback", ""),
    }
