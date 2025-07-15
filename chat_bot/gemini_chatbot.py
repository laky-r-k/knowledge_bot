import google.generativeai as genai
from chat_bot.base import CHATBOT
from typing import Optional, Dict
from dotenv import load_dotenv
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

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

class GeminiChatBot(CHATBOT):
    def __init__(self, model_name: str = "models/gemini-1.5-flash", kg_builder: Optional[object] = None):
        super().__init__()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.kg_builder = kg_builder
        logger.info(f"Initialized GeminiChatBot with model {model_name}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def ask(self, query: str, context: str = "", use_kg: bool = True) -> Dict[str, str]:
        """
        Answer a query using:
        - optional KG search
        - chat memory (context)
        - Gemini LLM for response
        Returns: {"response": str, "status": str}
        """
        logger.info(f"Processing query: {query}")
        try:
            kg_context = self.search_kg(query, use_kg)
            chat_context = context or self.get_recent_context()
            combined_context = f"{kg_context}\n{chat_context}".strip()

            prompt = f"""You are a chatbot for the MOSDAC website.
Use the facts to enhance the depth of the answer:

{combined_context}

User: {query}
Bot:"""

            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            self.add_to_history(query, answer)
            logger.info("Query processed successfully")
            return {"response": answer, "status": "success"}
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {"response": f"[LLM Error] {e}", "status": "error"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def search_kg(self, query: str, use_kg: bool) -> str:
        """Extract keywords from query and search the knowledge graph."""
        logger.info(f"Searching KG for query: {query}")
        if not use_kg or not self.kg_builder:
            return ""

        prompt = f"""System: You are a chatbot for the MOSDAC website. Extract keywords from the query for KG search.
Query: {query}
Return: Comma-separated keywords"""
        try:
            response = self.model.generate_content(prompt)
            keywords = response.text.strip()
            if not keywords:
                logger.warning("No keywords extracted from query")
                return ""
            keywords = keywords.split(",")
            logger.info(f"Extracted keywords: {keywords}")
        except Exception as e:
            logger.error(f"Keyword Extraction Error: {e}")
            return f"[LLM Error] {e}"

        kg_context = ""
        try:
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    triples = self.kg_builder.search(keyword)
                    kg_context += self.kg_builder.to_prompt_text(triples)
            logger.info("KG search completed")
        except Exception as e:
            logger.error(f"KG Error: {e}")
            kg_context = f"[KG Error] {e}"
        return kg_context