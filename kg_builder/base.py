from abc import ABC, abstractmethod
class BaseKGBuilder(ABC):
    @abstractmethod
    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
        pass

    @abstractmethod
    def build_graph(self, triples) -> Any:
        pass

    @abstractmethod
    def search(self, query: str) -> List[Tuple[str, str, str]]:
        """Search graph and return relevant triples"""
        pass

    @abstractmethod
    def to_prompt_text(self, triples) -> str:
        """Convert triples to LLM-friendly text"""
        pass
