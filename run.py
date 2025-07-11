# run_bot.py

from chatbot.gemini_chatbot import GeminiChatBot
from kg_builder.spacy_kg_builder import SpaCyKGBuilder

# Step 1: Load and build the Knowledge Graph
kg = SpaCyKGBuilder()

with open("data/mosdac_scraped.txt", "r", encoding="utf-8") as f:
    text = f.read()

triples = kg.extract_triples(text)
kg.build_graph(triples)

# Step 2: Initialize chatbot with the KG
bot = GeminiChatBot(kg_builder=kg)

# Step 3: Run CLI loop
print("🤖 Ask anything about satellites or MOSDAC (type 'exit' to quit)")

while True:
    query = input("🧑 You: ")
    if query.lower() in ['exit', 'quit']:
        break

    response = bot.ask(query)
    print("🤖 Bot:", response)
