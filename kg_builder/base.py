from abc import ABC, abstractmethod
from typing import List, Tuple
import networkx as nx

class BaseKGBuilder(ABC):

    @abstractmethod
    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract (subject, predicate, object) triples from text"""
        pass

    @abstractmethod
    def build_graph(self, triples: List[Tuple[str, str, str]]) -> nx.DiGraph:
        """Build a knowledge graph from triples"""
        pass

    @abstractmethod
    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """Search the graph and return matching triples"""
        pass

    @abstractmethod
    def to_prompt_text(self, triples: List[Tuple[str, str, str]]) -> str:
        """Convert triples into readable prompt text for LLM"""
        pass
