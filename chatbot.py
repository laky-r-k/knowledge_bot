# bot/chatbot.py
from bot.graph_builder import extract_triples
from bot.visualize import visualize_kg
from llm.llm_chat import ask_llm
import networkx as nx

def build_graph_from_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    triples = extract_triples(text)
    G = nx.DiGraph()
    for head, rel, tail in triples:
        G.add_edge(head, tail, label=rel)
    return G, text

def query_knowledge_graph(G, entity):
    if entity in G:
        results = []
        for target in G[entity]:
            rel = G[entity][target]['label']
            results.append(f"{entity} {rel}s {target}")
        return "\n".join(results)
    return None

def run_chatbot():
    print("📡 Loading knowledge graph...")
    G, full_text = build_graph_from_text("data/satellite_facts.txt")
    print("✅ Ready! Ask me anything about satellites, weather, or ISRO.")

    while True:
        question = input("\n🧠 You: ")
        if question.lower() in ["exit", "quit"]:
            break

        # Try to pull an entity from the question (last noun word)
        words = question.strip().split()
        entity = words[-1]

        # First try the KG
        answer = query_knowledge_graph(G, entity)

        if answer:
            print(f"🤖 Bot (KG):\n{answer}")
        else:
            print("🤖 Bot (LLM): Thinking...")
            llm_response = ask_llm(question, context=full_text[:4000])  # limit context
            print(f"💬 {llm_response}")

if __name__ == "__main__":
    run_chatbot()
