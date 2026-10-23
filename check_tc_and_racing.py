import socket
import requests
from bs4 import BeautifulSoup
import sqlite3

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()
c.execute("SELECT slug FROM games")
existing_slugs = {row[0] for row in c.fetchall()}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://steamrip.com/'
}

candidate_slugs = [
    # Tom Clancy
    'tom-clancys-the-division-free-download',
    'tom-clancys-the-division-2-free-download',
    'the-division-free-download',
    'the-division-2-free-download',
    'tom-clancys-ghost-recon-breakpoint-free-download',
    'ghost-recon-breakpoint-free-download',
    'tom-clancys-rainbow-six-extraction-free-download',
    'rainbow-six-extraction-free-download',
    'tom-clancys-endwar-free-download',
    'tom-clancys-hawx-free-download',
    'tom-clancys-hawx-2-free-download',
    'tom-clancys-rainbow-six-lockdown-free-download',
    'tom-clancys-ghost-recon-advanced-warfighter-free-download',
    'tom-clancys-ghost-recon-advanced-warfighter-2-free-download',

    # Racing blockbusters
    'assetto-corsa-free-download',
    'assetto-corsa-competizione-free-download',
    'carx-drift-racing-online-free-download',
    'carx-street-free-download',
    'f1-23-free-download',
    'f1-22-free-download',
    'f1-2020-free-download',
    'dirt-rally-2-0-free-download',
    'dirt-5-free-download',
    'dirt-3-complete-edition-free-download',
    'project-cars-2-free-download',
    'project-cars-3-free-download',
    'ea-sports-wrc-free-download',
    'wrc-generations-free-download',
    'wrc-10-fia-world-rally-championship-free-download',
    'burnout-paradise-remastered-free-download',
    'grid-legends-free-download',
    'grid-2-free-download',
    'the-crew-2-free-download',
    'the-crew-motorfest-free-download',
    'need-for-speed-heat-deluxe-edition-free-download',
    'need-for-speed-payback-free-download',
    'need-for-speed-rivals-free-download',
    'need-for-speed-prostreet-free-download',
    'need-for-speed-underground-2-free-download',
    'need-for-speed-underground-free-download',
    'need-for-speed-shift-free-download',
    'shift-2-unleashed-free-download',
    'ride-4-free-download',
    'ride-5-free-download',
    'motogp-24-free-download',
    'motogp-23-free-download',
    'automobilista-2-free-download',
    'wreckfest-free-download',
    'flatout-2-free-download',
    'initial-drift-online-free-download'
]

valid_to_scrape = []
for s in candidate_slugs:
    # check if already in db
    base = s.rsplit('-', 1)[0]
    matched = [es for es in existing_slugs if es == s or es.startswith(base)]
    if matched:
        print(f"Already in DB: {s} -> {matched[:1]}")
    else:
        url = f"https://steamrip.com/{s}/"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                print(f"FOUND ON STEAMRIP & MISSING FROM DB: {s} (size: {len(r.text)})")
                valid_to_scrape.append((s, url))
            else:
                print(f"SteamRIP {r.status_code} for {s}")
        except Exception as e:
            print(f"Error {s}: {e}")

print(f"\nTotal new games to scrape: {len(valid_to_scrape)}")
for s, u in valid_to_scrape:
    print(f"  {s} -> {u}")
