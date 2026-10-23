import requests
import socket
import urllib3.util.connection
import sqlite3
import re
from bs4 import BeautifulSoup

urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()
c.execute('SELECT slug FROM games')
existing_slugs = set(r[0].lower().strip('/') for r in c.fetchall())

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

queries = [
    'naruto', 'ninja storm', 'shinobi striker', 'dragon ball', 'kakarot',
    'one piece', 'pirate warriors', 'burning blood',
    'demon slayer', 'jujutsu kaisen', 'attack on titan', 'jojo',
    'sword art online', 'fatal bullet', 'persona', 'metaphor',
    'granblue', 'guilty gear', 'blazblue', 'my hero', 'one justice',
    'fate', 'tokyo ghoul', 'berserk', 'danganronpa', 'tales of',
    'chainsaw', 'hunter x hunter', 'fairy tail', 'digimon', 'jump force'
]

keywords = [
    'naruto', 'storm', 'dragon', 'ball', 'piece', 'slayer', 'jujutsu', 'titan',
    'jojo', 'sword art', 'persona', 'granblue', 'guilty', 'blazblue', 'hero',
    'fate', 'ghoul', 'berserk', 'danganronpa', 'tales', 'fairy', 'digimon',
    'jump force', 'kakarot', 'anime', 'metaphor', 'shinobi', 'boruto'
]

missing = []

for q in queries:
    url = f"https://steamrip.com/?s={requests.utils.quote(q)}"
    try:
        r = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '-free-download' in href:
                slug = href.strip('/').split('/')[-1]
                title = a.get_text(strip=True)
                if slug and slug not in existing_slugs and not any(m['slug'] == slug for m in missing):
                    if any(k in title.lower() for k in keywords):
                        missing.append({'title': title, 'slug': slug, 'url': f"https://steamrip.com/{slug}/"})
                        print(f"Found missing: {title} ({slug})")
    except Exception as e:
        print(f"Error searching {q}: {e}")

print(f"\nTotal missing anime titles found: {len(missing)}")
with open('missing_anime.json', 'w', encoding='utf-8') as f:
    import json
    json.dump(missing, f, indent=2)
