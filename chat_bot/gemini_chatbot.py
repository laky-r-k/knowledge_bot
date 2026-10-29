# chatbot/gemini_chatbot.py

import time
from typing import Optional, List, Dict
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from chat_bot.base import CHATBOT
from chat_bot.CONFIG.config import GEMINI_API_KEY
from langchain_core.runnables import RunnableLambda, RunnableMap

def safe_generate_content(model, prompt, retries=3, delay=8):
    """Generates content with automatic exponential backoff for free-tier rate limits."""
    for attempt in range(retries):
        try:
            return model.generate_content(prompt)
        except ResourceExhausted:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                raise
        except Exception:
            raise

class GeminiChatBot(CHATBOT):
    def __init__(self, model_name: str = "models/gemini-2.5-flash-lite", kg_builder: Optional[object] = None):
        super().__init__()
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.kg_builder = kg_builder

        # Define LangChain RAG chain
        self.rag_chain = (
            RunnableMap({"query": lambda x: x})
            | RunnableLambda(self.extract_keywords)
            | RunnableLambda(self.search_kg_triples)
            | RunnableLambda(self.generate_response)
        )

    def ask(self, query: str, context: str = "", use_kg: bool = True) -> str:
        if use_kg and self.kg_builder:
            return self.rag_chain.invoke(query)
        else:
            prompt = f"{context}\n\nUser: {query}\nBot:"
            response = safe_generate_content(self.model, prompt)
            return response.text.strip()

    def extract_keywords(self, input_dict: Dict) -> Dict:
        query = input_dict["query"]
        prompt = f"""Extract only important keywords for KG search from the following query.
Return comma-separated values. No explanation.

Query: {query}
Keywords:"""

        try:
            response = safe_generate_content(self.model, prompt)
            keywords = [kw.strip() for kw in response.text.strip().split(",") if kw.strip()]
        except Exception as e:
            keywords = []

        return {"query": query, "keywords": keywords}

    def search_kg_triples(self, input_dict: Dict) -> Dict:
        query = input_dict["query"]
        keywords = input_dict["keywords"]

        kg_context = ""
        try:
            for kw in keywords:
                triples = self.kg_builder.search(kw)
                if triples:
                    kg_context += self.kg_builder.to_prompt_text(triples) + "\n"
        except Exception as e:
            kg_context = f"[KG search error] {e}"

        return {"query": query, "context": kg_context.strip()}

    def generate_response(self, input_dict: Dict) -> str:
        query = input_dict["query"]
        context = input_dict["context"]
        history = self.get_recent_context()

        full_context = "\n".join(filter(None, [context, history]))

        prompt = f"""You are a helpful assistant for the department faculty directory.
You have access to the following related facts from a knowledge graph:

{full_context}

Use these facts to improve the accuracy or depth of your answer if relevant — but feel free to include other general knowledge if needed. Do not hallucinate technical facts.

User: {query}
Bot:"""


        try:
            response = safe_generate_content(self.model, prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"[LLM Error] {e}"

        self.add_to_history(query, answer)
        return answer
