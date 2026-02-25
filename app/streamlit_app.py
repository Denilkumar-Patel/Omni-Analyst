import os
import streamlit as st
import uuid
from dotenv import load_dotenv
from app.graph import create_research_graph

load_dotenv()

# Configure the page
st.set_page_config(page_title="Omni-Analyst", page_icon="🤖", layout="centered")
st.title("🤖 Omni-Analyst: Multi-Agent System")
st.markdown("An autonomous research workforce with Human-in-the-Loop safety.")

# Initialize our Graph and Memory Thread in Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph" not in st.session_state:
    st.session_state.graph = create_research_graph()
if "needs_approval" not in st.session_state:
    st.session_state.needs_approval = False

# The User Input
query = st.text_input("Enter your research task:", placeholder="e.g., Analyze 2026 Agentic AI trends.")

# Step 1: Run the Initial Research Phase
if st.button("Start Agents") and query:
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    initial_state = {
        "task": query,
        "research_data": [],
        "revision_count": 0,
        "is_satisfactory": False
    }
    
    # Visual feedback using st.status
    with st.status("Agents are collaborating...", expanded=True) as status:
        for output in st.session_state.graph.stream(initial_state, config=config):
            for key, value in output.items():
                st.write(f"✅ **{key.upper()}** Agent finished executing.")
                if key == "critic":
                    st.info(f"**Critic's Feedback:** {value.get('critique')}")
        
        status.update(label="Workflow paused for human review!", state="complete")
        st.session_state.needs_approval = True

# Step 2: The Human-in-the-Loop Approval UI
if st.session_state.needs_approval:
    st.warning("⚠️ The Critic has approved the raw data. Do you authorize the Writer to generate the final report?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Approve & Generate"):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            with st.spinner("Writer Agent is drafting the executive report..."):
                # Pass 'None' to resume the graph from the exact point it paused
                for output in st.session_state.graph.stream(None, config=config):
                    pass
                
                # Fetch the final output
                final_state = st.session_state.graph.get_state(config).values
                
            st.success("Report Generated Successfully!")
            st.markdown("---")
            st.markdown(final_state.get("content", ""))
            
            # Reset the state for the next research task
            st.session_state.needs_approval = False
            st.session_state.thread_id = str(uuid.uuid4()) 
            
    with col2:
        if st.button("👎 Reject & Start Over"):
            st.error("Workflow aborted. Resetting agents.")
            st.session_state.needs_approval = False
            st.session_state.thread_id = str(uuid.uuid4())