import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re
import time
from typing import List, Tuple

try:
    from scaper_crawler.base import BaseScraper
except ImportError:
    from base import BaseScraper


class FacultyScraper(BaseScraper):
    """Scraper optimized for BMSCE faculty profile pages.
    
    Extracts only meaningful faculty content (profile info, about,
    education, publications) while filtering out navigation bars,
    footers, and other website chrome.
    """

    def __init__(self):
        self.visited = set()
        self.data: List[Tuple[str, str]] = []

    def crawl(self, base_url: str, depth: int = 1) -> List[Tuple[str, str]]:
        """Crawl a single URL (kept for interface compatibility)."""
        html = self._fetch(base_url)
        if html:
            cleaned = self.extract_text(html)
            self.data.append((base_url, cleaned))
            self.visited.add(base_url)
        return self.data

    def crawl_list(self, urls: List[str]) -> List[Tuple[str, str]]:
        """Scrape each URL in the list and extract clean faculty content."""
        for url in urls:
            if url in self.visited:
                continue
            html = self._fetch(url)
            if html is None:
                continue

            cleaned = self.extract_text(html)
            if cleaned.strip():
                self.data.append((url, cleaned))
                self.visited.add(url)
                print(f"✔ Scraped: {url}")
            else:
                print(f"⚠ No faculty content found: {url}")

            time.sleep(0.5)

        return self.data

    def _fetch(self, url: str) -> str:
        """Fetch HTML from a URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠ Skipped (HTTP {response.status_code}): {url}")
        except Exception as e:
            print(f"⚠ Failed to fetch {url}: {e}")
        return None

    def extract_text(self, html: str) -> str:
        """Extract only faculty profile content from BMSCE HTML.
        
        Targets:
        1. Profile header (name, designation, qualification, email, research interests)
        2. h4 sections: About, Education, Selected Publications
        """
        soup = BeautifulSoup(html, "lxml")
        sections = []

        # --- 1. Profile header from div.col-md-9.order-2 ---
        profile_div = soup.find("div", class_=lambda c: c and "col-md-9" in c and "order-2" in c)
        if profile_div:
            name_tag = profile_div.find("h2")
            name = name_tag.get_text(strip=True) if name_tag else "Unknown"

            # Extract structured fields
            profile_text = profile_div.get_text(separator="\n", strip=True)
            sections.append(f"Name: {name}")

            # Parse designation, qualification, email, research interests
            lines = [l.strip() for l in profile_text.split("\n") if l.strip() and l.strip() != name]
            for line in lines:
                if "Research Interests:" in line:
                    sections.append(line)
                elif "@" in line:
                    sections.append(f"Email: {line}")
                elif line in ["Professor", "Associate Professor", "Assistant Professor"] or "Professor" in line or "HOD" in line:
                    sections.append(f"Designation: {line}")
                elif line in ["Ph.D.", "M.Tech.", "M.E.", "B.E.", "M.S."] or "Ph.D" in line:
                    sections.append(f"Qualification: {line}")

        # --- 2. h4 sections: About, Education, Selected Publications ---
        target_sections = ["About", "Education", "Selected Publications",
                           "Research", "Awards", "Patents", "Workshops"]

        for h4 in soup.find_all("h4"):
            title = h4.get_text(strip=True)
            if title not in target_sections:
                continue

            # Collect text from siblings until the next h4
            content_parts = []
            sibling = h4.find_next_sibling()
            while sibling and sibling.name != "h4":
                text = sibling.get_text(separator="\n", strip=True)
                if text:
                    content_parts.append(text)
                sibling = sibling.find_next_sibling()

            # If no siblings found, try parent's text minus the heading
            if not content_parts:
                parent = h4.parent
                if parent:
                    text = parent.get_text(separator="\n", strip=True)
                    text = text.replace(title, "", 1).strip()
                    if text:
                        content_parts.append(text)

            if content_parts:
                section_text = "\n".join(content_parts)
                sections.append(f"\n{title}:\n{section_text}")

        return "\n".join(sections)

    def save_output(self, output_dir: str):
        """Save each URL's scraped text to a separate file in output_dir."""
        os.makedirs(output_dir, exist_ok=True)

        for url, content in self.data:
            # Create filename from the faculty name in the URL
            slug = url.rstrip("/").split("/")[-1]
            # Clean the slug for use as filename
            filename = re.sub(r'[^a-zA-Z0-9_-]', '_', slug) + ".txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Source: {url}\n")
                f.write("=" * 60 + "\n\n")
                f.write(content)

            print(f"  📄 Saved: {filepath}")

        # Also save a combined file for the KG builder
        combined_path = os.path.join(output_dir, "_combined.txt")
        with open(combined_path, "w", encoding="utf-8") as f:
            for url, content in self.data:
                f.write(f"\n--- {url} ---\n{content}\n")

        print(f"  📁 Combined file: {combined_path}")


# ============================================================
# 🔗 FACULTY PAGE URLs
# ============================================================
FACULTY_URLS = [
    "https://bmsce.ac.in/home/facultyProfile/135/Dr-M-Dakshayini",
    "https://bmsce.ac.in/home/facultyProfile/156/Dr-Sandeep-Varma-N",
    "https://bmsce.ac.in/home/facultyProfile/28/Dr-Gowrishankar",
    "https://bmsce.ac.in/home/facultyProfile/438/Dr-Monika-Puttaramaiah",
]

if __name__ == "__main__":
    scraper = FacultyScraper()

    if FACULTY_URLS:
        scraper.crawl_list(FACULTY_URLS)
        scraper.save_output("data/faculty")
    else:
        print("⚠ No URLs in FACULTY_URLS list. Add your faculty page URLs and re-run.")
