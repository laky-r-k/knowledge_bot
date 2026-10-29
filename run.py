# run_bot.py

from chat_bot.gemini_chatbot import GeminiChatBot
from kg_builder.kg_builder import SpaCyKGBuilder

# Step 1: Load and build the Knowledge Graph
kg = SpaCyKGBuilder()

with open("data/faculty/_combined.txt", "r", encoding="utf-8") as f:
    text = f.read()

triples = kg.extract_triples(text)
kg.build_graph(triples)

print(f"📊 Knowledge Graph: {len(triples)} triples extracted")

# Step 2: Initialize chatbot with the KG
bot = GeminiChatBot(kg_builder=kg)

# Step 3: Run CLI loop
print("🤖 Ask anything about the department faculty (type 'exit' to quit)")

while True:
    query = input("🧑 You: ")
    if query.lower() in ['exit', 'quit']:
        break

    response = bot.ask(query)
    print("🤖 Bot:", response)
