import streamlit as st
from openai import OpenAI
import chromadb
import fitz
import os

st.title("Lab 4 - RAG Course Information Chatbot")

# creating openai client and storing it in session state to avoid re-creating it on every rerun
if "client" not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

client = st.session_state.client

# create the vector database using the course PDF files
def create_vector_db():
    chroma_client = chromadb.Client()

    collection = chroma_client.create_collection(
        name="Lab4Collection"
    )

    # naming folder containing the 7 course PDF files
    pdf_folder = "Lab-04-Data"

    # going through each file in the folder
    for filename in os.listdir(pdf_folder):

        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)

            # open the PDF and extract its text
            pdf = fitz.open(file_path)
            text = ""

            for page in pdf:
                text += page.get_text()

            pdf.close()

            # create an embedding for the PDF text
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embedding = embedding_response.data[0].embedding

            # add the PDF to the ChromaDB collection
            collection.add(
                ids=[filename],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{"filename": filename}]
            )

    return collection

# only create the vector database once
if "Lab4_VectorDB" not in st.session_state:
    st.session_state.Lab4_VectorDB = create_vector_db()

vector_db = st.session_state.Lab4_VectorDB

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
