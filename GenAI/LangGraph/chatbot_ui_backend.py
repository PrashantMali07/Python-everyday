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

import operator

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING_V2"] = "true"

## Initializing LLMs

# Using models known to work well with structured output
ollama_gpt = ChatOllama(model='gpt-oss:120b-cloud')
llama4_llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")
qwen_llm = ChatGroq(model="qwen/qwen3-32b")
google_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Creating a fallback LLM that tries multiple models in order until it gets a valid response
fallback_llm = ollama_gpt.with_fallbacks([llama4_llm,qwen_llm,google_llm])

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

def chat_node(state: ChatState) -> ChatState:
    # Get the last human message
    last_message = state['messages']
    
    # Generate a response using the fallback LLM
    response = fallback_llm.invoke(last_message)
    
    return {'messages': [response]}

check_pointer = InMemorySaver()
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=check_pointer)

response = chatbot.invoke({"messages":HumanMessage(content="Hello, How are you?")}, config={'configurable': {'thread_id': "thread_id_1"}})

print(chatbot.get_state(config={'configurable': {'thread_id': "thread_id_1"}}).values['messages'])