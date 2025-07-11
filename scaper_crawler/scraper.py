import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from base import BaseScraper
import os
import time
from typing import List, Tuple

class MosdacScraper(BaseScraper):
    def __init__(self):
        self.visited = set()
        self.data: List[Tuple[str, str]] = []

    def crawl(self, base_url: str, depth: int = 1) -> List[Tuple[str, str]]:
        """Recursively crawl internal pages up to given depth."""
        self._crawl_recursive(base_url, base_url, 0, depth)
        return self.data

    def _crawl_recursive(self, current_url: str, base_url: str, curr_depth: int, max_depth: int):
        if current_url in self.visited or curr_depth > max_depth:
            return

        try:
            response = requests.get(current_url, timeout=5)
            if response.status_code != 200:
                return

            html = response.text
            cleaned_text = self.extract_text(html)
            self.data.append((current_url, cleaned_text))
            self.visited.add(current_url)
            print(f"✔ Crawled: {current_url}")

            soup = BeautifulSoup(html, "lxml")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link['href'])
                # Stay within the same domain
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    self._crawl_recursive(full_url, base_url, curr_depth + 1, max_depth)

            time.sleep(0.5)  # Polite crawling delay

        except Exception as e:
            print(f"⚠ Failed to crawl {current_url}: {e}")

    def extract_text(self, html: str) -> str:
        """Extracts clean text from the HTML content."""
        soup = BeautifulSoup(html, "lxml")

        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text

    def save_output(self, output_path: str):
        """Save scraped (URL, text) data to a file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for url, content in self.data:
                f.write(f"\n--- URL: {url} ---\n{content}\n")
        print(f"📁 Output saved to {output_path}")
# run_scraper.py



scraper = MosdacScraper()
scraper.crawl("https://www.mosdac.gov.in", depth=1)
scraper.save_output("data/mosdac_data.txt")
