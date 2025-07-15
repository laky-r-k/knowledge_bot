import os
from scraper_crawler.scraper import MosdacScraper
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

if __name__ == "__main__":
    logger.info("Starting scraper")
    scraper = MosdacScraper()
    scraper.crawl("https://www.mosdac.gov.in")
    output_path = os.getenv("SCRAPER_OUTPUT_PATH", "data/mosdac_data.txt")
    scraper.save_output(output_path)
    logger.info("Scraper completed")