import streamlit as st
from langchain_core.messages import HumanMessage
from chatbot_ui_backend import chatbot

st.title("Chatbot with LangGraph")

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type here...")


if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        ai_messages = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode = 'messages'
            )
        )
    st.session_state["messages"].append({"role": "assistant", "content": ai_messages})