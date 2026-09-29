import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from backend import chatbot, retrieve_thread_ids
import uuid

def generate_thread_id():
    return str(uuid.uuid4())

def add_threads(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_threads(st.session_state['thread_id'])
    st.session_state["messages"] = []

def load_conversation(thread_id):
    try:
        snapshot = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        return snapshot.values.get("messages", [])
    except Exception:
        return []

# Page title
# st.title("Chatbot with LangGraph - Resume Support")

# --------------------------------- Main chat interface ----------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_thread_ids()

add_threads(st.session_state["thread_id"])

# ----------------- Sidebar for chat controls and recent chats -----------------
st.sidebar.title("Chatbot Controls") # Add title

if st.sidebar.button("New Chat"): # Add New chat button
    reset_chat()

st.sidebar.header("Recent Chats") # Add section and header for recent chats

for thread_id in st.session_state["chat_threads"]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"] = thread_id # Display thread IDs as a placeholder for recent chats
        msg = load_conversation(thread_id)
        temp_msg = []

        for message in msg:

            if isinstance(message, HumanMessage):
                role = "user"
            else:
                role = "assistant"

            temp_msg.append({"role":role, "content": message.content})

        st.session_state['messages'] = temp_msg

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Thread config
CONFIG = {'configurable': {'thread_id': st.session_state["thread_id"]}}

# User input
user_input = st.chat_input("Type here...")

# Chatbot response handling with streaming
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        def parsed_stream_message():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode = 'messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield the content of the message chunk to be displayed in the Streamlit app
                    yield message_chunk.content
        ai_messages = st.write_stream(parsed_stream_message())

    st.session_state["messages"].append({"role": "assistant", "content": ai_messages})