import os
import time
from dotenv import load_dotenv
import streamlit as st

from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

# Loading environment variable
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]="Q&A Chatbot with Groq"

# Initalizing the Groq model
llm=ChatGroq(model="qwen/qwen3-32b")

# Initializing Prompt Template
prompt=ChatPromptTemplate.from_messages([
        ("system",
    """
    Answer the questions based on the provided context only.
    please provide the most accurate response based on the question and the context. 
    If you don't know the answer, say you don't know.
    <context>
    {context}
    </context>
    Question: {input}
    """,
        )
])

# defining a function to generate vector store from the documents
def generate_vector_store():
    if "vectors" not in st.session_state:
        # Initializing the Ollama Embeddings
        st.session_state.embedding = OllamaEmbeddings(model="qwen3-embedding:0.6b")
        # Data ingestion step
        st.session_state.loader = PyPDFDirectoryLoader("/home/prashant/Documents/gen-ai/ChatBots/RAG+Documents+Q&A/research_papers")
        # Loading and reading the documents
        st.session_state.docs = st.session_state.loader.load()
        # Text splitting step
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # reading first 50 documents to avoid memory issues. You can increase this number based on your system's capacity.
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
        # Generating vector store from the documents
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embedding)

st.title("Document based Chatbot with Groq")
user_prompt=st.text_input("Ask a question related to the documents:")

if st.button("Generate Embeddings and Vector Store"):
    with st.spinner("Processing documents and generating vector store..."):
        generate_vector_store()
    st.success("Vector store generated successfully!")

if user_prompt:
    if "vectors" in st.session_state:
        with st.spinner("Generating response..."):
            # creating a document chain
            document_chain=create_stuff_documents_chain(llm,prompt)
            # creating a retrieval chain
            retriver=st.session_state.vectors.as_retriever()
            retrieval_chain = create_retrieval_chain(retriver, document_chain)
            # generating response using the retrieval chain
            start=time.process_time()
            response = retrieval_chain.invoke({'input': user_prompt})
            print("Time taken to generate response: ", time.process_time()-start)
        st.write("**Answer:**")
        st.write(response['answer'])
    else:
        st.write("Please generate the vector store first by clicking the button above.")  

    with st.expander("Document Similarity Search"):
        for i, doc in enumerate(response['context']):
            st.write(f"**Document {i+1}:**")
            st.write(doc.page_content)
            st.write("---")