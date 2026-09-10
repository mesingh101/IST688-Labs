import streamlit as st
from openai import OpenAI

st.title("Lab 3 - Streaming Chatbot with Memory")

# creating openai client and storing it in session state to avoid re-creating it on every rerun
if "client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

client = st.session_state.client

#initialize session state for messages if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []

#display previous messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#get user input and store it in session state
if prompt := st.chat_input("What can I help you with?"):

    
    with st.chat_message("user"):
        st.markdown(prompt)


    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
        
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
