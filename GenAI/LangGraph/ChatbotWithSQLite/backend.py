import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_classic.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.messages import BaseMessage, HumanMessage

from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

import operator
import sqlite3

## Calling the Tools from the tools.py file
from tools import calculator, get_stock_price, get_url_content, wikipedia_tool, arxiv_tool, web_search_tool

## importing ToolNode from LangGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING_V2"] = "true"

## -----------------> Initializing LLMs

## -----------------> Using models known to work well with structured output
ollama_gpt = ChatOllama(model='gpt-oss:120b-cloud')
llama4_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
qwen_llm = ChatGroq(model="qwen/qwen3-32b")
google_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

## -----------------> Creating a fallback LLM that tries multiple models in order until it gets a valid response
fallback_llm = ollama_gpt.with_fallbacks([llama4_llm,qwen_llm,google_llm])

## Calling and Binding the tools to the fallback LLM so that it can use them when generating responses
Tools=[calculator, get_stock_price, get_url_content, wikipedia_tool, arxiv_tool, web_search_tool]
tools_llm = fallback_llm.bind_tools(Tools)

## -----------------> Define the graph node and state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

def chat_node(state: ChatState) -> ChatState:
    # Get the last human message
    last_message = state['messages']
    
    # Generate a response using the fallback LLM
    response = tools_llm.invoke(last_message)
    
    return {'messages': [response]}

# creating a connection to the SQLite database and initializing the SqliteSaver with that connection.
# This will allow us to save the chatbot's conversation history to the SQLite database.
conn = sqlite3.connect(database='/home/prashant/Documents/gen-ai/LangGraph/ChatbotWithSQLite/chatbot_history.db', check_same_thread=False)

# Checkpointer for saving the state of the chatbot's conversation history to a SQLite database
check_pointer = SqliteSaver(conn=conn)

## Tool node
tool_node = ToolNode(Tools)

## -----------------> Building the graph
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node) 
graph.add_node('tools', tool_node)

graph.add_edge(START, 'chat_node') 
graph.add_conditional_edges('chat_node', tools_condition) 
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=check_pointer)


## ------------------> Helper function to retrieve conversation history for a given thread_id
def retrieve_thread_ids():
    all_threads = set()

    for item in check_pointer.list(None):
        all_threads.add(item.config['configurable']['thread_id'])

    return list(all_threads)