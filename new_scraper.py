#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SteamRip Scraper & Poster Downloader.

Scrapes games, descriptions, file sizes, system requirements, download mirrors,
and high-resolution poster images from https://steamrip.com/ into the SQLite
database (backend/games.db) and downloads game posters locally into the posters/ directory.

Usage:
    python new_scraper.py                     # Scrape first 3 pages and download posters
    python new_scraper.py --pages 5           # Scrape first 5 pages
    python new_scraper.py --start-page 2      # Continue from page 2
    python new_scraper.py --limit 10          # Scrape up to 10 games
    python new_scraper.py --from-list         # Scrape from the complete games list
    python new_scraper.py --no-posters        # Scrape metadata only (don't save poster files)
"""

import argparse
import os
import re
import socket
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import urllib3.util.connection

# Force IPv4 resolution on Windows to avoid Errno 11002 getaddrinfo failures
urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET

import requests
from bs4 import BeautifulSoup

# Base paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
DEFAULT_DB_PATH = BACKEND_DIR / "games.db"
DEFAULT_POSTERS_DIR = ROOT_DIR / "posters"
BACKEND_POSTERS_DIR = BACKEND_DIR / "posters"

BASE_URL = "https://steamrip.com/"
GAMES_LIST_URL = "https://steamrip.com/games-list/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://steamrip.com/",
}

BLANK_IMAGE_PLACEHOLDERS = (
    "data:image/png;base64",
    "data:image/gif;base64",
    "data:image/svg+xml",
)


def slugify(text: str) -> str:
    """Normalize text into an alphanumeric slug."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


def clean_title(title: str) -> str:
    """Clean extra spaces and trailing punctuation from game title."""
    if not title:
        return ""
    title = re.sub(r"\s+", " ", title).strip()
    return title


def extract_mirror_label(url: str, default_label: str = "Download") -> str:
    """Extract a user-friendly mirror name from a download URL."""
    domain = urlparse(url).netloc.lower()
    if "bzzhr" in domain or "buzzheavier" in domain:
        return "Buzzheavier"
    if "fileditch" in domain:
        return "FileDitch"
    if "mega.nz" in domain or "mega.co" in domain:
        return "Mega"
    if "gofile" in domain:
        return "GoFile"
    if "qiwi" in domain:
        return "Qiwi"
    if "1fichier" in domain:
        return "1Fichier"
    if "pixeldrain" in domain:
        return "PixelDrain"
    if "megadb" in domain:
        return "MegaDB"
    if "torrent" in url.lower():
        return "Torrent"
    if default_label and default_label.lower() != "download here":
        return default_label
    return "Direct Download"


