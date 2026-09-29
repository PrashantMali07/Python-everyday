import json
import requests
import operator
import os
from bs4 import BeautifulSoup
from typing import Literal
from langchain_classic.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun,tool

from dotenv import load_dotenv
load_dotenv()

@tool
def calculator(num1: float, num2: float, operation: Literal['add', 'subtract', 'multiply', 'divide']) -> float:
    """Calculate different operations on two numbers."""
    if operation == 'add':
        return operator.add(num1, num2)
    elif operation == 'subtract':
        return operator.sub(num1, num2)
    elif operation == 'multiply':
        return operator.mul(num1, num2)
    elif operation == 'divide':
        if num2 == 0:
            raise ValueError("Cannot divide by zero")
        return operator.truediv(num1, num2)

@tool
def get_stock_price(symbol: str)->dict:
    """
    fetch the latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')
    using Alpha vantage using the URL with API key.
    """
    import requests
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    if "Global Quote" in data:
        return {"symbol": symbol, 
                "today_price": data["Global Quote"]["05. price"],
                "last_price": data["Global Quote"]['02. open'],
                "change": data["Global Quote"]['09. change'],
                "change_percent": data["Global Quote"]['10. change percent']}
    else:
        raise ValueError(f"Could not fetch stock price for symbol: {symbol}")

@tool
def get_url_content(url: str) -> str:
    """
    CRITICAL: Use this tool ONLY when the user provides an exact website URL link 
    (starting with http:// or https://) and asks to extract information directly from it.
    
    DO NOT use Wikipedia or DuckDuckGo if a specific direct URL is provided. 
    Input must be a single, valid, raw URL string.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: Webpage returned status code {response.status_code}"
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # --- FIXING THE HTML SNIPPET ISSUE ---
        # If it's Google Scholar, extract just the authors so we don't dump raw HTML to the LLM
        if "scholar.google" in url:
            for field in soup.find_all("div", class_="gsc_oci_field"):
                if "Authors" in field.get_text():
                    value_div = field.find_next_sibling("div", class_="gsc_oci_value")
                    if value_div:
                        return f"Data successfully extracted from URL. Authors: {value_div.get_text(strip=True)}"
            return "Connected to Google Scholar, but could not find the Authors block."
            
        # For any other general website, strip out the HTML tags and return pure text
        # This stops the LLM from getting drowned in `<!DOCTYPE html>` codes
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose() 
        return f"Webpage content text: {soup.get_text()[:2000]}" # Limit characters to save tokens
        
    except Exception as e:
        return f"An error occurred while fetching the URL: {str(e)}"

wikipedia_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=250)    
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia_wrapper)

arxiv_wrapper = ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=250)
arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)

web_search_tool = DuckDuckGoSearchRun(region="us-en", top_k_results=3, doc_content_chars_max=250)

Tools = [calculator, get_stock_price, get_url_content, wikipedia_tool, arxiv_tool, web_search_tool]