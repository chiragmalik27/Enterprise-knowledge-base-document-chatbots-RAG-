import os
import uuid
import logging

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks
)

from pydantic import BaseModel

from data_loader import DataLoader
from vector_db import QdrantStorage
from rag_chat import RAGChat


# -----------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------

load_dotenv()


# -----------------------------
# CREATE FASTAPI APP
# -----------------------------

app = FastAPI(
    title="Enterprise Knowledge Base RAG API"
)


# -----------------------------
# CREATE RAG CHATBOT
# -----------------------------

chatbot = RAGChat()


# -----------------------------
# CHAT REQUEST MODEL
# -----------------------------

class ChatRequest(BaseModel):
    question: str


# =====================================================
# PDF PROCESSING FUNCTION
# =====================================================

def process_pdf(file_path: str, source: str):

    try:

        print(f"\nProcessing PDF: {source}")


        # Create DataLoader
        loader = DataLoader()


        # Create Qdrant storage
        storage = QdrantStorage()


        # -----------------------------
        # STEP 1: LOAD PDF
        # -----------------------------

        documents = loader.load_pdf(file_path)

        print("PDF loaded")


        # -----------------------------
        # STEP 2: CREATE CHUNKS
        # -----------------------------

        chunks = loader.create_chunks(documents)

        print(f"Created {len(chunks)} chunks")


        # -----------------------------
        # STEP 3: CREATE EMBEDDINGS
        # -----------------------------

        vectors = loader.create_embeddings(chunks)

        print(f"Created {len(vectors)} embeddings")


        # -----------------------------
        # STEP 4: CREATE UNIQUE IDs
        # -----------------------------

        ids = [

            str(uuid.uuid4())

            for _ in chunks

        ]


        # -----------------------------
        # STEP 5: CREATE PAYLOADS
        # -----------------------------

        payloads = [

            {
                "text": chunk,
                "source": source
            }

            for chunk in chunks

        ]


        # -----------------------------
        # STEP 6: STORE IN QDRANT
        # -----------------------------

        storage.upsert(

            ids=ids,

            vectors=vectors,

            payloads=payloads

        )


        print(f"PDF successfully stored in Qdrant: {source}")


        # -----------------------------
        # OPTIONAL: DELETE LOCAL PDF
        # -----------------------------

        if os.path.exists(file_path):

            os.remove(file_path)

            print("Temporary PDF file deleted")


    except Exception as e:

        print(f"ERROR PROCESSING PDF: {str(e)}")

        logging.exception("PDF processing failed")


# =====================================================
# HOME ENDPOINT
# =====================================================

@app.get("/")
def home():

    return {

        "message": "RAG AI Chatbot is running!"

    }


# =====================================================
# CHAT ENDPOINT
# =====================================================

@app.post("/chat")
def chat(request: ChatRequest):

    result = chatbot.ask(request.question)

    return result


# =====================================================
# PDF UPLOAD ENDPOINT
# =====================================================

@app.post("/upload")
async def upload_pdf(

    background_tasks: BackgroundTasks,

    file: UploadFile = File(...)

):


    # -----------------------------
    # CHECK PDF
    # -----------------------------

    if not file.filename or not file.filename.lower().endswith(".pdf"):

        raise HTTPException(

            status_code=400,

            detail="Only PDF files are allowed"

        )


    # -----------------------------
    # CREATE UPLOADS FOLDER
    # -----------------------------

    os.makedirs(

        "uploads",

        exist_ok=True

    )


    # -----------------------------
    # CREATE UNIQUE FILE ID
    # -----------------------------

    file_id = str(uuid.uuid4())


    # -----------------------------
    # CREATE FILE PATH
    # -----------------------------

    file_path = f"uploads/{file_id}.pdf"


    # -----------------------------
    # SAVE PDF
    # -----------------------------

    with open(file_path, "wb") as buffer:

        content = await file.read()

        buffer.write(content)


    print(f"PDF uploaded successfully: {file.filename}")


    # -----------------------------
    # PROCESS PDF IN BACKGROUND
    # -----------------------------

    background_tasks.add_task(

        process_pdf,

        file_path,

        file.filename

    )


    # -----------------------------
    # RETURN RESPONSE IMMEDIATELY
    # -----------------------------

    return {

        "message": "PDF uploaded successfully and processing has started",

        "file_id": file_id,

        "source": file.filename

    }


# =====================================================
# GET ALL PDFs
# =====================================================

@app.get("/pdfs")
def get_pdfs():

    storage = QdrantStorage()


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


# =====================================================
# DELETE PDF
# =====================================================

@app.delete("/pdf/{source}")
def delete_pdf(source: str):

    storage = QdrantStorage()


    storage.delete_by_source(source)


    return {

        "message": f"{source} deleted successfully from Qdrant"

    }