from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def crawl(self, base_url: str, depth: int = 1):
        """Crawl internal pages up to given depth"""
        pass

    @abstractmethod
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML"""
        pass

    @abstractmethod
    def save_output(self, output_path: str):
        """Save scraped content to a file or DB"""
        pass
