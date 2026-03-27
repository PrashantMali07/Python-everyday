import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains import LLMChain, LLMMathChain
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_classic.agents import initialize_agent, AgentType, Tool
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_community.utilities import WikipediaAPIWrapper

## Setting up environment variables
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]=os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT_NAME"]=os.getenv("LANGCHAIN_PROJECT_NAME")
load_dotenv()

# Streamlit page configuration
st.set_page_config(page_title="Langchain: Text to Maths Problem solver.", page_icon="🦜", layout="wide")
st.title("Langchain: Text to Maths Problem solver.")
st.subheader('Get step by step solutions for your mathematical problems.')

groq_key = os.getenv("GROQ_API_KEY")

with st.sidebar:
    st.title("API Key Setting.")
    
    # Groq API Key Section
    st.subheader("Groq API Key")
    groq_radio = st.radio(
        "Groq API Key Option:",
        ("Use Environment Variable", "Enter Manually"),
        key="groq_radio"
    )
    if groq_radio == "Enter Manually":
        if not groq_key:
            st.warning("⚠️ GROQ_API_KEY not found in environment. Please enter your API Key.")
        groq_key = st.text_input(
            "Enter your Groq API Key:", 
            type="password",
            value=groq_key or "",
            help="You can find your key at https://console.groq.com/keys"
        )
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("Groq API Key set for this session!")
        else:
            st.error("Please enter a valid Groq API key to proceed.")
            st.stop()
    else:
        if groq_key:
            st.write("Groq API Key status: ✅ Loaded from environment")
        else:
            st.error("GROQ_API_KEY not found in environment. Switch to 'Enter Manually'.")
            st.stop()

## Initializing the LLM models
# Groq is incredibly fast, perfect for the first attempt, but we can have a fallback in case of rate limits or server errors
primary_llm = ChatOllama(model="gemma3:27b-cloud",streaming=True)

# We point ChatOllama to the official cloud endpoint, which has a much higher rate limit and is more reliable for fallback purposes
fallback_llm = ChatGroq(model="qwen/qwen3-32b",api_key=groq_key,streaming=True)

# This will catch Rate Limits (429), Server Errors (500), or timeouts on Groq
llm_with_fallback = primary_llm.with_fallbacks([fallback_llm])

## initializing the tool - #1 Wikipedia Search Tool
wikipedia_wrapper=WikipediaAPIWrapper()
wikipedia_tool=Tool(
    name="Wikipedia",
    func=wikipedia_wrapper.run,
    description="A tool for searching the Internet with various information on the topics asked by the user."
)

## Initializing the Tool - #2 Maths Solver 
maths_chain=LLMMathChain.from_llm(llm=llm_with_fallback)
calculator=Tool(
    name="Calculator",
    func=maths_chain.run,
    description="A tool for solving mathematical problems. It can be used to perform calculations, solve equations, and answer questions related to mathematics."
)

## Initializing the Agent Prompt
prompt_template=""""
You are an agent tasked for solving users mathematical problems. Logically arrive at the solution and provide detailed explanations in several pointers for the question below.
If you need to use a calculator, use the Calculator tool. If you need to search for information, use the Wikipedia tool. 
Always think step by step and provide detailed explanations for your reasoning.
Question: {question}
Answer:
"""

prompt=PromptTemplate.from_template(input_variable=["question"],template=prompt_template)

# Creating the Chain
chain=LLMChain(llm=llm_with_fallback,prompt=prompt,verbose=False)

## 3. Creating Reasoning Tool
reasoning_tool=Tool(
    name="Reasoning Agent",
    func=chain.run,
    description="A tool for answering logic-based & reasoning mathematical problems with step by step reasoning. It can be used to solve complex problems which require multiple steps of reasoning and calculations."
)

## Initializing the Agent by combining the tools
agent=initialize_agent(
    tools=[wikipedia_tool,calculator,reasoning_tool],
    llm=llm_with_fallback,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True
)

# creating function to split the output
def strip_thinking(text: str) -> str:
    # This removes everything between <think> tags and the tags themselves
    if "</think>" in text:
        return text.split("</think>")[-1].strip()
    return text.strip()

def strip_thinking_process(llm_output):
    # If the output is a string, strip the tags
    if isinstance(llm_output, str):
        return re.sub(r'<think>.*?</think>', '', llm_output, flags=re.DOTALL).strip()
    # If it's a message object (standard for ChatModels)
    if hasattr(llm_output, "content"):
        llm_output.content = re.sub(r'<think>.*?</think>', '', llm_output.content, flags=re.DOTALL).strip()
    return llm_output

if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role": "assistant", "content":"Hi, I am your Maths Problem Solver Agent. I can help you solve mathematical problems step by step."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask any Mathematical problem here...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.spinner("Generating response..."):
        st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        response=agent.invoke(user_query,callbacks=[st_cb])
        clean_response=strip_thinking_process(response)
        st.session_state.messages.append({"role": "assistant", "content": clean_response})
        st.write(clean_response)