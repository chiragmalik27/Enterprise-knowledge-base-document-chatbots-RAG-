import streamlit as st
import requests


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="RAG AI Chatbot",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# TITLE
# -----------------------------

st.title("🤖 RAG AI Chatbot")

st.write("Upload PDFs and ask questions about your documents!")


# -----------------------------
# SIDEBAR - PDF UPLOAD
# -----------------------------

with st.sidebar:

    st.header("📄 Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        if st.button("Upload PDF"):

            with st.spinner("Uploading and processing PDF..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    "https://enterprise-knowledge-base-document.onrender.com/upload",
                    files=files
                )

                if response.status_code == 200:

                    data = response.json()

                    st.success("PDF uploaded successfully! 🎉")

                    st.write(
                        f"📄 {uploaded_file.name}"
                    )

                else:

                    st.error(
                        f"Upload failed: {response.text}"
                    )


# -----------------------------
# CHAT SECTION
# -----------------------------

st.header("💬 Chat with your documents")


# Create chat history
if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# User enters a question
question = st.chat_input(
    "Ask a question about your documents..."
)


if question:

    # Show user question
    with st.chat_message("user"):

        st.write(question)


    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # Get answer from FastAPI
    with st.chat_message("assistant"):

        with st.spinner("🤔 Thinking..."):

            response = requests.post(
                "https://enterprise-knowledge-base-document.onrender.com/chat",
                json={
                    "question": question
                }
            )


            if response.status_code == 200:

                data = response.json()

                # Get answer
                answer = data.get(
                    "answer",
                    "Sorry, I could not find an answer."
                )

                # Display answer
                st.write(answer)

                # Save answer
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                # Display sources
                sources = data.get("sources", [])

                if sources:

                    st.caption(
                        "📄 Sources: "
                        + ", ".join(sources)
                    )

            else:

                st.error(
                    f"Error: {response.text}"
                )