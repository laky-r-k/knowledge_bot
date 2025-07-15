from bot.chat_bot.gemini_chatbot import GeminiChatBot
from bot.kg_builder.kg_builder import SpaCyKGBuilder
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

def main():
    logger.info("Starting chatbot")
    kg = SpaCyKGBuilder()
    graph_path = "data/kg_graph.gpickle"
    data_path = os.getenv("SCRAPER_OUTPUT_PATH", "data/mosdac_data.txt")

    if os.path.exists(graph_path):
        kg.load_graph(graph_path)
        logger.info("Loaded existing knowledge graph")
    else:
        if not os.path.exists(data_path):
            logger.error(f"Data file {data_path} not found. Run run_scraper.py first.")
            raise FileNotFoundError(f"Data file {data_path} not found")
        with open(data_path, "r", encoding="utf-8") as f:
            text = f.read()
        triples = kg.extract_triples(text)
        kg.build_graph(triples)

    bot = GeminiChatBot(kg_builder=kg)
    logger.info("Chatbot initialized. Type 'exit' to quit.")

    while True:
        query = input("You: ").strip()
        if query.lower() == "exit":
            logger.info("Exiting chatbot")
            break
        try:
            response = bot.ask(query)
            print(f"MOSDAC Bot: {response['response']}")
            if response["suggestions"]:
                print("Suggestions:", ", ".join(response["suggestions"]))
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print("Sorry, something went wrong. Please try again.")

if __name__ == "__main__":
    main()