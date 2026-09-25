from langchain.tools import tool
import requests
import os
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

tavily = TavilyClient(api_key=tavily_api_key)

@tool
def web_search(query: str) -> str:
    """ Perform a web search using Tavily for recent and reliable information on the given query. Returns titles, URL and snippets"""
    results = tavily.search(query, max_results=5)
    out = []
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")
    return "\n----\n".join(out)

#print(web_search.invoke("whats the recent news on war in iran"))

