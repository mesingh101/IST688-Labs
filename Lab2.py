import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Lab 2 - Document Summarizer")
summary_type = st.sidebar.selectbox(
    "Choose summary type",
    [
        "100 words",
        "2 connecting paragraphs",
        "5 bullet points"
    ]
)

use_advanced_model = st.sidebar.checkbox("Use advanced model")
st.write(
    "Upload a PDF document below and GPT will summarize it "
    "based on the summary type you select."
)

if use_advanced_model:
    model = "gpt-5-mini"
else:
    model = "gpt-5-nano"
    
# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
# Get OpenAI API key from Streamlit secrets.
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Validate OpenAI API key.
try:
    client.models.list()
    st.success("API key is valid")
except Exception as e:
    st.error(f"API key is invalid: {e}")
    st.stop()

# Let the user upload a PDF file.
uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type="pdf"
)

if uploaded_file:
    from pypdf import PdfReader

    reader = PdfReader(uploaded_file)

    document = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            document += text + "\n"

    instructions = f"""
    Summarize the following document as {summary_type}.

    Document:
    {document}
    """

    messages = [
        {
            "role": "user",
            "content": instructions
        }
    ]

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )

    st.write_stream(stream)