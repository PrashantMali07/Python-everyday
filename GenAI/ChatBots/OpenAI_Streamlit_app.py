import os
import streamlit as st
import openai
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
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

def generate_response(question,api_key,llm,temperature,max_tokens):
    openai.api_key = api_key
    # Initialize the ChatOpenAI model
    model = ChatOpenAI(model=llm)
    
    # Format the prompt with the user's question
    output_parser = StrOutputParser()
    
    # Creating a Chain
    chain= prompt | model | output_parser
    # Generate a response using the model
    response=chain.invoke({'question': question})
    
    return response

st.title("Q&A Chatbot with OpenAI")
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
llm=st.sidebar.selectbox("Select LLM", ["gpt-5", "gpt-5-mini","gpt-5-chat-latest","gpt-4o-mini"])

max_tokens=st.sidebar.slider("Max Tokens",min_value=50,max_value=200,value=100)
temperature=st.sidebar.slider("Temperature",min_value=0.0,max_value=1.0,value=0.7)

st.write("What's in you mind? Ask me anything!")
user_input=st.text_input("Your Question:")

if user_input and api_key:
    with st.spinner("Generating response..."):
        response = generate_response(user_input,api_key,llm,temperature,max_tokens)
    st.write("**Answer:**")
    st.write(response)
elif not api_key:
    st.write("Ahhhh! You forgot to enter your OpenAI API Key. Please enter it in the sidebar to get a response.")
else:
    st.write("Please ask a question to get a response.")