from chat_bot.gemini_chatbot import GeminiChatBot
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

def run_cli(bot: GeminiChatBot):
    """Run the chatbot in a CLI loop."""
    logger.info("Starting CLI chatbot (no KG)")
    print("🤖 Ask anything about MOSDAC (type 'exit' to quit)")
    while True:
        query = input("🧑 You: ")
        if query.lower() in ["exit", "quit"]:
            logger.info("Exiting CLI chatbot")
            break
        response = bot.ask(query)
        print(f"🤖 Bot: {response['response']}")
        if response["status"] == "error":
            logger.error(f"Error in response: {response['response']}")

if __name__ == "__main__":
    bot = GeminiChatBot()
    run_cli(bot)