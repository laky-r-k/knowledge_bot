import google.generativeai as genai

# ✅ Paste your actual API key here
API_KEY = ""

# ✅ Configure Gemini
genai.configure(api_key=API_KEY)

# ✅ Use correct full model name
model = genai.GenerativeModel("models/gemini-pro")

def ask_llm(question, context=""):
    prompt = f"""Answer the question using the following context:

{context}

Question: {question}
Answer:"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[LLM Error] {e}"
