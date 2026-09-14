'''http://127.0.0.1:8000/docs?utm_source=chatgpt.com   => For FAST API SWAGGER API DOCS'''

import logging
import os
import uuid
import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from data_loader import DataLoader
from vector_db import QdrantStorage
from fastapi import FastAPI
from pydantic import BaseModel

import inngest
import inngest.fast_api

from dotenv import load_dotenv

from rag_chat import RAGChat


# Load variables from .env
load_dotenv()


# Create Inngest client
inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)


# Create FastAPI app
app = FastAPI()


# Create RAG chatbot
chatbot = RAGChat()


# -----------------------------
# CHAT REQUEST MODEL
# -----------------------------

class ChatRequest(BaseModel):
    question: str


# -----------------------------
# HOME ENDPOINT
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "RAG AI Chatbot is running!"
    }


# -----------------------------
# CHAT ENDPOINT
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question

    result = chatbot.ask(question)

    return result

# -----------------------------
# PDF UPLOAD ENDPOINT
# -----------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Check if uploaded file is a PDF
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Create uploads folder
    os.makedirs("uploads", exist_ok=True)

    # Create unique ID
    file_id = str(uuid.uuid4())

    # Save PDF path
    file_path = f"uploads/{file_id}.pdf"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Send event to Inngest
    await inngest_client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "file_id": file_id,
                "file_path": file_path,
                "source": file.filename
            }
        )
    )

    return {
        "message": "PDF uploaded and sent for processing",
        "file_id": file_id,
        "file_path": file_path
    }

@app.get("/pdfs")
def get_pdfs():

    storage = QdrantStorage()

    # Get all points from Qdrant
    results, _ = storage.client.scroll(
        collection_name="docs",
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    pdfs = {}

    for point in results:

        payload = point.payload or {}
        source = payload.get("source", "Unknown")

        if source not in pdfs:
            pdfs[source] = 0

        pdfs[source] += 1

    return {
        "total_pdfs": len(pdfs),
        "pdfs": pdfs
    }
@app.delete("/pdf/{source}")
def delete_pdf(source: str):

    storage = QdrantStorage()

    storage.delete_by_source(source)

    return {
        "message": f"{source} deleted successfully from Qdrant"
    }
# -----------------------------
# INNGEST FUNCTION
# -----------------------------

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(
        event="rag/ingest_pdf"
    )
)

async def rag_ingest_pdf(ctx: inngest.Context):

    # Get information sent from the upload event
    file_path = ctx.event.data["file_path"]
    source = ctx.event.data["source"]

    print(f"Processing PDF: {source}")


    # Create DataLoader
    loader = DataLoader()


    # Create Qdrant storage
    storage = QdrantStorage()


    # STEP 1: Load PDF
    documents = loader.load_pdf(file_path)

    print("PDF loaded")


    # STEP 2: Create chunks
    chunks = loader.create_chunks(documents)

    print(f"Created {len(chunks)} chunks")


    # STEP 3: Create Gemini embeddings
    vectors = loader.create_embeddings(chunks)

    print(f"Created {len(vectors)} embeddings")


    # STEP 4: Create unique IDs
    ids = [
        str(uuid.uuid4())
        for _ in chunks
    ]


    # STEP 5: Create payloads
    payloads = [
        {
            "text": chunk,
            "source": source
        }
        for chunk in chunks
    ]


    # STEP 6: Store in Qdrant
    storage.upsert(
        ids=ids,
        vectors=vectors,
        payloads=payloads
    )

    print("PDF successfully stored in Qdrant!")

    return {
        "message": "PDF ingestion completed",
        "chunks": len(chunks),
        "source": source
    }

# -----------------------------
# CONNECT INNGEST + FASTAPI
# -----------------------------

inngest.fast_api.serve(
    app,
    inngest_client,
    [rag_ingest_pdf]
)