import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.state import AgentState

def critic_node(state: AgentState):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior Fact-Checker. Review the research data and original task.
        Respond strictly in JSON format:
        {{
            "is_satisfactory": true/false,
            "feedback": "Detailed feedback for the researcher or writer."
        }}"""),
        ("human", "TASK: {task}\n\nCURRENT DATA: {data}")
    ])
    
    chain = prompt | llm | JsonOutputParser()
    
    data_to_review = "\n".join(state.get("research_data", []))
    
    result = chain.invoke({
        "task": state["task"],
        "data": data_to_review
    })
    
    return {
        "is_satisfactory": result.get("is_satisfactory", False),
        "critique": result.get("feedback", "")
    }