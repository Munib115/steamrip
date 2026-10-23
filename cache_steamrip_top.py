import socket
import requests
from bs4 import BeautifulSoup
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://steamrip.com/',
}

all_top_slugs = []
seen = set()

for p in range(1, 20):
    url = f'https://steamrip.com/top-games/page/{p}/' if p > 1 else 'https://steamrip.com/top-games/'
    success = False
    for attempt in range(4):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 404:
                print(f"Reached end of top-games at page {p}")
                break
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                cards = soup.find_all('li', class_='post-item') or soup.find_all('article')
                if not cards:
                    break
                for card in cards:
                    a = card.find('a', href=True)
                    if a and '-free-download' in a['href']:
                        slug = a['href'].strip('/').split('/')[-1]
                        if slug not in seen:
                            seen.add(slug)
                            all_top_slugs.append(slug)
                print(f"Page {p}: collected {len(cards)} cards (total unique: {len(all_top_slugs)})")
                success = True
                break
        except Exception as e:
            time.sleep(1.5)
    if not success and p > 1:
        break

print(f"\nTotal top games collected from SteamRIP: {len(all_top_slugs)}")
with open('steamrip_top_games.json', 'w') as f:
    json.dump(all_top_slugs, f, indent=2)
print("Saved to steamrip_top_games.json")
