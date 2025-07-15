import spacy
import networkx as nx
import logging
from kg_builder.base import BaseKGBuilder
from config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(CONFIG["LOG_FILE"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SpaCyKGBuilder(BaseKGBuilder):
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.graph = nx.DiGraph()
        logger.info("Initialized SpaCyKGBuilder")

    def extract_triples(self, text: str) -> list:
        logger.info("Extracting triples from text")
        try:
            doc = self.nlp(text)
            triples = []
            for sent in doc.sents:
                for token in sent:
                    if token.dep_ in ("nsubj", "dobj"):
                        subject = token.text
                        verb = token.head.text
                        for child in token.head.children:
                            if child.dep_ == "dobj":
                                obj = child.text
                                triples.append((subject, verb, obj))
            return triples
        except Exception as e:
            logger.error(f"Triple Extraction Error: {e}")
            return []

    def build_graph(self, triples: list) -> None:
        logger.info("Building knowledge graph")
        try:
            for subj, pred, obj in triples:
                self.graph.add_edge(subj, obj, predicate=pred)
            nx.write_pickle(self.graph, CONFIG["KG_GRAPH_PATH"])
            logger.info(f"Graph saved to {CONFIG['KG_GRAPH_PATH']}")
        except Exception as e:
            logger.error(f"Graph Building Error: {e}")

    def load_graph(self, path: str = CONFIG["KG_GRAPH_PATH"]) -> None:
        logger.info(f"Loading graph from {path}")
        try:
            self.graph = nx.read_pickle(path)
            logger.info("Graph loaded successfully")
        except Exception as e:
            logger.error(f"Graph Loading Error: {e}")