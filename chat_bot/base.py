from abc import ABC, abstractmethod

class CHATBOT(ABC):
    @abstractmethod
    def ask(self, query: str, context: str = "") -> str:
        """Ask the LLM with optional context and return response"""
        pass
