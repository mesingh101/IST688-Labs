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

## test the vector database
#test_search = "Data Science Overview"

#test_embedding_response = client.embeddings.create(
   # model="text-embedding-3-small",
   # input=test_search
#)

#test_embedding = test_embedding_response.data[0].embedding

#results = vector_db.query(
    #query_embeddings=[test_embedding],
   # n_results=3
#)

#st.write("Top 3 documents:")

#for i, metadata in enumerate(results["metadatas"][0], start=1):
   # st.write(f"{i}. {metadata['filename']}")

#^ commented out the test code to avoid cluttering the app with test results

# retrieve relevant course information from the vector database
def retrieve_course_info(question):

    question_embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    question_embedding = question_embedding_response.data[0].embedding

    results = vector_db.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    retrieved_text = "\n\n".join(results["documents"][0])

    return retrieved_text

# system prompt controls how the chatbot should respond
system_prompt = {
    "role": "system",
    "content": """
    You are a course information chatbot.

    Answer the user's question using the course information retrieved
    from the vector database.

    If the retrieved course information contains the answer, clearly
    state that your answer is based on information retrieved from the
    course documents.

    If the retrieved information does not contain enough information
    to answer the question, clearly say that the course documents
    do not provide enough information.

    Keep your answers clear and helpful.
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

    # retrieve course information related to the user's question
    retrieved_text = retrieve_course_info(prompt)

    # add the retrieved information to the user's question
    rag_prompt = f"""
    User question:
    {prompt}

    Retrieved course information:
    {retrieved_text}
    """

    
    with st.chat_message("user"):
        st.markdown(prompt)


    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # send the retrieved course information and question to the LLM
    messages_to_send = [
        system_prompt,
        {
            "role": "user",
            "content": rag_prompt
        }
    ]

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