#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze steamrip.com HTML structure for game cards."""
import requests
from bs4 import BeautifulSoup

URL = "https://steamrip.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.get(URL, headers=headers, timeout=15)
print("Status:", response.status_code)
print("Length:", len(response.text))

with open("C:/Users/Munib Raza/OneDrive/Desktop/streamrip/steamrip_home.html", "w", encoding="utf-8") as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, "lxml")

# Look for card-like elements
patterns = ["game-card", "game-item", "card", "item", "product", "clickable", "entry"]
for pattern in patterns:
    cards = soup.find_all(class_=pattern)
    if cards:
        print(f"\n=== Found {len(cards)} elements with class containing '{pattern}' ===")
        card = cards[0]
        print("--- First card HTML (first 1500 chars) ---")
        print(str(card)[:1500])
        print()

# Also try finding links that lead to game detail pages
print("\n=== Looking for game link patterns ===")
game_links = soup.find_all("a", href=True)
game_link_patterns = []
for a in game_links:
    href = a.get("href", "")
    text = a.get_text(strip=True)
    # Look for links that might be game links
    if any(word in text.lower() for word in ["free download", "build", "steam", "game"]) and len(text) > 3:
        game_link_patterns.append((text[:50], href[:80]))

print(f"Found {len(game_link_patterns)} potential game links")
for t, h in game_link_patterns[:10]:
    print(f"  Text: {t!r} | Href: {h!r}")

# Look for any img tags that might be game thumbnails
print("\n=== Sample image tags ===")
img_tags = soup.find_all("img", limit=10)
for img in img_tags:
    src = img.get("src", "")
    alt = img.get("alt", "")
    print(f"  src: {src[:100]} | alt: {alt[:80]}")

# Look for specific container with games list
print("\n=== Looking for game list containers ===")
for container in soup.find_all(["div", "article", "section"]):
    cls = container.get("class", [])
    if isinstance(cls, list) and len(cls) > 0:
        cls_str = " ".join(cls)
        if any(w in cls_str.lower() for w in ["game", "item", "card", "poster"]):
            print(f"  Container class: {cls_str[:100]}")
            print(f"  HTML start: {str(container)[:300]}")
            print()
            break
