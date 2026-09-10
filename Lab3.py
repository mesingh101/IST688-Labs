import streamlit as st
from openai import OpenAI

st.title("Lab 3 - Streaming Chatbot with Memory")

# creating openai client and storing it in session state to avoid re-creating it on every rerun
if "client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

client = st.session_state.client

#system prompt controls how the chatbot should respond
system_prompt = {
    "role": "system",
    "content": """
    You are a helpful chatbot.
    Explain all answers so that a 10-year-old can understand them.

    When the user asks a question:
    1. Answer the question.
    2. End by asking exactly: "Do you want more info?"

    If the user says yes:
    - Give more information about the previous topic.
    - End by asking exactly: "Do you want more info?"

    If the user says no:
    - Do not give more information about the previous topic.
    - Ask: "What can I help you with?"
    """
}

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

#keep the last two user messages and their assistant responses
conversation_buffer = st.session_state.messages[-3:]

#always include the system prompt with the conversation buffer
messages_to_send = [system_prompt] + conversation_buffer

stream = client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages_to_send,
    stream=True
)

with st.chat_message("assistant"):
    response = st.write_stream(stream)

st.session_state.messages.append(
     {"role": "assistant", "content": response}
    )
