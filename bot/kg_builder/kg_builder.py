import spacy
import networkx as nx
import os
from dotenv import load_dotenv
import logging
from .base import BaseKGBuilder

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

# Load environment variables
load_dotenv()

class SpaCyKGBuilder(BaseKGBuilder):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.max_length = 4000000  # Increased to handle large texts
        self.graph = nx.DiGraph()
        logger.info("Initialized SpaCyKGBuilder with max_length=%d", self.nlp.max_length)

    def extract_triples(self, text: str) -> list:
        logger.info("Extracting triples from text (length=%d)", len(text))
        try:
            triples = []
            chunk_size = 1000000
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                doc = self.nlp(chunk)
                for sent in doc.sents:
                    for token in sent:
                        if token.dep_ in ("nsubj", "dobj"):
                            subject = token.text
                            verb = token.head.text
                            for child in token.head.children:
                                if child.dep_ == "dobj":
                                    obj = child.text
                                    triples.append((subject, verb, obj))
            logger.info("Extracted %d triples", len(triples))
            return triples
        except Exception as e:
            logger.error(f"Triple Extraction Error: {e}")
            return []
    def build_graph(self, triples: list) -> None:
        logger.info("Building knowledge graph with %d triples", len(triples))
        try:
            for subj, pred, obj in triples:
                self.graph.add_edge(subj, obj, predicate=pred)
            graph_path = os.getenv("KG_GRAPH_PATH", "data/kg_graph.gpickle")
            os.makedirs(os.path.dirname(graph_path), exist_ok=True)
            nx.write_gpickle(self.graph, graph_path)
            logger.info(f"Graph saved to {graph_path}")
        except Exception as e:
            logger.error(f"Graph Building Error: {e}")
            raise

    def search(self, query: str) -> list:
        logger.info(f"Searching graph for query: {query}")
        try:
            doc = self.nlp(query)
            keywords = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]
            matching_triples = []
            for subj, obj, data in self.graph.edges(data=True):
                if any(kw in subj.lower() or kw in obj.lower() for kw in keywords):
                    matching_triples.append((subj, data["predicate"], obj))
            return matching_triples[:5]
        except Exception as e:
            logger.error(f"Search Error: {e}")
            return []

    def to_prompt_text(self, triples: list) -> str:
        logger.info("Converting triples to prompt text")
        try:
            return "\n".join([f"{subj} {pred} {obj}" for subj, pred, obj in triples])
        except Exception as e:
            logger.error(f"Prompt Text Conversion Error: {e}")
            return ""

    def load_graph(self, path: str = os.getenv("KG_GRAPH_PATH", "data/kg_graph.gpickle")) -> None:
        logger.info(f"Loading graph from {path}")
        try:
            if os.path.exists(path):
                self.graph = nx.read_gpickle(path)
                logger.info("Graph loaded successfully")
            else:
                logger.error(f"Graph file {path} not found")
                raise FileNotFoundError(f"Graph file {path} not found")
        except Exception as e:
            logger.error(f"Graph Loading Error: {e}")
            raise