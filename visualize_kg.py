"""Visualize the Knowledge Graph as an interactive HTML page using pyvis."""

from pyvis.network import Network
from kg_builder.kg_builder import SpaCyKGBuilder

# 1. Load data & build KG
kg = SpaCyKGBuilder()

with open("data/faculty_data.txt", "r", encoding="utf-8") as f:
    text = f.read()

triples = kg.extract_triples(text)
kg.build_graph(triples)

print(f"📊 Nodes: {kg.graph.number_of_nodes()}  |  Edges: {kg.graph.number_of_edges()}  |  Triples: {len(triples)}")

print("\n🔗 Sample triples:")
for s, p, o in triples[:15]:
    print(f"   ({s})  --[{p}]-->  ({o})")

# 2. Build interactive pyvis graph
net = Network(height="750px", width="100%", bgcolor="#1a1a2e", font_color="white",
              directed=True, notebook=False)

# Physics settings for nice layout
net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150)

# Add nodes and edges from triples
for subj, pred, obj in triples:
    net.add_node(subj, label=subj, color="#4FC3F7", size=20)
    net.add_node(obj, label=obj, color="#81C784", size=20)
    net.add_edge(subj, obj, title=pred, label=pred, color="#E0E0E0", font={"size": 10})

# Enable interactive controls
net.show_buttons(filter_=["physics"])

output_path = "data/knowledge_graph.html"
net.save_graph(output_path)
print(f"\n✅ Interactive graph saved to {output_path}")
print(f"   Open it in your browser: file://{output_path}")
