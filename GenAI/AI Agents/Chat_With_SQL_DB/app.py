import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_classic.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from sqlalchemy import create_engine
import sqlite3
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT_NAME"] = "Chat with SQL Database"

st.set_page_config(page_title="Chat with SQL Database", page_icon="🦜", layout="wide")
st.title("🦜LangChain: Chat with SQL Database")

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

# Sidebar title
st.sidebar.title("Settings")

## Creating radio buttons
radio_opt=["Use Sqlite3 Database - Student.db","Connect to MySQL Database"]

selected_opt=st.sidebar.radio("Select the Database to connect with:",options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    st.sidebar.write("You have selected to connect with MySQL Database. Please provide the following details:")
    host=st.sidebar.text_input("Host",value="localhost")
    port=st.sidebar.text_input("Port",value="3306")
    user=st.sidebar.text_input("User",value="root")
    password=st.sidebar.text_input("Password",type="password")
    database=st.sidebar.text_input("Database Name",value="testdb")
else:
    db_uri=LOCALDB
    st.sidebar.write("You have selected to use the local SQLite database (student.db).")

if not db_uri:
    st.warning("Please select a database option from the sidebar to proceed.")

## Setting up the LLM/AI model
llm=ChatOllama(model="qwen3-vl:235b-instruct-cloud",streaming=True)

def configure_db(db_uri,host=None,port=None,user=None,password=None,database=None):
    if db_uri==LOCALDB:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir,"students.db")
        st.write(f"Using local SQLite database at: {db_path}")
        
        if not os.path.exists(db_path):
            sqlite3.connect(db_path).close()
        
        engine = create_engine(f"sqlite:///{db_path}")
        # creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        return SQLDatabase(engine)
    elif db_uri==MYSQL:
        if not (host and port and user and password and database):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")) 
    
if db_uri==MYSQL:
    db=configure_db(db_uri,host,port,user,password,database)
else:
    db=configure_db(db_uri)

## toolkit
toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools",
    handle_parsing_errors=True,
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.spinner("Generating response..."):
        st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        response=agent.invoke(user_query,callbacks=[st_cb])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)