class SteamRipScraper:
    """Robust scraper for SteamRip games and posters."""

    def __init__(
        self,
        db_path: Path = DEFAULT_DB_PATH,
        posters_dir: Path = DEFAULT_POSTERS_DIR,
        download_posters: bool = True,
        delay: float = 0.5,
        workers: int = 6,
    ) -> None:
        self.db_path = Path(db_path)
        self.posters_dir = Path(posters_dir)
        self.download_posters = download_posters
        self.delay = delay
        self.workers = workers
        self.db_lock = threading.Lock()

        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.download_posters:
            self.posters_dir.mkdir(parents=True, exist_ok=True)
            BACKEND_POSTERS_DIR.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=3)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.init_db()

    def init_db(self) -> None:
        """Create database tables if they do not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                requirements TEXT,
                download_url TEXT,
                direct_file_url TEXT,
                thumbnail_url TEXT,
                file_size VARCHAR(64),
                source_url TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_games_slug ON games (slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_games_title ON games (title)")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS game_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                label VARCHAR(128),
                url TEXT NOT NULL,
                file_type VARCHAR(32),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_game_files_game_id ON game_files (game_id)")
        
        # Ensure category and genres columns exist
        try:
            cursor.execute("ALTER TABLE games ADD COLUMN category VARCHAR(64)")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE games ADD COLUMN genres VARCHAR(255)")
        except Exception:
            pass
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_games_category ON games (category)")

        conn.commit()
        conn.close()

    def get_existing_slugs(self) -> set[str]:
        """Return a set of slugs already stored in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT slug FROM games")
        rows = cursor.fetchall()
        conn.close()
        return {r[0] for r in rows}

    def fetch_url(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Fetch a URL politely with retry and exponential backoff."""
        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 200:
                    time.sleep(self.delay)
                    return resp
                if resp.status_code == 404:
                    print(f"  [404 Not Found] {url}")
                    return None
                print(f"  [HTTP {resp.status_code}] Retrying {url} ({attempt}/{max_retries})...")
            except Exception as exc:
                print(f"  [Error] {exc}. Retrying {url} ({attempt}/{max_retries})...")
            time.sleep(attempt * 1.5)
        return None

    def download_poster_image(self, poster_url: str, slug: str) -> Optional[str]:
        """Download poster image and save locally as {slug}.jpg.
        
        Returns relative URL path (/posters/{slug}.jpg) or None if download fails.
        """
        if not self.download_posters or not poster_url:
            return None

        # Determine extension from url or default to .jpg
        parsed = urlparse(poster_url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            ext = ".jpg"

        filename = f"{slug}{ext}"
        primary_file = self.posters_dir / filename
        backend_file = BACKEND_POSTERS_DIR / filename

        # If already downloaded and non-empty, reuse it
        if primary_file.exists() and primary_file.stat().st_size > 1024:
            if not backend_file.exists() or backend_file.stat().st_size != primary_file.stat().st_size:
                try:
                    backend_file.write_bytes(primary_file.read_bytes())
                except Exception:
                    pass
            return f"/posters/{filename}"

        # Fetch image bytes
        for attempt in range(1, 4):
            try:
                resp = self.session.get(poster_url, timeout=15)
                if resp.status_code == 200 and len(resp.content) > 500:
                    primary_file.write_bytes(resp.content)
                    try:
                        backend_file.write_bytes(resp.content)
                    except Exception:
                        pass
                    return f"/posters/{filename}"
            except Exception as e:
                time.sleep(attempt * 1.0)

        return None

    def parse_card_poster(self, card_soup: BeautifulSoup) -> Optional[str]:
        """Extract high-resolution poster URL from a game card."""
        img = card_soup.find("img")
        if not img:
            return None

        # Check data-src, data-lazy-src, data-original
        for attr in ["data-src", "data-lazy-src", "data-original", "data-url"]:
            src = img.get(attr)
            if src and not any(src.startswith(b) for b in BLANK_IMAGE_PLACEHOLDERS):
                return urljoin(BASE_URL, src)

        # Check noscript tag
        noscript = card_soup.find("noscript")
        if noscript:
            ns_soup = BeautifulSoup(noscript.string or str(noscript), "lxml")
            ns_img = ns_soup.find("img")
            if ns_img and ns_img.get("src"):
                src = ns_img["src"]
                if not any(src.startswith(b) for b in BLANK_IMAGE_PLACEHOLDERS):
                    return urljoin(BASE_URL, src)

        # Fallback to direct src if not placeholder
        src = img.get("src")
        if src and not any(src.startswith(b) for b in BLANK_IMAGE_PLACEHOLDERS):
            return urljoin(BASE_URL, src)

        return None

    def parse_detail_page(self, url: str) -> Dict[str, Any]:
        """Fetch and extract complete details from a game's detail page."""
        resp = self.fetch_url(url)
        if not resp:
            return {}

        soup = BeautifulSoup(resp.text, "lxml")
        data: Dict[str, Any] = {
            "poster_url": None,
            "description": None,
            "requirements": None,
            "files": [],
        }

        # 1. Poster from meta tag or main image
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            data["poster_url"] = og_img["content"]

        entry = soup.find("div", class_="entry-content") or soup.find("article")
        if not entry:
            return data

        # 2. Extract description & system requirements
        description_paragraphs: List[str] = []
        requirements_text = ""

        for p in entry.find_all(["p", "div"]):
            txt = p.get_text(strip=True)
            if not txt:
                continue

            # Identify system requirements
            if any(k in txt.upper() for k in ["SYSTEM REQUIREMENTS", "MINIMUM:", "RECOMMENDED:"]):
                # Often in the text or child elements
                requirements_text = txt
                continue
            if ("OS:" in txt or "PROCESSOR:" in txt.upper() or "GRAPHICS:" in txt.upper()) and not requirements_text:
                requirements_text = txt
                continue

            # Skip banners, screenshot labels, download prompts
            if any(
                skip in txt.upper()
                for skip in [
                    "SCREENSHOTS",
                    "CLICK THE DOWNLOAD",
                    "HAVE FUN AND PLAY",
                    "NOTICE:",
                    "DOWNLOAD HERE",
                    "FREE DOWNLOAD",
                ]
            ):
                continue

            if len(txt) > 30 and len(description_paragraphs) < 4:
                description_paragraphs.append(txt)

        data["description"] = "\n\n".join(description_paragraphs) if description_paragraphs else None
        data["requirements"] = requirements_text if requirements_text else None

        # 3. Extract download buttons and mirror links
        seen_links = set()
        for a in entry.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_href = urljoin(url, href)
            # Ensure protocol
            if full_href.startswith("//"):
                full_href = "https:" + full_href

            classes = " ".join(a.get("class", []))
            link_text = clean_title(a.get_text(strip=True))

            # Exclude internal steamrip links from download mirrors
            if "steamrip.com" in full_href.lower():
                continue

            # Match steamrip download buttons and known file hosts
            is_download = (
                any(
                    host in full_href.lower()
                    for host in [
                        "buzzheavier",
                        "bzzhr",
                        "fileditch",
                        "mega.nz",
                        "gofile.io",
                        "qiwi",
                        "1fichier",
                        "pixeldrain",
                        "megadb",
                        "filecrypt",
                        "datanodes",
                        "vikingfile",
                    ]
                )
                or (
                    ("shortc-button" in classes or "btn-download" in classes)
                    and not any(x in full_href for x in ["/faq", "/how-to-download", "/contact", "/requests", "/steps-for-games", "discord.gg", "reddit.com"])
                )
            )

            # Avoid internal wiki / faq / blog links
            if (
                is_download
                and full_href not in seen_links
                and not any(x in full_href for x in ["/faq", "/how-to-download", "/contact", "/requests", "/steps-for-games"])
            ):
                seen_links.add(full_href)
                label = extract_mirror_label(full_href, link_text)
                data["files"].append({"label": label, "url": full_href, "file_type": "direct"})

        # 4. Extract category & genres from detail page post-cat tags
        post_cats = soup.find_all(class_="post-cat")
        if post_cats:
            cat_names = [clean_title(c.get_text(strip=True)) for c in post_cats if c.get_text(strip=True)]
            if cat_names:
                data["category"] = cat_names[0]
                data["genres"] = ", ".join(cat_names)

        # 5. Extract file size if mentioned in page storage specifications
        page_text = entry.get_text() if entry else soup.get_text()
        storage_match = re.search(r"Storage:\s*(\d+(?:\.\d+)?\s*(?:GB|MB|TB))", page_text, re.I)
        if storage_match:
            data["file_size"] = storage_match.group(1).strip()

        return data

    def parse_listing_page(self, page_num: int = 1) -> Tuple[List[Dict[str, Any]], bool]:
        """Scrape game cards from a listing page.
        
        Returns (list_of_game_stubs, has_next_page).
        """
        page_url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
        print(f"\n[Page {page_num}] Fetching {page_url} ...")
        resp = self.fetch_url(page_url)
        if not resp:
            return [], False

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.find_all("li", class_="post-item")
        if not cards:
            cards = soup.find_all("article", class_="post")

        games: List[Dict[str, Any]] = []
        for card in cards:
            # 1. Detail URL
            link = card.find("a", href=True)
            if not link:
                continue
            detail_url = urljoin(BASE_URL, link["href"])
            # Remove trailing slash for clean slug
            slug = link["href"].strip("/").split("/")[-1]
            if not slug:
                continue

            # 2. Title
            title_el = card.find("h2", class_="post-title") or card.find("h2", class_="the-post-title")
            title = clean_title(title_el.get_text(strip=True)) if title_el else slug.replace("-", " ").title()

            # 3. Category & Genres
            cat_el = card.find(class_="post-cat")
            primary_cat = clean_title(cat_el.get_text(strip=True)) if cat_el else None
            card_classes = card.get("class", [])
            genres_list = [c.replace("category-", "") for c in card_classes if c.startswith("category-")]
            genres = ", ".join(genres_list) if genres_list else None

            # 4. Poster URL from card
            poster_url = self.parse_card_poster(card)

            # 5. Meta line (Year | Size)
            meta_line = card.find(class_="game-meta-line")
            file_size = None
            if meta_line:
                meta_txt = meta_line.get_text(strip=True)
                # Formats like "2026 | 8.2 GB"
                if "|" in meta_txt:
                    parts = [p.strip() for p in meta_txt.split("|")]
                    for part in parts:
                        if any(unit in part.upper() for unit in ["MB", "GB", "KB", "TB"]):
                            file_size = part
                elif any(unit in meta_txt.upper() for unit in ["MB", "GB", "KB", "TB"]):
                    file_size = meta_txt

            games.append(
                {
                    "title": title,
                    "slug": slug,
                    "detail_url": detail_url,
                    "card_poster_url": poster_url,
                    "file_size": file_size,
                    "category": primary_cat,
                    "genres": genres,
                }
            )

        # Check if next page exists
        next_button = soup.find("a", class_=lambda c: c and "next" in c.lower())
        has_next = bool(next_button or len(cards) >= 15)
        return games, has_next

    def parse_games_list_index(self) -> List[Dict[str, Any]]:
        """Scrape all games from https://steamrip.com/games-list/."""
        print(f"\n[Index] Fetching full games list: {GAMES_LIST_URL} ...")
        resp = self.fetch_url(GAMES_LIST_URL)
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.find_all("a", href=True)

        games = []
        seen = set()
        for a in links:
            href = a["href"].strip()
            # Match game detail pages
            if "free-download" in href:
                slug = href.strip("/").split("/")[-1]
                if (
                    slug in seen
                    or not slug
                    or any(x in slug for x in ["tag", "category", "author", "page", "games-list", "top-games", "updated-games"])
                ):
                    continue
                seen.add(slug)
                title = clean_title(a.get_text(strip=True)) or slug.replace("-", " ").title()
                detail_url = urljoin(BASE_URL, href)
                games.append(
                    {
                        "title": title,
                        "slug": slug,
                        "detail_url": detail_url,
                        "card_poster_url": None,
                        "file_size": None,
                        "category": None,
                        "genres": None,
                    }
                )

        print(f"Found {len(games)} games from complete games list index.")
        return games

    def save_game(self, game_data: Dict[str, Any], detail_data: Dict[str, Any]) -> int:
        """Insert or update a game and its download links in the SQLite database (thread-safe)."""
        slug = game_data["slug"]
        title = game_data["title"]
        source_url = game_data.get("detail_url")
        file_size = game_data.get("file_size") or detail_data.get("file_size")
        category = game_data.get("category") or detail_data.get("category")
        genres = game_data.get("genres") or detail_data.get("genres")

        # Pick best poster URL (card portrait or detail landscape/cover)
        poster_url = game_data.get("card_poster_url") or detail_data.get("poster_url")

        # Download poster file locally if enabled
        local_poster_path = None
        if self.download_posters and poster_url:
            local_poster_path = self.download_poster_image(poster_url, slug)

        poster_file = self.posters_dir / f"{slug}.jpg"
        if local_poster_path:
            final_thumbnail = local_poster_path
        elif poster_file.exists():
            final_thumbnail = f"/posters/{slug}.jpg"
        else:
            final_thumbnail = poster_url

        description = detail_data.get("description")
        requirements = detail_data.get("requirements")
        files = detail_data.get("files") or []
        direct_file_url = files[0]["url"] if files else None

        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM games WHERE slug = ?", (slug,))
            row = cursor.fetchone()

            if row:
                game_id = row[0]
                cursor.execute(
                    """
                    UPDATE games
                    SET title = ?, description = COALESCE(?, description),
                        requirements = COALESCE(?, requirements),
                        thumbnail_url = COALESCE(?, thumbnail_url),
                        file_size = COALESCE(?, file_size),
                        direct_file_url = COALESCE(?, direct_file_url),
                        category = COALESCE(?, category),
                        genres = COALESCE(?, genres),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (title, description, requirements, final_thumbnail, file_size, direct_file_url, category, genres, game_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO games (
                        title, slug, description, requirements,
                        download_url, direct_file_url, thumbnail_url,
                        file_size, source_url, category, genres, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        title,
                        slug,
                        description,
                        requirements,
                        source_url,
                        direct_file_url,
                        final_thumbnail,
                        file_size,
                        source_url,
                        category,
                        genres,
                    ),
                )
                game_id = cursor.lastrowid

            for f in files:
                cursor.execute(
                    "SELECT id FROM game_files WHERE game_id = ? AND url = ?",
                    (game_id, f["url"]),
                )
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO game_files (game_id, label, url, file_type)
                        VALUES (?, ?, ?, ?)
                        """,
                        (game_id, f["label"], f["url"], f["file_type"]),
                    )

            conn.commit()
            conn.close()

        return game_id

    def is_game_complete(self, slug: str) -> bool:
        """Check if game already has mirrors and a valid poster (thread-safe)."""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT g.id, COUNT(f.id)
                FROM games g
                LEFT JOIN game_files f ON g.id = f.game_id
                WHERE g.slug = ?
                GROUP BY g.id
                """,
                (slug,),
            )
            row = cursor.fetchone()
            conn.close()

        if not row:
            return False
        has_files = row[1] > 0
        poster_file = self.posters_dir / f"{slug}.jpg"
        has_poster = (not self.download_posters) or (poster_file.exists() and poster_file.stat().st_size > 1024)
        return has_files and has_poster

    def process_single_game(self, g: Dict[str, Any], idx: int, total_games: int, stats: Dict[str, int]) -> None:
        title = g["title"]
        slug = g["slug"]
        detail_url = g["detail_url"]

        if self.is_game_complete(slug):
            return

        detail_data = {}
        if detail_url:
            try:
                detail_data = self.parse_detail_page(detail_url)
            except Exception as exc:
                stats["errors"] += 1

        try:
            self.save_game(g, detail_data)
            stats["games_scraped"] += 1

            poster_file = self.posters_dir / f"{slug}.jpg"
            if poster_file.exists():
                stats["posters_downloaded"] += 1

            files_count = len(detail_data.get("files", []))
            print(f"[{stats['games_scraped']} scraped] Saved: {title} | Mirrors: {files_count} | Poster: {slug}.jpg")
        except Exception as exc:
            stats["errors"] += 1

    def scrape(
        self,
        pages: int = 0,
        start_page: int = 1,
        limit: Optional[int] = None,
        from_list: bool = True,
        hours: float = 6.0,
    ) -> Dict[str, int]:
        """Main scraping loop with multi-worker concurrent support."""
        stats = {"games_scraped": 0, "posters_downloaded": 0, "errors": 0}
        existing_slugs = self.get_existing_slugs()
        start_time = time.time()
        max_duration = hours * 3600

        print(f"[*] Starting SteamRip Multi-Threaded Scraper ({self.workers} workers)...")
        print(f"[*] Target Duration: {hours:.1f} hours")
        print(f"[*] Database: {self.db_path} ({len(existing_slugs)} games currently stored)")
        print(f"[*] Posters directory: {self.posters_dir}")

        if from_list:
            games_to_process = self.parse_games_list_index()
            if limit:
                games_to_process = games_to_process[:limit]
            total_games = len(games_to_process)
            print(f"\n[*] Processing {total_games} games with {self.workers} workers...\n")

            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = {
                    executor.submit(self.process_single_game, g, idx, total_games, stats): g
                    for idx, g in enumerate(games_to_process, 1)
                }
                for future in as_completed(futures):
                    if time.time() - start_time > max_duration:
                        print(f"[*] Time limit ({hours} hours) reached. Stopping.")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    try:
                        future.result()
                    except Exception as exc:
                        stats["errors"] += 1
        else:
            current_page = start_page
            pages_fetched = 0
            while True:
                if time.time() - start_time > max_duration:
                    break
                if pages > 0 and pages_fetched >= pages:
                    break

                cards, has_next = self.parse_listing_page(current_page)
                if not cards:
                    if time.time() - start_time < max_duration:
                        time.sleep(300)
                        current_page = 1
                        continue
                    break

                print(f"\n[*] Page {current_page}: Found {len(cards)} games.")
                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    futures = {
                        executor.submit(self.process_single_game, g, idx, len(cards), stats): g
                        for idx, g in enumerate(cards, 1)
                    }
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception:
                            stats["errors"] += 1

                pages_fetched += 1
                if limit and stats["games_scraped"] >= limit:
                    break

                if not has_next:
                    if time.time() - start_time < max_duration:
                        time.sleep(300)
                        current_page = 1
                    else:
                        break
                else:
                    current_page += 1

        elapsed_mins = (time.time() - start_time) / 60
        print("\n" + "=" * 50)
        print(f"[*] Scraping session completed in {elapsed_mins:.1f} minutes!")
        print(f"    New games scraped:    {stats['games_scraped']}")
        print(f"    Posters downloaded:   {stats['posters_downloaded']}")
        print(f"    Errors encountered:   {stats['errors']}")
        print(f"    Database location:    {self.db_path.resolve()}")
        print(f"    Posters location:     {self.posters_dir.resolve()}")
        print("=" * 50)
        return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="SteamRip Multi-Threaded Game & Poster Scraper")
    parser.add_argument("--pages", type=int, default=0, help="Number of pages to scrape (0 for all, default: 0)")
    parser.add_argument("--start-page", type=int, default=1, help="Starting page number (default: 1)")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of games to scrape")
    parser.add_argument("--hours", type=float, default=6.0, help="Maximum run duration in hours (default: 6.0)")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent worker threads (default: 6)")
    parser.add_argument("--from-list", action="store_true", default=False, help="Scrape from the complete games-list index (A-Z)")
    parser.add_argument("--no-posters", action="store_true", help="Do not download poster images to disk")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)")
    parser.add_argument("--db-path", type=str, default=str(DEFAULT_DB_PATH), help="Path to SQLite database")
    parser.add_argument("--posters-dir", type=str, default=str(DEFAULT_POSTERS_DIR), help="Path to posters directory")

    args = parser.parse_args()

    scraper = SteamRipScraper(
        db_path=Path(args.db_path),
        posters_dir=Path(args.posters_dir),
        download_posters=not args.no_posters,
        delay=args.delay,
        workers=args.workers,
    )

    # If --from-list was explicitly requested, scrape from the full games list index
    # Otherwise, default to scraping newly added releases from the homepage (pages 1..N)
    from_list = args.from_list
    pages = args.pages if args.pages > 0 else (0 if from_list else 5)

    scraper.scrape(
        pages=pages,
        start_page=args.start_page,
        limit=args.limit,
        from_list=from_list,
        hours=args.hours,
    )


if __name__ == "__main__":
    main()
