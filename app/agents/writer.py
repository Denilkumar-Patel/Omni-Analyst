from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.state import AgentState

def writer_node(state: AgentState):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Principal Technical Writer. Transform raw research into a structured, executive-level report. 
        Use Markdown formatting. Ensure tone is objective and analytical."""),
        ("human", """ORIGINAL REQUEST: {task}
        
        VERIFIED DATA POINTS:
        {research_data}
        
        CRITIC'S FEEDBACK:
        {critique}
        
        REQUIREMENTS:
        - Use '##' for Executive Summary
        - Use '###' for Detailed Analysis
        - Include a 'Risk & Limitations' section
        - List all sources in a 'References' section.""")
    ])

    chain = prompt | llm | StrOutputParser()

    report_content = chain.invoke({
        "task": state.get("task", "Analyze the topic."),
        "research_data": "\n".join(state.get("research_data", [])),
        "critique": state.get("critique", "No critique provided. Proceed with standard formatting.")
    })

    return {
        "content": report_content
    }