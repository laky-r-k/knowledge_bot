import os
from bot.scraper_crawler.scraper import MosdacScraper
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
    data = scraper.crawl("https://www.mosdac.gov.in")
    output_path = os.getenv("SCRAPER_OUTPUT_PATH", "data/mosdac_data.txt")
    scraper.save_output(output_path)
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        logger.info("Scraper completed successfully")
    else:
        logger.error("Scraper failed to produce valid output")
        raise RuntimeError("No valid data scraped. Check logs for errors.")