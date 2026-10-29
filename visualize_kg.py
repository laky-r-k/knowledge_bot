"""Visualize the Knowledge Graph as an interactive HTML page using pyvis."""

import glob
from pyvis.network import Network
from kg_builder.gemini_kg_builder import GeminiKGBuilder

# Paths
FACULTY_DIR = "data/faculty"
TRIPLES_PATH = "data/kg_cache/triples.json"
GRAPH_PATH = "data/kg_cache/graph.graphml"

# 1. Build or load KG
kg = GeminiKGBuilder()

if not kg.load(TRIPLES_PATH, GRAPH_PATH):
    faculty_files = sorted(glob.glob(f"{FACULTY_DIR}/*.txt"))
    faculty_files = [f for f in faculty_files if "_combined" not in f]

    print(f"📄 Found {len(faculty_files)} faculty files")
    triples = kg.extract_triples_from_files(faculty_files)
    kg.build_graph(triples)
    kg.save(TRIPLES_PATH, GRAPH_PATH)
else:
    kg.build_graph(kg.triples)

print(f"📊 Nodes: {kg.graph.number_of_nodes()}  |  Edges: {kg.graph.number_of_edges()}  |  Triples: {len(kg.triples)}")

print("\n🔗 Sample triples:")
for s, p, o in kg.triples[:15]:
    print(f"   ({s})  --[{p}]-->  ({o})")

# 2. Build interactive pyvis graph
net = Network(height="750px", width="100%", bgcolor="#1a1a2e", font_color="white",
              directed=True, notebook=False)

net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150)

# Color faculty names differently from other nodes
faculty_names = set()
for s, p, o in kg.triples:
    if p in ["designation", "department", "email"]:
        faculty_names.add(s)

for subj, pred, obj in kg.triples:
    # Faculty nodes = orange, others = blue/green
    subj_color = "#FF9800" if subj in faculty_names else "#4FC3F7"
    obj_color = "#FF9800" if obj in faculty_names else "#81C784"

    net.add_node(subj, label=subj, color=subj_color, size=25 if subj in faculty_names else 15)
    net.add_node(obj, label=obj, color=obj_color, size=25 if obj in faculty_names else 15)
    net.add_edge(subj, obj, title=pred, label=pred, color="#E0E0E0", font={"size": 10})

net.show_buttons(filter_=["physics"])

output_path = "data/knowledge_graph.html"
net.save_graph(output_path)
print(f"\n✅ Interactive graph saved to {output_path}")
