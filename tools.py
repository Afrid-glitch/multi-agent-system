from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from rich import print
load_dotenv()

Tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a topic . Return Titles , URLs and snippets.
    """
    results = Tavily.search(query = query, max_results=2)

    out = []

    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'] [:300]}\n")

    return "\n----\n".join(out)

print(web_search.invoke("latest news on AI technology"))