# bot/visualize.py
import networkx as nx
import matplotlib.pyplot as plt

def visualize_kg(triples):
    G = nx.DiGraph()
    for head, relation, tail in triples:
        G.add_edge(head, tail, label=relation)

    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
    plt.title("Knowledge Graph")
    plt.show()

    return G
