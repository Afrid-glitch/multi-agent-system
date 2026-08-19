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

@tool
def scrape_url(url: str) -> str:
    """
    Scrape the content of a webpage given its URL. Return the text content of the page for deeper reading.
    """
    try:
        resp = requests.get(url, timeout=8 , headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style','nav', 'footer']):
            tag.decompose()
        return soup.get_text(separator='\n', strip=True)[:3000]  # Limit to first 3000 characters
    except Exception as e:
        return f"could not scrape the URL: {str(e)}"