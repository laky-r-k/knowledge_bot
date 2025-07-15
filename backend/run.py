from flask import Flask, render_template, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bot.chat_bot.gemini_chatbot import GeminiChatBot
from bot.kg_builder.kg_builder import SpaCyKGBuilder
from dotenv import load_dotenv
import os
import logging
import time

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

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize knowledge graph
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

@app.before_request
def before_request():
    """Initialize chatbot for each request."""
    try:
        g.bot = GeminiChatBot(kg_builder=kg)
        logger.info(f"Initialized chatbot for request from {request.remote_addr}")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")
        g.bot = None

@app.teardown_request
def teardown_request(exception=None):
    """Clean up chatbot instance."""
    if hasattr(g, 'bot'):
        g.pop('bot', None)

@app.route("/")
def index():
    """Serve the main chat interface."""
    logger.info(f"Serving index page to {request.remote_addr}")
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
@limiter.limit("10 per minute")
def ask():
    """Handle chat queries."""
    logger.info(f"Received API request to /api/ask from {request.remote_addr}")
    if not g.bot:
        logger.error("Chatbot not initialized")
        return jsonify({"response": "Service unavailable. Please try again later.", "status": "error", "suggestions": []}), 503
    try:
        if not request.is_json:
            logger.warning("Invalid JSON payload")
            return jsonify({"response": "Invalid request format.", "status": "error", "suggestions": []}), 400
        data = request.get_json()
        query = data.get("query", "").strip()
        if not query:
            logger.warning("Empty query received")
            return jsonify({"response": "Please enter a question.", "status": "error", "suggestions": []}), 400
        response = g.bot.ask(query)
        logger.info(f"Query processed: {query}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"API Error: {e}")
        return jsonify({"response": "Sorry, something went wrong. Please try again.", "status": "error", "suggestions": []}), 500

@app.route("/api/clear", methods=["POST"])
@limiter.limit("5 per minute")
def clear():
    """Clear chat history."""
    logger.info(f"Received API request to /api/clear from {request.remote_addr}")
    if not g.bot:
        logger.error("Chatbot not initialized")
        return jsonify({"response": "Service unavailable. Please try again later.", "status": "error"}), 503
    try:
        g.bot.clear_history()
        logger.info("Chat history cleared")
        return jsonify({"response": "Chat history cleared successfully.", "status": "success"})
    except Exception as e:
        logger.error(f"Clear History Error: {e}")
        return jsonify({"response": "Failed to clear chat history.", "status": "error"}), 500

@app.route("/api/feedback", methods=["POST"])
@limiter.limit("5 per minute")
def feedback():
    """Handle feedback submissions."""
    logger.info(f"Received API request to /api/feedback from {request.remote_addr}")
    try:
        if not request.is_json:
            logger.warning("Invalid JSON payload")
            return jsonify({"response": "Invalid request format.", "status": "error"}), 400
        data = request.get_json()
        feedback_text = data.get("feedback", "").strip()
        if not feedback_text:
            logger.warning("Empty feedback received")
            return jsonify({"response": "Please enter feedback.", "status": "error"}), 400
        feedback_path = "data/feedback.txt"
        os.makedirs(os.path.dirname(feedback_path), exist_ok=True)
        with open(feedback_path, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {request.remote_addr}: {feedback_text}\n")
        logger.info("Feedback saved successfully")
        return jsonify({"response": "Feedback submitted successfully!", "status": "success"})
    except Exception as e:
        logger.error(f"Feedback Error: {e}")
        return jsonify({"response": "Failed to submit feedback.", "status": "error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)