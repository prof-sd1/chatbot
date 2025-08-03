import streamlit as st
import openai
from io import BytesIO
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
import pytesseract
import re

# Set page config
st.set_page_config(page_title="LegalEase AI Assistant", layout="wide")

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Helper: Extract text from PDF
def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Helper: Extract text from DOCX
def extract_text_from_docx(file_bytes):
    doc = Document(file_bytes)
    return "\n".join([para.text for para in doc.paragraphs])

# Helper: OCR image
def extract_text_from_image(image_file):
    image = Image.open(image_file)
    return pytesseract.image_to_string(image)

# Legal Agreement Template Generator
def generate_agreement(company_name, client_name, service_description):
    return f"""
    SOFTWARE SERVICE AGREEMENT

    This Software Service Agreement (“Agreement”) is entered into between {company_name}, 
    and {client_name}.

    Services Provided:
    {service_description}

    Terms & Conditions:
    1. Service will be provided as per SLA.
    2. The client shall pay fees agreed upon.
    3. Both parties agree to confidentiality.

    Signed,
    {company_name} | {client_name}
    """

# Title
st.title("🧑‍⚖️ LegalEase AI Assistant")
st.caption("📑 Legal document parser, agreement generator, and AI legal chatbot")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Chatbot", "📂 Document Parser", "📄 Agreement Generator", "📥 About"])

# -------------------------
# Tab 1: OpenAI Chatbot
# -------------------------
with tab1:
    st.header("🤖 LegalEase Chatbot (OpenAI-powered)")
    st.markdown("Ask me anything legal: contracts, clauses, regulations...")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_query := st.chat_input("Ask a legal question..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Drafting a response..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are LegalEase AI, a professional legal assistant. You help users with contracts, legal advice, terms, and summaries."},
                        *st.session_state.chat_history
                    ],
                    temperature=0.3,
                    max_tokens=700,
                )
                bot_reply = response.choices[0].message["content"]
            except Exception as e:
                bot_reply = f"❌ Error: {e}"

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

    if st.session_state.chat_history:
        chat_txt = "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.chat_history])
        st.download_button("📥 Download Chat", data=chat_txt, file_name="legal_chat.txt")

# -------------------------
# Tab 2: Document Parser
# -------------------------
with tab2:
    st.header("📂 Legal Document Parser")
    st.markdown("Upload PDF, DOCX, or Image to extract legal text.")

    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "png", "jpg", "jpeg"])
    if uploaded_file:
        file_type = uploaded_file.type
        file_bytes = uploaded_file.read()

        with st.spinner("Extracting text..."):
            if "pdf" in file_type:
                extracted_text = extract_text_from_pdf(file_bytes)
            elif "word" in file_type or uploaded_file.name.endswith(".docx"):
                extracted_text = extract_text_from_docx(BytesIO(file_bytes))
            elif "image" in file_type:
                extracted_text = extract_text_from_image(BytesIO(file_bytes))
            else:
                extracted_text = "Unsupported file format."

        st.subheader("📝 Extracted Text")
        st.text_area("Result", extracted_text, height=400)

# -------------------------
# Tab 3: Agreement Generator
# -------------------------
with tab3:
    st.header("📄 Legal Agreement Generator")
    st.markdown("Generate software service agreements between two parties.")

    company_name = st.text_input("Your Company Name", value="Chereka Technology")
    client_name = st.text_input("Client Name")
    service_description = st.text_area("Service Description")

    if st.button("🧾 Generate Agreement") and company_name and client_name and service_description:
        agreement = generate_agreement(company_name, client_name, service_description)
        st.text_area("Generated Agreement", agreement, height=350)
        st.download_button("📥 Download Agreement", data=agreement, file_name="legal_agreement.txt")

# -------------------------
# Tab 4: About
# -------------------------
with tab4:
    st.header("📥 About LegalEase AI")
    st.markdown("""
    **LegalEase AI** is your digital legal assistant. It allows:
    - 📤 Parsing of legal files: PDFs, Word docs, images
    - 🧾 Agreement drafting for SaaS and software services
    - 🤖 Conversational chatbot powered by OpenAI
    
    Built by **Chereka Technology** 🇪🇹
    """)

    st.markdown("🔗 [Contact Developer](https://samueldagne.bio)")
