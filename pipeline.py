from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dict:

    state ={}

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"find recent, reliable and detailed information about : {topic}")]
    })
    state["search_result"] = search_result["messages"][-1].content

    print("\n Search Result", state["search_result"])



    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages" : [("user", f"Based on the following search results about '{topic}', "
                       f"pick the most relavent URL and scrape it for deeper sontent\n\n"
                       f"Search Results:\n{state['search_result'][:800]}"
                       )]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\n Scraped Content", state["scraped_content"])

    research_combined =(
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
        })
    
    print("\n Research Report", state["report"])

    # Critic report

    state["feedback"] = critic_chain.invoke({
        "report" : state["report"]
    })

    print("\n Critic report \n", state["feedback"])

    return state

if __name__ == "__main__":
    topic = input("\n Enter the research topic: ")
    run_research_pipeline(topic)



