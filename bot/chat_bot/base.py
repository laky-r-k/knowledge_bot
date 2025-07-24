from abc import ABC, abstractmethod
from typing import List, Dict

class BaseChatBot(ABC):
    """Abstract base class for chatbots."""
    def __init__(self, kg_builder=None):
        self.history: List[Dict[str, str]] = []
        self.kg_builder = kg_builder

    @abstractmethod
    def ask(self, query: str) -> dict:
        """Ask the chatbot with optional context and return response as a dictionary."""
        pass

    def add_to_history(self, user: str, bot: str) -> None:
        """Add a user-bot conversation pair to history."""
        self.history.append({"user": user, "bot": bot})

    def get_recent_context(self, turns: int = 3) -> str:
        """Get recent conversation history as context (default: last 3 turns)."""
        prompt = ""
        for turn in self.history[-turns:]:
            prompt += f"User: {turn['user']}\nBot: {turn['bot']}\n"
        return prompt

    def clear_history(self) -> None:
        """Clear the chat history."""
        self.history = []