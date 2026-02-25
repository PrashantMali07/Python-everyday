##Loading environment variables and dependencies
import os
import streamlit as st
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

load_dotenv()

## Loading .env
os.environ['LANGCHAIN_API_KEY']=os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_TRACING_V2']="true"
os.environ['LANGCHAIN_PROJECT']=os.getenv("LANGCHAIN_PROJECT")

## Prompt Template
prompt=ChatPromptTemplate([
    ("system","You are a helpful assistant. Please respond to the questions asked."),
    ("user","Question:{question}")
])

## Initializing the Streamlit App
# Setting the page title
st.title("Ollama Demo Application with Lanchain & Llama Vision model.")

# Taking user input
input_text=st.text_input("What's in your mind?")

## Initializing Ollama LLM 
llm=OllamaLLM(model="llama3.2-vision:latest") ## We can also call Ollama cloud models

# Seting response parser
output_parser=StrOutputParser()

# Setting up the chain
chain=prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({"question":input_text}))