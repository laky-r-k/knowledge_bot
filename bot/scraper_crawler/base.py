from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    @abstractmethod
    def crawl(self, base_url: str, depth: int = 1) -> List[Tuple[str, str]]:
        """Crawl internal pages up to given depth."""
        pass

    @abstractmethod
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        pass

    @abstractmethod
    def save_output(self, output_path: str) -> None:
        """Save scraped content to a file or DB."""
        pass