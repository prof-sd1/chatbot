import streamlit as st
import openai
from io import BytesIO
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import numpy as np
import re

# ----------------------------------
# Configure your OpenAI API Key
# ----------------------------------
openai.api_key = "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"

st.set_page_config(page_title="LegalEase AI Assistant", layout="wide")
st.title("📘 LegalEase AI Assistant")
st.caption("Summarize legal documents • Chat about laws • Extract from PDFs, Word, and Images")

# -----------------------------
# Sidebar - File Upload
# -----------------------------
st.sidebar.header("📂 Upload a Legal Document")
uploaded_file = st.sidebar.file_uploader("Choose a PDF, Word, or Image file", type=["pdf", "docx", "png", "jpg", "jpeg"])

# -----------------------------
# Text Extractors
# -----------------------------
def extract_text_from_pdf(file_bytes):
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_image(image):
    img = Image.open(image)
    return pytesseract.image_to_string(img)

# -----------------------------
# ChatBot using OpenAI API
# -----------------------------
def chat_with_openai(prompt, chat_history):
def chat_with_openai(prompt, chat_history):
    messages = [{"role": "system", "content": "You are a helpful legal assistant."}]
    for q, a in chat_history:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": prompt})

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
# -----------------------------
# Main File Handling
# -----------------------------
extracted_text = ""

if uploaded_file:
    file_type = uploaded_file.type
    if file_type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file.read())
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted_text = extract_text_from_docx(uploaded_file)
    elif "image" in file_type:
        extracted_text = extract_text_from_image(uploaded_file)
    else:
        st.warning("Unsupported file type.")

    if extracted_text:
        st.subheader("📄 Extracted Text")
        st.text_area("Text Content", extracted_text, height=300)

# -----------------------------
# Chatbot Interface
# -----------------------------
st.subheader("💬 Chat with LegalEase AI")
if extracted_text:
    st.info("Ask a question based on the uploaded document or about legal topics.")

chat_history = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Type your question here:")

if st.button("Ask"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            combined_prompt = user_input + "\n\nContext:\n" + extracted_text if extracted_text else user_input
            answer = chat_with_openai(combined_prompt, st.session_state.chat_history)
            st.session_state.chat_history.append((user_input, answer))

# Display Chat
if st.session_state.chat_history:
    for i, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 LegalEase:** {a}")
        st.markdown("---")
