# chatbot/gemini_chatbot.py

import google.generativeai as genai
from chat_bot.base import CHATBOT
from chat_bot.CONFIG.config import GEMINI_API_KEY
from typing import Optional

class GeminiChatBot(CHATBOT):
    def __init__(self, model_name: str = "models/gemini-1.5-flash", kg_builder: Optional[object] = None):
        super().__init__()
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.kg_builder = kg_builder  # Pass your KG builder from outside

    def ask(self, query: str, context: str = "", use_kg: bool = True) -> str:
        """
        Answer a query using:
        - optional KG search
        - chat memory (context)
        - Gemini LLM for response
        """
        kg_context = ""
        if use_kg and self.kg_builder:
            try:
                triples = self.kg_builder.search(query)
                kg_context = self.kg_builder.to_prompt_text(triples)
            except Exception as e:
                kg_context = f"[KG Error] {e}"
        print("these are facts from knowlege graph just to show you :",kg_context)
        # Get chat history (if context isn't passed explicitly)
        chat_context = context or self.get_recent_context()
        combined_context = f"{kg_context}\n{chat_context}".strip()

        prompt = f"""
Use the following information for more detailed and specific answering:

{combined_context}

User: {query}
Bot:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"[LLM Error] {e}"

        self.add_to_history(query, answer)
        return answer
    
