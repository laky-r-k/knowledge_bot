"""Extract faculty profile content by targeting h4 sections."""
import requests
from bs4 import BeautifulSoup

html = requests.get('https://bmsce.ac.in/home/facultyProfile/135/Dr-M-Dakshayini', timeout=10).text
soup = BeautifulSoup(html, 'lxml')

# 1. Profile header — div with class col-md-9 order-2
profile = soup.find('div', class_='col-md-9 order-2'.split())
if profile:
    print("=== PROFILE ===")
    print(profile.get_text(separator='\n', strip=True))
    print()

# 2. Content under h4 tags (About, Education, Selected Publications)
for h4 in soup.find_all('h4'):
    title = h4.get_text(strip=True)
    if title in ['About', 'Education', 'Selected Publications']:
        print(f"=== {title.upper()} ===")
        # Get the next sibling elements until next h4
        sibling = h4.find_next_sibling()
        while sibling and sibling.name != 'h4':
            text = sibling.get_text(separator='\n', strip=True)
            if text:
                print(text)
            sibling = sibling.find_next_sibling()
        # If no siblings, try parent's next content
        if not h4.find_next_sibling():
            parent = h4.parent
            text = parent.get_text(separator='\n', strip=True)
            # Remove the heading itself
            text = text.replace(title, '', 1).strip()
            if text:
                print(text)
        print()
