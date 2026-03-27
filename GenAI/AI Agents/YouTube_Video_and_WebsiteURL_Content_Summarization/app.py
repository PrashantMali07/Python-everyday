import os
import streamlit as st
import validators
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader, WebBaseLoader

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Langchain: Summarize Text from YT or Website URL", page_icon="🦜", layout="wide")
st.title("Langchain: Summarize Text from YT or Website URL")
st.subheader('Summarize URL')

groq_key = os.getenv("GROQ_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

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
    
    # YouTube API Key Section
    st.subheader("YouTube API Key (Optional)")
    youtube_radio = st.radio(
        "YouTube API Key Option:",
        ("Use Environment Variable", "Enter Manually", "Skip (No Video Info)"),
        key="youtube_radio"
    )
    if youtube_radio == "Enter Manually":
        if not youtube_api_key:
            st.warning("⚠️ YOUTUBE_API_KEY not found in environment. Please enter your API Key.")
        youtube_api_key = st.text_input(
            "Enter your YouTube API Key:", 
            type="password",
            value=youtube_api_key or "",
            help="Get your key from https://console.cloud.google.com/ (enable YouTube Data API v3)"
        )
        if youtube_api_key:
            os.environ["YOUTUBE_API_KEY"] = youtube_api_key
            st.success("YouTube API Key set for this session!")
        else:
            st.warning("No YouTube API Key entered. Video info will be skipped.")
    elif youtube_radio == "Use Environment Variable":
        if youtube_api_key:
            st.write("YouTube API Key status: ✅ Loaded from environment")
        else:
            st.warning("YOUTUBE_API_KEY not found in environment. Video info will be skipped.")
    else:  # Skip
        st.write("YouTube API Key: Skipped - No video info will be fetched.")

## Initializing the LLM models
# Groq is incredibly fast, perfect for the first attempt, but we can have a fallback in case of rate limits or server errors
primary_llm = ChatGroq(model="qwen/qwen3-32b",api_key=groq_key,streaming=True)

# We point ChatOllama to the official cloud endpoint, which has a much higher rate limit and is more reliable for fallback purposes
fallback_llm = ChatOllama(model="gpt-oss:120b-cloud",streaming=True)

# This will catch Rate Limits (429), Server Errors (500), or timeouts on Groq
llm_with_fallback = primary_llm.with_fallbacks([fallback_llm])

# Determine if we can fetch YouTube video info
use_video_info = bool(os.getenv("YOUTUBE_API_KEY"))

# creating prompt template
prompt_template="""
Provide a summary of following content in 300 words:
Context:{text}
"""

prompt=PromptTemplate(template=prompt_template,input_variables=["text"])

# creating function to split the output
def strip_thinking(text: str) -> str:
    # This removes everything between <think> tags and the tags themselves
    if "</think>" in text:
        return text.split("</think>")[-1].strip()
    return text.strip()

generic_url=st.text_input("URL",label_visibility="collapsed")

if st.button("Summarize."):
    # validate inputs
    if not groq_key.strip() or not generic_url.strip():
        st.error("Please provide the necessary information to proceed.")
    elif not validators.url(generic_url):
        st.error("⚠️ Please enter a valid video URL.")
    else:
        try:
            with st.spinner("Getting responses..."):
                if "youtube.com" in generic_url:
                    loader=YoutubeLoader.from_youtube_url(generic_url,add_video_info=False)
                    # st.write(loader.load())
                else:
                    headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                "Accept-Language": "en-US,en;q=0.5",
                                "Accept-Encoding": "gzip, deflate",
                                "Connection": "keep-alive",
                                "Upgrade-Insecure-Requests": "1",
                            }
                    loader=UnstructuredURLLoader(urls=[generic_url],ssl_verify=True,
                                                 headers=headers)
                docs=loader.load()

                # initializing chain
                chain=load_summarize_chain(llm_with_fallback,chain_type="stuff",prompt=prompt)
                summarize_response=chain.run(docs)

                # displaying the output
                output=strip_thinking(summarize_response)
                st.success(output)
        except Exception as e:
            st.exception(f"Exception:{e}")