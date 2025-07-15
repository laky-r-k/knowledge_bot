import spacy
import networkx as nx
from typing import List, Tuple
from kg_builder.base import BaseKGBuilder
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SpaCyKGBuilder(BaseKGBuilder):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.graph = nx.DiGraph()
        self.triples: List[Tuple[str, str, str]] = []
        logger.info("Initialized SpaCyKGBuilder")

    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract subject-predicate-object triples from text using SpaCy."""
        logger.info("Extracting triples from text")
        triples = []
        try:
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
            logger.info(f"Extracted {len(triples)} triples")
        except Exception as e:
            logger.error(f"Triple Extraction Error: {e}")
        return triples

    def build_graph(self, triples: List[Tuple[str, str, str]]) -> nx.DiGraph:
        """Build a directed graph from triples using NetworkX."""
        logger.info("Building knowledge graph")
        G = nx.DiGraph()
        for s, p, o in triples:
            G.add_edge(s, o, label=p)
        self.graph = G
        try:
            nx.write_gpickle(G, "data/kg_graph.gpickle")
            logger.info("Saved knowledge graph to data/kg_graph.gpickle")
        except Exception as e:
            logger.error(f"Graph Saving Error: {e}")
        return G

    def load_graph(self, path: str = "data/kg_graph.gpickle") -> nx.DiGraph:
        """Load a saved knowledge graph from a file."""
        logger.info(f"Loading knowledge graph from {path}")
        try:
            if os.path.exists(path):
                self.graph = nx.read_gpickle(path)
                logger.info("Loaded knowledge graph")
            else:
                logger.warning(f"No graph found at {path}")
                self.graph = nx.DiGraph()
        except Exception as e:
            logger.error(f"Graph Loading Error: {e}")
            self.graph = nx.DiGraph()
        return self.graph

    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """Search the graph for triples containing the query keyword."""
        logger.info(f"Searching KG for query: {query}")
        keyword = query.lower()
        matches = [t for t in self.triples if keyword in t[0].lower() or keyword in t[2].lower()]
        logger.info(f"Found {len(matches)} matching triples")
        return matches

    def to_prompt_text(self, triples: List[Tuple[str, str, str]]) -> str:
        """Convert triples into readable prompt text for LLM."""
        lines = [f"{i+1}. {s} {p} {o}." for i, (s, p, o) in enumerate(triples)]
        return "Facts:\n" + "\n".join(lines) if lines else ""