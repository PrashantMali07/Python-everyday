import streamlit as st
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

llm = ChatNVIDIA(
  model="openai/gpt-oss-20b",
  api_key=api_key
)

def vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = NVIDIAEmbeddings(api_key=api_key)
        st.session_state.loader=PyPDFDirectoryLoader("/home/prashant/Documents/gen-ai/GettingStarted_With_Nvidia_NIMs/us_census")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=700,chunk_overlap=50)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:30])
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

st.title("Getting Started with NVIDIA NIMs and LangChain")

# Initializing Prompt Template
prompt=ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    please provide the most accurate response based on the question and the context. 
    If you don't know the answer, say you don't know.
    <context>
    {context}
    </context>
    Question: {input}
    """)

user_input=st.text_input("Ask a question about the US Census data:", key="input")

if st.button("Generate Embeddings"):
    vector_embeddings()
    st.success("Embeddings generated using NVIDIA embeddings and vector store created successfully!")


if user_input and "vectors" in st.session_state:
    with st.spinner("Generating response..."):
        retriever = st.session_state.vectors.as_retriever(search_kwargs={"k": 4})
        doc_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        qa_chain = create_retrieval_chain(retriever,doc_chain)
        response = qa_chain.invoke({"input": user_input})
        st.write(response)