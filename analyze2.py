#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze steamrip.com HTML structure more deeply."""
import requests
from bs4 import BeautifulSoup

URL = "https://steamrip.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

response = requests.get(URL, headers=headers, timeout=15)

# Find div elements with 'card' in class
divs = response.find_all("div")
for d in divs:
    cls = d.get("class", [])
    if isinstance(cls, list) and any("card" in str(c).lower() for c in cls):
        print("=== Card div found ===")
        print("Classes:", cls)
        print("HTML:", str(d)[:2000])
        print()
        break

# Find the game list section more specifically
soup = BeautifulSoup(response.text, "lxml")
# Search for elements with 'list' or 'game' in their id or class
for tag in soup.find_all(True):  # all tags
    cls = tag.get("class", [])
    if isinstance(cls, list):
        cls_str = " ".join(cls).lower()
        if any(w in cls_str for w in ["game", "item", "poster", "product", "entry"]):
            print(f"=== Tag: {tag.name} classes: {cls} ===")
            print(str(tag)[:2000])
            print()
            break
