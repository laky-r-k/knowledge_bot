# run_bot.py

import glob
from chat_bot.gemini_chatbot import GeminiChatBot
from kg_builder.gemini_kg_builder import GeminiKGBuilder

# Paths
FACULTY_DIR = "data/faculty"
TRIPLES_PATH = "data/kg_cache/triples.json"
GRAPH_PATH = "data/kg_cache/graph.graphml"

# Step 1: Build or load the Knowledge Graph
kg = GeminiKGBuilder()

if not kg.load(TRIPLES_PATH, GRAPH_PATH):
    # Process each faculty file individually
    faculty_files = sorted(glob.glob(f"{FACULTY_DIR}/*.txt"))
    # Exclude the combined file
    faculty_files = [f for f in faculty_files if "_combined" not in f]

    print(f"📄 Found {len(faculty_files)} faculty files")
    triples = kg.extract_triples_from_files(faculty_files)
    kg.build_graph(triples)
    kg.save(TRIPLES_PATH, GRAPH_PATH)
else:
    kg.build_graph(kg.triples)

print(f"\n📊 Knowledge Graph: {len(kg.triples)} triples, {kg.graph.number_of_nodes()} nodes, {kg.graph.number_of_edges()} edges")

# Step 2: Initialize chatbot with the KG
bot = GeminiChatBot(kg_builder=kg)

# Step 3: Run CLI loop
print("🤖 Ask anything about the department faculty (type 'exit' to quit)\n")

while True:
    query = input("🧑 You: ")
    if query.lower() in ['exit', 'quit']:
        break

    response = bot.ask(query)
    print("🤖 Bot:", response)
