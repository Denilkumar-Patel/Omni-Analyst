import argparse
import uuid

from dotenv import load_dotenv

from app.config import load_settings
from app.graph import create_research_graph


load_dotenv(override=True)


def run_research_system(user_query: str, auto_approve: bool = False) -> str:
    load_settings()
    graph = create_research_graph()

    initial_state = {
        "task": user_query,
        "research_data": [],
        "revision_count": 0,
        "is_satisfactory": False,
        "content": "",
        "critique": "",
    }

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Starting research for: {user_query}")
    print(f"Session ID: {thread_id}\n")

    for output in graph.stream(initial_state, config=config):
        for key, value in output.items():
            print(f"Finished node: {key}")
            if key == "critic":
                print(f"Critique: {value.get('critique', '')}")
                print(f"Satisfactory: {value.get('is_satisfactory', False)}\n")

    snapshot = graph.get_state(config)
    if snapshot.next and snapshot.next[0] == "writer":
        approved = auto_approve
        if not auto_approve:
            response = input("Generate the final report? (y/n): ").strip().lower()
            approved = response in {"y", "yes"}

        if not approved:
            print("Workflow aborted before report generation.")
            return ""

        for output in graph.stream(None, config=config):
            for key in output:
                print(f"Finished node: {key}")

    final_state = graph.get_state(config).values
    report = final_state.get("content", "")
    print("\nFINAL REPORT\n")
    print(report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Omni-Analyst from the CLI.")
    parser.add_argument("query", nargs="?", help="Research task to run.")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip the human approval prompt and generate the report.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    query = args.query or "Analyze the latest trends in Agentic AI for enterprise systems."
    run_research_system(query, auto_approve=args.auto_approve)
