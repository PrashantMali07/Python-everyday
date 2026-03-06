import os
import streamlit as st
import openai
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="Q&A Chatbot with OpenAI"

# Initializing Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries."),
        ("user","Question:{question}")
    ]
)

def generate_response(question,llm,temperature,max_tokens):
    # Initialize the ChatOpenAI model
    model = ChatOllama(model=llm)
    
    # Format the prompt with the user's question
    output_parser = StrOutputParser()
    
    # Creating a Chain
    chain= prompt | model | output_parser
    # Generate a response using the model
    response=chain.invoke({'question': question})
    
    return response

st.title("Q&A Chatbot with Ollama")
st.sidebar.title("Settings")
llm=st.sidebar.selectbox("Select available models:", ["gpt-oss:20b", "qwen3-coder:480b-cloud","gpt-oss:120b-cloud","llama3.2-vision:latest"])

max_tokens=st.sidebar.slider("Max Tokens",min_value=50,max_value=200,value=100)
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)

st.write("What's in you mind? Ask me anything!")
user_input=st.text_input("Your Question:")

if user_input:
    with st.spinner("Generating response..."):
        response = generate_response(user_input,llm,temperature,max_tokens)
    st.write("**Answer:**")
    st.write(response)
else:
    st.write("Please ask a question to get a response.")