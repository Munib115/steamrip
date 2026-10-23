#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze steamrip.com HTML structure - focused on game cards."""
import sys
import requests
from bs4 import BeautifulSoup

# Fix for Unicode output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

URL = "https://steamrip.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.get(URL, headers=headers, timeout=15)
soup = BeautifulSoup(response.text, "lxml")

# Find all links that look like game links (contain 'free-download' or similar patterns)
# These would be game detail page links
game_link_patterns = []
for a in soup.find_all("a", href=True):
    href = a.get("href", "")
    text = a.get_text(strip=True)
    # Look for links that might be game links
    if ("download" in href.lower() or "game" in href.lower()) and len(text) > 5:
        game_link_patterns.append((text[:60], href[:100]))

print(f"Found {len(game_link_patterns)} potential game links")
for t, h in game_link_patterns[:20]:
    print(f"  Text: {t!r}")
    print(f"  Href: {h!r}")
    print()

# Now find the actual game card structure
# Look for elements containing multiple game-related items
print("\n\n=== Looking for game cards with images ===")
# Find all elements that have both img and link
for img in soup.find_all("img"):
    parent = img.find_parent(class_="game") or img.find_parent(class_="item") or img.find_parent(class_="card")
    if parent:
        print(f"=== Found game card with img ===")
        print(f"Parent classes: {parent.get('class', [])}")
        print(f"Parent HTML: {str(parent)[:2000]}")
        print()

# Also look for the specific structure of game items in the all-games page
print("\n\n=== Looking at games-list page ===")
resp2 = requests.get("https://steamrip.com/games-list/", headers=headers, timeout=15)
soup2 = BeautifulSoup(resp2.text, "lxml")

# Find game card items
for tag in soup2.find_all(True):
    cls = tag.get("class", [])
    if isinstance(cls, list):
        cls_str = " ".join(cls)
        if any(w in cls_str.lower() for w in ["game", "item", "poster", "product"]):
            # Check if it contains an img or link
            if tag.find("img") or tag.find("a"):
                print(f"=== Tag: {tag.name} classes: {cls} ===")
                print(str(tag)[:2500])
                print()

