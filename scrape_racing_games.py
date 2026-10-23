import requests
from bs4 import BeautifulSoup
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from new_scraper import SteamRipScraper

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://steamrip.com/'
}

conn = sqlite3.connect('backend/games.db')
c = conn.cursor()
c.execute("SELECT slug FROM games")
existing_slugs = {row[0] for row in c.fetchall()}

scraper = SteamRipScraper(
    db_path=Path("backend/games.db"),
    posters_dir=Path("posters"),
    download_posters=True,
)

# 1. Scrape NFS Heat directly
nfs_heat_url = "https://steamrip.com/need-for-speed-heat-deluxe-edition-free-download/"
print(f"Scraping NFS Heat Deluxe Edition...")
try:
    detail = scraper.parse_detail_page(nfs_heat_url)
    if detail:
        gid = scraper.save_game({
            "title": "Need for Speed Heat Deluxe Edition Free Download",
            "slug": "need-for-speed-heat-deluxe-edition-free-download",
            "detail_url": nfs_heat_url,
            "category": "Racing",
            "genres": "Racing, Open World"
        }, detail)
        print(f"Saved NFS Heat ID {gid} with {len(detail.get('files', []))} mirrors!")
        
        # copy poster to backend/posters
        p1 = Path("posters/need-for-speed-heat-deluxe-edition-free-download.jpg")
        p2 = Path("backend/posters/need-for-speed-heat-deluxe-edition-free-download.jpg")
        if p1.exists():
            p2.write_bytes(p1.read_bytes())
except Exception as e:
    print(f"Error scraping NFS Heat: {e}")

# 2. Scrape category/racing on SteamRIP
missing_racing = []
for p in range(1, 10):
    url = f"https://steamrip.com/category/racing/page/{p}/" if p > 1 else "https://steamrip.com/category/racing/"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"Ended racing category at page {p}")
            break
        soup = BeautifulSoup(r.text, 'html.parser')
        cards = soup.find_all('li', class_='post-item') or soup.find_all('article')
        if not cards:
            break
        print(f"Racing Page {p}: found {len(cards)} cards")
        for card in cards:
            a = card.find('a', href=True)
            if a and '-free-download' in a['href']:
                href = a['href']
                slug = href.strip('/').split('/')[-1]
                base = slug.rsplit('-', 1)[0]
                matched = [es for es in existing_slugs if es == slug or es.startswith(base)]
                if not matched:
                    title_el = card.find(['h2', 'h1']) or a
                    title = title_el.get_text(strip=True)
                    missing_racing.append((slug, href, title))
    except Exception as e:
        print(f"Error page {p}: {e}")
        break

print(f"\nTotal missing racing games found: {len(missing_racing)}")
for s, h, t in missing_racing:
    print(f"  Scraping: {s} -> {t[:40]} ...")
    try:
        detail = scraper.parse_detail_page(h)
        if detail:
            gid = scraper.save_game({
                "title": t,
                "slug": s,
                "detail_url": h,
                "category": "Racing",
                "genres": "Racing"
            }, detail)
            print(f"    Saved game ID {gid} with {len(detail.get('files', []))} mirrors")
            p1 = Path(f"posters/{s}.jpg")
            p2 = Path(f"backend/posters/{s}.jpg")
            if p1.exists():
                p2.write_bytes(p1.read_bytes())
    except Exception as e:
        print(f"    Failed {s}: {e}")

print("Racing scraper complete!")
