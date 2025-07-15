from chat_bot.gemini_chatbot import GeminiChatBot
from kg_builder.kg_builder import SpaCyKGBuilder
from dotenv import load_dotenv
import os
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

def run_cli(bot: GeminiChatBot):
    """Run the chatbot in a CLI loop."""
    logger.info("Starting CLI chatbot with KG")
    print("🤖 Ask anything about satellites or MOSDAC (type 'exit' to quit)")
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
    logger.info("Starting chatbot setup")
    # Step 1: Load and build the Knowledge Graph
    kg = SpaCyKGBuilder()
    graph_path = "data/kg_graph.gpickle"
    if os.path.exists(graph_path):
        kg.load_graph(graph_path)
        logger.info("Loaded existing knowledge graph")
    else:
        data_path = os.getenv("SCRAPER_OUTPUT_PATH", "data/mosdac_data.txt")
        if not os.path.exists(data_path):
            logger.error(f"Data file {data_path} not found")
            raise FileNotFoundError(f"Data file {data_path} not found")
        with open(data_path, "r", encoding="utf-8") as f:
            text = f.read()
        triples = kg.extract_triples(text)
        kg.build_graph(triples)

    # Step 2: Initialize chatbot with the KG
    bot = GeminiChatBot(kg_builder=kg)

    # Step 3: Run CLI loop
    run_cli(bot)