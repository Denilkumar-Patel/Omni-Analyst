from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import load_settings
from app.state import AgentState


def writer_node(state: AgentState):
    settings = load_settings()
    llm = ChatGroq(
        model=settings.writer_model,
        temperature=0.3,
        groq_api_key=settings.groq_api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a principal technical analyst. Transform verified research into a concise,
source-grounded executive report. Do not invent facts or references. If evidence is thin,
name the limitation clearly.""",
            ),
            (
                "human",
                """ORIGINAL REQUEST:
{task}

VERIFIED DATA POINTS:
{research_data}

CRITIC FEEDBACK:
{critique}

REQUIREMENTS:
- Start with "## Executive Summary"
- Include "### Key Findings"
- Include "### Risks and Limitations"
- Include "### Recommended Next Steps"
- Include "### References" with source titles and URLs when available.""",
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    report_content = chain.invoke(
        {
            "task": state.get("task", "Analyze the topic."),
            "research_data": "\n\n".join(state.get("research_data", [])),
            "critique": state.get("critique", "No critique provided."),
        }
    )

    return {"content": report_content}
