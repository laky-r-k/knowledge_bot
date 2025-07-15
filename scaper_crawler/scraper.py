import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from scraper_crawler.base import BaseScraper
import os
import time
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv

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

class MosdacScraper(BaseScraper):
    def __init__(self):
        self.visited = set()
        self.data: List[Tuple[str, str]] = []
        logger.info("Initialized MosdacScraper")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _fetch_url(self, url: str) -> str:
        """Fetch URL content with retries."""
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text

    def crawl(self, base_url: str, depth: int = None) -> List[Tuple[str, str]]:
        """Recursively crawl internal pages up to given depth."""
        depth = depth or int(os.getenv("CRAWL_DEPTH", 1))
        logger.info(f"Starting crawl at {base_url} with depth {depth}")
        self._crawl_recursive(base_url, base_url, 0, depth)
        return self.data

    def _crawl_recursive(self, current_url: str, base_url: str, curr_depth: int, max_depth: int):
        if current_url in self.visited or curr_depth > max_depth:
            return

        try:
            html = self._fetch_url(current_url)
            cleaned_text = self.extract_text(html)
            self.data.append((current_url, cleaned_text))
            self.visited.add(current_url)
            logger.info(f"✔ Crawled: {current_url}")

            soup = BeautifulSoup(html, "lxml")
            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    self._crawl_recursive(full_url, base_url, curr_depth + 1, max_depth)
            time.sleep(0.5)  # Polite crawling delay
        except Exception as e:
            logger.error(f"⚠ Failed to crawl {current_url}: {e}")

    def extract_text(self, html: str) -> str:
        """Extracts clean text from the HTML content."""
        logger.info("Extracting text from HTML")
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return text
        except Exception as e:
            logger.error(f"Text Extraction Error: {e}")
            return ""

    def save_output(self, output_path: str) -> None:
        """Save scraped (URL, text) data to a file."""
        logger.info(f"Saving output to {output_path}")
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                for url, content in self.data:
                    f.write(f"\n--- URL: {url} ---\n{content}\n")
            logger.info(f"📁 Output saved to {output_path}")
        except Exception as e:
            logger.error(f"Save Output Error: {e}")