import os
from dotenv import load_dotenv
import time
from google import genai
from google.genai import types

from llama_index.core import SimpleDirectoryReader


# Load variables from .env file
load_dotenv()


class DataLoader:

    def __init__(self):
        # Get Gemini API key from .env
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        # Create Gemini client
        self.client = genai.Client(api_key=api_key)

        # Gemini embedding model
        self.embedding_model = "gemini-embedding-001"

    def load_pdf(self, file_path):
        """
        Load a PDF file and extract its text.
        """

        documents = SimpleDirectoryReader(
            input_files=[file_path]
        ).load_data()

        return documents

    def create_chunks(self, documents, chunk_size=1000):
        """
        Split PDF text into smaller chunks.
        """

        chunks = []

        for document in documents:

            text = document.text

            for i in range(0, len(text), chunk_size):

                chunk = text[i:i + chunk_size]

                if chunk.strip():
                    chunks.append(chunk)

        return chunks

    def create_embeddings(self, texts):

        all_vectors = []

        # Smaller batch size
        batch_size = 50

        for i in range(0, len(texts), batch_size):

            batch = texts[i:i + batch_size]

            print(
                f"Creating embeddings for chunks "
                f"{i + 1} to {i + len(batch)}"
            )

            # Maximum retry attempts
            max_retries = 5

            for attempt in range(max_retries):

                try:

                    response = self.client.models.embed_content(
                        model=self.embedding_model,
                        contents=batch,
                        config=types.EmbedContentConfig(
                            output_dimensionality=3072
                        )
                    )

                    if not response.embeddings:
                        raise ValueError(
                            "No embeddings returned by Gemini"
                        )

                    vectors = [
                        embedding.values
                        for embedding in response.embeddings
                    ]

                    all_vectors.extend(vectors)

                    # Success, leave retry loop
                    break

                except Exception as e:

                    # Last attempt failed
                    if attempt == max_retries - 1:
                        raise e

                    # Wait longer after every failed attempt
                    wait_time = 5 * (attempt + 1)

                    print(
                        f"Gemini rate limit/error. "
                        f"Waiting {wait_time} seconds before retrying..."
                    )

                    time.sleep(wait_time)

            # Wait before sending the next batch
            print("Waiting 3 seconds before next batch...")
            time.sleep(3)

        return all_vectors

    def create_query_embedding(self, query):

        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=query,
            config=types.EmbedContentConfig(
                output_dimensionality=3072
            )
        )

        if not response.embeddings:
            raise ValueError("No embedding was returned by Gemini")

        return response.embeddings[0].values