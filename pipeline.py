from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

"""Supervisor pipeline"""

def run_research_pipeline(topic: str) -> dict:
    """Calls all 4 agents and chains and passes information between them using a shared state dictionary. Agents use message based input/output."""
    state = {}

    # Step 1: Search Agent
    print("Running Search Agent...")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state['search_result'] = search_result["messages"][-1].content
    print("\n Search result: ", state['search_result'])

    # Step 2: Reader Agent
    print("\nRunning Reader Agent...")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result["messages"][-1].content
    print()("\n Scraped content: ", state['scraped_content'])

    # Step 3: Writer Chain
    print("\nWriter Chain Drafting the Research Report...")

    research_combined = f"Search Results:\n{state['search_result']}\n\nScraped Content:\n{state['scraped_content']}"

    state["report"] =writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Research Report: ", state['report'])

    # Step 4: Critic Chain
    print("\nCritic Chain Reviewing the Research Report...")

    state["critique"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\n Critic Report: ", state['critique'])

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    run_research_pipeline(topic)



    