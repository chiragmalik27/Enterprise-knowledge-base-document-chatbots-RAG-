from rag_chat import RAGChat


# Create chatbot
chatbot = RAGChat()


# Ask question
question = input("Ask a question about your PDF: ")


# Get answer
result = chatbot.ask(question)


print("\n🤖 ANSWER:\n")

print(result["answer"])


print("\n📄 SOURCES:")

for source in result["sources"]:
    print(source)