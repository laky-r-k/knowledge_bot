import google.generativeai as genai
from .base import BaseChatBot
import os
from dotenv import load_dotenv
import logging

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

class GeminiChatBot(BaseChatBot):
    def __init__(self, kg_builder):
        super().__init__(kg_builder)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat_session = self.model.start_chat(history=[])
        logger.info("Initialized GeminiChatBot")

    def ask(self, query: str) -> dict:
        logger.info(f"Processing query: {query}")
        try:
            context = self.get_recent_context()
            prompt = f"""
            You are a scientific assistant for the MOSDAC Chatbot, specializing in meteorological and oceanographic data.
            Use the knowledge graph to provide accurate, concise answers. If the graph lacks data, use your general knowledge.
            Query: {query}
            Knowledge Graph: {self.kg_builder.graph.edges(data=True)}
            Recent Conversation: {context}
            Provide a response and up to 3 relevant follow-up question suggestions.
            """
            response = self.chat_session.send_message(prompt)
            self.add_to_history(query, response.text)
            suggestions = self._generate_suggestions(query)
            return {"response": response.text, "status": "success", "suggestions": suggestions}
        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return {"response": f"Error: {str(e)}", "status": "error", "suggestions": []}

    def _generate_suggestions(self, query: str) -> list:
        try:
            related_nodes = []
            for node in self.kg_builder.graph.nodes:
                if query.lower() in node.lower():
                    related_nodes.extend([n for n in self.kg_builder.graph.neighbors(node)])
            return [f"What is {node}?" for node in related_nodes[:3]]
        except Exception as e:
            logger.error(f"Suggestion Generation Error: {e}")
            return []

    def clear_history(self) -> None:
        logger.info("Clearing chat history")
        try:
            super().clear_history()
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            logger.error(f"Clear History Error: {e}")