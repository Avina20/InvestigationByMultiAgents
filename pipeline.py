from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

"""Supervisor pipeline"""

def run_research_pipeline(topic: str, on_step=None) -> dict:
    """Calls all 4 agents and chains and passes information between them using a shared state dictionary. Agents use message based input/output.

    on_step(step, status, output) is an optional callback, called with status "start" before each step and "done" after it (used by the Streamlit UI).
    """
    state = {}
    notify = on_step or (lambda *args: None)

    # Step 1: Search Agent
    print("Running Search Agent...")
    notify("search", "start", None)
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state['search_result'] = search_result["messages"][-1].text
    print("\n Search result: ", state['search_result'])
    notify("search", "done", state['search_result'])

    # Step 2: Reader Agent
    print("\nRunning Reader Agent...")
    notify("reader", "start", None)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result["messages"][-1].text
    print("\n Scraped content: ", state['scraped_content'])
    notify("reader", "done", state['scraped_content'])

    # Step 3: Writer Chain
    print("\nWriter Chain Drafting the Research Report...")
    notify("writer", "start", None)

    research_combined = f"Search Results:\n{state['search_result']}\n\nScraped Content:\n{state['scraped_content']}"

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Research Report: ", state['report'])
    notify("writer", "done", state['report'])

    # Step 4: Critic Chain
    print("\nCritic Chain Reviewing the Research Report...")
    notify("critic", "start", None)

    state["critique"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\n Critic Report: ", state['critique'])
    notify("critic", "done", state['critique'])

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    run_research_pipeline(topic)
