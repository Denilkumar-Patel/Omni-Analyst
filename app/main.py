import os
import uuid
from dotenv import load_dotenv
from app.graph import create_research_graph

# Force reload to override any cached empty variables
load_dotenv(override=True) 

# Now import your LangChain modules...
from langchain_core.prompts import ChatPromptTemplate
# ...

def run_research_system(user_query: str):
    app = create_research_graph()
    
    initial_state = {
        "task": user_query,
        "research_data": [],
        "revision_count": 0,
        "is_satisfactory": False,
        "content": "",
        "critique": ""
    }

    # 1. Create a unique Thread ID for this session's memory
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- Starting Research for: {user_query} ---")
    print(f"--- Session ID: {thread_id} ---\n")
    
    # 2. Run the graph with the config. It will pause before the 'writer' node.
    print("Executing Research & Critique loop...\n")
    for output in app.stream(initial_state, config=config):
        for key, value in output.items():
            print(f"Finished node: {key}")
            if key == "critic":
                print(f" -> Critique: {value.get('critique', '')}")
                print(f" -> Satisfactory: {value.get('is_satisfactory', False)}\n")

    # 3. Check the graph's current state to see if it hit our interrupt
    snapshot = app.get_state(config)
    
    # If the next node in line is 'writer', that means it paused for human approval
    if snapshot.next and snapshot.next[0] == "writer":
        print("\n" + "="*50)
        print("⏸️ HUMAN IN THE LOOP: Graph Paused Before Writer")
        print("="*50 + "\n")
        
        user_approval = input("Do you approve the critic's review and want to generate the final report? (y/n): ")
        
        if user_approval.lower() == 'y':
            print("\nResuming workflow to Writer...\n")
            
            # Pass 'None' to resume from where it paused, using the same config/memory
            for output in app.stream(None, config=config):
                for key, value in output.items():
                    print(f"Finished node: {key}")
            
            # 4. Fetch the final state from memory
            final_state = app.get_state(config).values
            print("\n" + "="*50)
            print("FINAL REPORT")
            print("="*50 + "\n")
            print(final_state.get("content", ""))
        else:
            print("\nWorkflow aborted by user.")

if __name__ == "__main__":
    query = "Analyze the latest trends in Agentic AI for enterprise systems."
    run_research_system