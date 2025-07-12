# run_bot.py

from chat_bot.gemini_chatbot import GeminiChatBot

bot = GeminiChatBot()


while True:
    query = input("🧑 You: ")
    if query.lower() in ["exit", "quit"]:
        break
    response = bot.ask(query)
    print("🤖 Bot:", response)
