import spacy
import networkx as nx
from typing import List, Tuple
from kg_builder.base import BaseKGBuilder

class SpaCyKGBuilder(BaseKGBuilder):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.graph = nx.DiGraph()
        self.triples = []

    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        triples = []
        doc = self.nlp(text)
        for sent in doc.sents:
            subj = None
            obj = None
            pred = None
            for token in sent:
                if "subj" in token.dep_:
                    subj = token.text
                if "obj" in token.dep_:
                    obj = token.text
                if token.dep_ == "ROOT":
                    pred = token.text
            if subj and pred and obj:
                triples.append((subj, pred, obj))
        self.triples = triples
        return triples

    def build_graph(self, triples: List[Tuple[str, str, str]]) -> nx.DiGraph:
        G = nx.DiGraph()
        for s, p, o in triples:
            G.add_edge(s, o, label=p)
        self.graph = G
        return G

    def search(self, query: str) -> List[Tuple[str, str, str]]:
        # naive search: return all triples containing the keyword
        keyword = query.lower()
        matches = [t for t in self.triples if keyword in t[0].lower() or keyword in t[2].lower()]
        return matches

    def to_prompt_text(self, triples: List[Tuple[str, str, str]]) -> str:
        lines = [f"{i+1}. {s} {p} {o}." for i, (s, p, o) in enumerate(triples)]
        return "Facts:\n" + "\n".join(lines)
