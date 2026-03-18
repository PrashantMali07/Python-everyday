import streamlit as st
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_classic.agents import initialize_agent, AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import time
from langchain_classic.agents import tool
from langchain_community.tools.arxiv.tool import ArxivQueryRun

import os
from dotenv import load_dotenv

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING_V2"] = "true"

load_dotenv()

## Calling Wikipedia Wrapper
wiki_wrapper = WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=250)
wiki=WikipediaQueryRun(api_wrapper=wiki_wrapper)

## Calling Arxiv Wrapper
arxiv_internal = ArxivQueryRun()

@tool
def polite_arxiv(query: str) -> str:
    """A tool to search Arxiv for scientific papers. 
    Use this for technical or academic research queries."""
    # Official Arxiv rule: 1 request every 3 seconds
    time.sleep(5) 
    return arxiv_internal.invoke(query)

arxiv_wrapper = ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=250)
arxiv=ArxivQueryRun(api_wrapper=arxiv_wrapper)

search=DuckDuckGoSearchRun(name="Search",description="useful for searching any information from the web")

st.title("Search Engine with LangChain Tools and Agents")

"""
In this app, we are using `StreamlitCallbackHandler` to display the thought & action of an agent in an interactive Streamlit App.
Try more LangChain & Streamlit Agent examples [here](github.com/langchain-ai/streamlit-agent)
"""

st.sidebar.title("Settings")

groq_key = os.getenv("GROQ_API_KEY")

# 2. If missing, create a Sidebar input
if not groq_key:
    with st.sidebar:
        st.warning("⚠️ GROQ_API_KEY not found in environment.")
        groq_key = st.text_input(
            "Enter your Groq API Key:", 
            type="password",
            help="You can find your key at https://console.groq.com/keys"
        )
        
        if groq_key:
            # Optionally set it for the current session
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("Key received for this session!")
        else:
            st.error("Please enter a valid API key to proceed.")
            st.stop() # Halts the rest of the app execution
else:
    # If the key is present, display a success message
    st.write("Current API Key status: ✅ Active")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role":"assistant","content":"Hi, I am your search assistant. I can search the web, Wikipedia, and Arxiv for you. How can I help you today?"}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Ask me anything about LangSmith or search the web!"):
    st.session_state["messages"].append({"role":"user","content":prompt})
    st.chat_message("user").write(prompt)

    ## Initializing the LLM models
    # Groq is incredibly fast, perfect for the first attempt, but we can have a fallback in case of rate limits or server errors
    primary_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",api_key=groq_key,streaming=True)

    # We point ChatOllama to the official cloud endpoint, which has a much higher rate limit and is more reliable for fallback purposes
    fallback_llm = ChatOllama(model="gpt-oss:120b-cloud",streaming=True)

    # This will catch Rate Limits (429), Server Errors (500), or timeouts on Groq
    llm_with_fallback = primary_llm.with_fallbacks([fallback_llm])
    tools=[search,wiki,polite_arxiv,arxiv]

    agent=initialize_agent(tools=tools,llm=llm_with_fallback,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,verbose=False,handle_parsing_errors=True)
    
    with st.spinner("Generating response..."):
        st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        response=agent.invoke({"input":st.session_state.messages},callbacks=[st_cb])
        if isinstance(response, dict):
            clean_output = response.get("output", str(response))
        else:
            clean_output = response
        st.session_state["messages"].append({"role":"assistant","content":clean_output})
        st.chat_message("assistant").write(clean_output)