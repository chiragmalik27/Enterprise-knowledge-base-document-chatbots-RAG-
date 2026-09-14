import os

from dotenv import load_dotenv
from google import genai

from data_loader import DataLoader
from vector_db import QdrantStorage


# Load .env file
load_dotenv()


class RAGChat:

    def __init__(self):

        # Get Gemini API key
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        # Gemini client
        self.client = genai.Client(api_key=api_key)

        # Our existing tools
        self.loader = DataLoader()
        self.storage = QdrantStorage()


    def ask(self, question):

        # STEP 1: Convert question into embedding
        query_vector = self.loader.create_query_embedding(question)


        # STEP 2: Search Qdrant
        result = self.storage.search(
            query_vector=query_vector,
            top_k=5
        )


        # STEP 3: Combine the relevant PDF text
        context = "\n\n".join(result["contexts"])


        # STEP 4: Create prompt for Gemini
        prompt = f"""
You are a helpful assistant.

Answer the user's question using ONLY the information provided
in the context below.

If the answer is not available in the context, say:
"I could not find the answer in the uploaded document."

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""


        # STEP 5: Ask Gemini to generate the answer
        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # Return answer and sources
        return {
            "answer": response.text,
            "sources": result["sources"]
        }