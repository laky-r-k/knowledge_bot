from abc import ABC, abstractmethod

class CHATBOT(ABC):
    def __init__(self):
        self.history = []

    @abstractmethod
    def ask(self, query: str, context: str = "") -> str:
        """Ask the chatbot with optional context and return response"""
        pass

    def add_to_history(self, user: str, bot: str):
        self.history.append({"user": user, "bot": bot})

    def get_recent_context(self, turns: int = 3) -> str:
        prompt = ""
        for turn in self.history[-turns:]:
            prompt += f"User: {turn['user']}\nBot: {turn['bot']}\n"
        return prompt
