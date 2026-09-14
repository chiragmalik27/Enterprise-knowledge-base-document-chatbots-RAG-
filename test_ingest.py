# import uuid

# from data_loader import DataLoader
# from vector_db import QdrantStorage


# # Create objects
# loader = DataLoader()
# storage = QdrantStorage()


# # 1. Load PDF
# documents = loader.load_pdf("sample.pdf")

# print("PDF loaded successfully")


# # 2. Create chunks
# chunks = loader.create_chunks(documents)

# print(f"Created {len(chunks)} chunks")


# # 3. Create Gemini embeddings
# vectors = loader.create_embeddings(chunks)

# print(f"Created {len(vectors)} embeddings")


# # 4. Create unique IDs
# ids = [
#     str(uuid.uuid4())
#     for _ in chunks
# ]


# # 5. Create payloads
# payloads = [
#     {
#         "text": chunk,
#         "source": "sample.pdf"
#     }
#     for chunk in chunks
# ]


# # 6. Store in Qdrant
# storage.upsert(
#     ids=ids,
#     vectors=vectors,
#     payloads=payloads
# )

# print("Successfully stored PDF in Qdrant!")