import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from new_scraper import SteamRipScraper

MISSING_SLUGS = [
    "the-outlast-trials-free-download-q1",
    "rematch-free-download",
    "pro-soccer-online-free-download-w1",
    "party-animals-free-download-1w",
    "sea-of-thieves-free-download",
    "dead-by-daylight-free-download-n1",
    "test-drive-unlimited-solar-crown-free-download",
]

scraper = SteamRipScraper(
    db_path=Path("backend/games.db"),
    posters_dir=Path("posters"),
    download_posters=True,
)

for slug in MISSING_SLUGS:
    url = f"https://steamrip.com/{slug}/"
    print(f"\nScraping mirrors for {slug}...")
    try:
        detail = scraper.parse_detail_page(url)
        if detail and detail.get("files"):
            print(f"Found {len(detail['files'])} mirrors for {slug}!")
            scraper.save_game({"slug": slug, "title": detail.get("title") or slug, "detail_url": url}, detail)
        else:
            # Check if slug redirects or has alternative
            print(f"No direct mirrors on {url}, checking without suffix...")
            base = slug.rsplit('-', 1)[0]
            alt_url = f"https://steamrip.com/{base}/"
            detail = scraper.parse_detail_page(alt_url)
            if detail and detail.get("files"):
                print(f"Found {len(detail['files'])} mirrors on {alt_url}!")
                scraper.save_game({"slug": slug, "title": detail.get("title") or slug, "detail_url": alt_url}, detail)
            else:
                print(f"No mirrors found on alternative {alt_url}")
    except Exception as e:
        print(f"Error {slug}: {e}")
