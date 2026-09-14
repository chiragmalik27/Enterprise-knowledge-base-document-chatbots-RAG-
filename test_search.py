from data_loader import DataLoader
from vector_db import QdrantStorage


# Create objects
loader = DataLoader()
storage = QdrantStorage()


# Ask a question
question = input("Ask a question about your PDF: ")


# Convert question into Gemini embedding
query_vector = loader.create_query_embedding(question)


# Search Qdrant
result = storage.search(
    query_vector=query_vector,
    top_k=5
)


# Print results
print("\n--- RELEVANT INFORMATION ---\n")

for context in result["contexts"]:
    print(context)
    print("\n-------------------\n")


print("Sources:", result["sources"])