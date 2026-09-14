# 🚀 Enterprise Knowledge Base Document Chatbot (RAG)

An AI-powered **Enterprise Knowledge Base Chatbot** that allows users to upload PDF documents and ask intelligent questions about their content using **Retrieval-Augmented Generation (RAG)**.

The application processes PDF documents, converts their content into vector embeddings using **Google Gemini**, stores them in **Qdrant Cloud**, and retrieves relevant information to generate AI-powered answers.

---

# 📌 Project Overview

Traditional AI chatbots can answer questions using their general knowledge, but businesses often need AI systems that can answer questions based specifically on their internal documents.

This project solves that problem using **Retrieval-Augmented Generation (RAG)**.

Users can:

- 📄 Upload PDF documents
- ✂️ Automatically split documents into chunks
- 🧠 Generate embeddings using Google Gemini
- 🗄️ Store embeddings in Qdrant Cloud
- 🔍 Retrieve relevant information using semantic search
- 🤖 Ask questions in natural language
- 💬 Receive AI-generated answers based on uploaded documents
- 📚 View uploaded PDFs
- 🗑️ Delete documents from the knowledge base

---

# 🧠 What is RAG?

**RAG (Retrieval-Augmented Generation)** combines two processes:

1. **Retrieval** – Find relevant information from a knowledge base.
2. **Generation** – Use an AI model to generate a natural language answer.

## Document Ingestion Flow

```text
Upload PDF
    ↓
Load PDF
    ↓
Create Text Chunks
    ↓
Generate Gemini Embeddings
    ↓
Store in Qdrant Cloud
