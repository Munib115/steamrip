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
soup = BeautifulSoup(response.text, "lxml")

# Find the game list section more specifically
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
