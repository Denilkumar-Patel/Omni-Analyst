import os
import uuid

import streamlit as st
from dotenv import load_dotenv

from app.config import load_settings
from app.graph import create_research_graph


load_dotenv()

for secret_name in ("GROQ_API_KEY", "TAVILY_API_KEY"):
    if not os.getenv(secret_name) and secret_name in st.secrets:
        os.environ[secret_name] = str(st.secrets[secret_name])

st.set_page_config(page_title="Omni-Analyst", layout="centered")
st.title("Omni-Analyst")
st.caption("Multi-agent research with fact-checking and human approval.")


def reset_workflow() -> None:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.needs_approval = False
    st.session_state.final_report = ""
    st.session_state.last_critique = ""


try:
    settings = load_settings()
except RuntimeError as exc:
    st.error(str(exc))
    st.info("Add the missing keys in Streamlit secrets or a local .env file.")
    st.stop()

if "thread_id" not in st.session_state:
    reset_workflow()
if "graph" not in st.session_state:
    st.session_state.graph = create_research_graph()

with st.sidebar:
    st.subheader("Runtime")
    st.write(f"Critic model: `{settings.critic_model}`")
    st.write(f"Writer model: `{settings.writer_model}`")
    st.write(f"Search results: `{settings.search_max_results}`")
    st.write(f"Max revisions: `{settings.max_revisions}`")
    if st.button("Reset session"):
        reset_workflow()
        st.rerun()

query = st.text_area(
    "Research task",
    placeholder="Analyze 2026 agentic AI trends for enterprise analytics teams.",
    height=110,
)

if st.button("Start research", type="primary", disabled=not query.strip()):
    reset_workflow()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    initial_state = {
        "task": query.strip(),
        "research_data": [],
        "revision_count": 0,
        "is_satisfactory": False,
        "content": "",
        "critique": "",
    }

    with st.status("Agents are researching and reviewing evidence...", expanded=True) as status:
        for output in st.session_state.graph.stream(initial_state, config=config):
            for node_name, value in output.items():
                st.write(f"{node_name.title()} finished.")
                if node_name == "critic":
                    st.session_state.last_critique = value.get("critique", "")
                    st.info(st.session_state.last_critique or "No critique returned.")

        status.update(label="Paused for human approval.", state="complete")
        st.session_state.needs_approval = True

if st.session_state.needs_approval:
    st.warning("Review the critic feedback before generating the final report.")
    approve_col, reject_col = st.columns(2)

    with approve_col:
        if st.button("Approve and generate", type="primary"):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            with st.spinner("Writer agent is drafting the report..."):
                for _ in st.session_state.graph.stream(None, config=config):
                    pass
                final_state = st.session_state.graph.get_state(config).values
                st.session_state.final_report = final_state.get("content", "")
                st.session_state.needs_approval = False

    with reject_col:
        if st.button("Reject and reset"):
            reset_workflow()
            st.rerun()

if st.session_state.final_report:
    st.success("Report generated.")
    st.markdown(st.session_state.final_report)
