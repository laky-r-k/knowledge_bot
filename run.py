from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__, template_folder="web/templates", static_folder="web/static")
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize knowledge graph and chatbot
logger.info("Starting chatbot setup")
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

@app.route("/")
def index():
    """Serve the main chat interface."""
    logger.info("Serving index page")
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
def ask():
    """Handle chat queries."""
    logger.info("Received API request to /api/ask")
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        if not query:
            logger.warning("Empty query received")
            return jsonify({"response": "Please enter a query.", "status": "error"}), 400
        response = bot.ask(query)
        logger.info(f"Query processed: {query}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({"response": f"[API Error] {e}", "status": "error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)