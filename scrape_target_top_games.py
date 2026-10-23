import os
import sys
from pathlib import Path

# Add streamrip root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from new_scraper import SteamRipScraper

TARGET_URLS = [
    "https://steamrip.com/cyberpunk-2077-free-download/",
    "https://steamrip.com/grand-theft-auto-iv-free-download/",
    "https://steamrip.com/red-dead-redemption-free-download/",
    "https://steamrip.com/marvels-spider-man-remastered-free-download/",
    "https://steamrip.com/god-of-war-free-download/",
    "https://steamrip.com/horizon-zero-dawn-complete-edition-free-download/",
    "https://steamrip.com/horizon-forbidden-west-complete-edition-free-download/",
    "https://steamrip.com/dying-light-2-stay-human-free-download/",
]

def main():
    db_path = Path("backend/games.db")
    posters_dir = Path("posters")
    backend_posters = Path("backend/posters")
    posters_dir.mkdir(parents=True, exist_ok=True)
    backend_posters.mkdir(parents=True, exist_ok=True)

    scraper = SteamRipScraper(
        db_path=db_path,
        posters_dir=posters_dir,
        download_posters=True,
        workers=4,
    )

    print(f"Scraping {len(TARGET_URLS)} targeted top blockbuster games...")
    for url in TARGET_URLS:
        slug = url.strip("/").split("/")[-1]
        print(f"\n---> Scraping {slug} ({url}) ...")
        try:
            detail = scraper.parse_detail_page(url)
            if not detail:
                print(f"Failed to parse {url}")
                continue

            game_data = {
                "title": detail.get("title") or slug.replace("-", " ").title(),
                "slug": slug,
                "detail_url": url,
                "card_poster_url": detail.get("poster_url"),
                "file_size": detail.get("file_size"),
                "category": detail.get("category"),
                "genres": detail.get("genres"),
            }

            game_id = scraper.save_game(game_data, detail)
            print(f"Successfully saved game ID {game_id}: {game_data['title']}")
            print(f"  Mirrors found: {len(detail.get('files', []))}")
            print(f"  Category: {detail.get('category')} | Size: {detail.get('file_size')}")

            # Also ensure poster is mirrored to backend/posters
            src_poster = posters_dir / f"{slug}.jpg"
            dst_poster = backend_posters / f"{slug}.jpg"
            if src_poster.exists():
                dst_poster.write_bytes(src_poster.read_bytes())
                print(f"  Poster copied: {src_poster} -> {dst_poster} ({src_poster.stat().st_size} bytes)")
            else:
                print(f"  Warning: poster not found at {src_poster}")

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
