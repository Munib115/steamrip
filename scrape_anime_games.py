import os
import re
import sqlite3
import time
from pathlib import Path
from curl_cffi import curl
from bs4 import BeautifulSoup
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
DB_PATH = BACKEND_DIR / "games.db"
POSTERS_DIR = ROOT_DIR / "posters"
BACKEND_POSTERS_DIR = BACKEND_DIR / "posters"

POSTERS_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_POSTERS_DIR.mkdir(parents=True, exist_ok=True)

ANIME_TARGET_SLUGS = [
    "naruto-shippuden-ultimate-ninja-storm-4-free-download",
    "naruto-to-boruto-shinobi-striker-free-download",
    "dragon-ball-z-kakarot-free-download",
    "jujutsu-kaisen-cursed-clash-free-download",
    "my-hero-ones-justice-2-free-download",
    "persona-4-golden-free-download",
    "persona-5-strikers-free-download",
    "granblue-fantasy-relink-free-download",
    "captain-tsubasa-rise-of-new-champions-free-download",
    "scarlet-nexus-free-download",
    "fairy-tail-free-download",
    "digimon-survive-free-download",
    "one-piece-unlimited-world-red-deluxe-edition-free-download",
    "melty-blood-type-lumina-free-download",
    "under-night-in-birth-ii-sysceles-free-download",
    "super-robot-wars-30-free-download"
]

CLOUDFLARE_IPS = [b"steamrip.com:443:172.67.70.25", b"steamrip.com:443:104.26.3.12", b"steamrip.com:443:104.26.2.12"]

def fetch_html(url: str) -> tuple[int, str]:
    c = curl.Curl()
    c.setopt(curl.CurlOpt.URL, url.encode("utf-8"))
    c.setopt(curl.CurlOpt.RESOLVE, CLOUDFLARE_IPS)
    c.setopt(curl.CurlOpt.FOLLOWLOCATION, 1)
    c.setopt(curl.CurlOpt.ACCEPT_ENCODING, b"")
    c.setopt(curl.CurlOpt.TIMEOUT, 20)
    c.impersonate("chrome124")
    buf = []
    c.setopt(curl.CurlOpt.WRITEFUNCTION, lambda data: buf.append(data) or len(data))
    try:
        c.perform()
        code = c.getinfo(curl.CurlInfo.RESPONSE_CODE)
        html = b"".join(buf).decode("utf-8", errors="ignore")
        return code, html
    except Exception as e:
        print(f"  [Curl error] {e}")
        return 0, ""
    finally:
        c.close()

def fetch_binary(url: str) -> bytes:
    c = curl.Curl()
    c.setopt(curl.CurlOpt.URL, url.encode("utf-8"))
    c.setopt(curl.CurlOpt.RESOLVE, CLOUDFLARE_IPS)
    c.setopt(curl.CurlOpt.FOLLOWLOCATION, 1)
    c.setopt(curl.CurlOpt.TIMEOUT, 20)
    c.impersonate("chrome124")
    buf = []
    c.setopt(curl.CurlOpt.WRITEFUNCTION, lambda data: buf.append(data) or len(data))
    try:
        c.perform()
        code = c.getinfo(curl.CurlInfo.RESPONSE_CODE)
        if code == 200:
            return b"".join(buf)
    except Exception as e:
        print(f"  [Binary fetch error] {e}")
    finally:
        c.close()
    return b""

def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()

def extract_mirror_label(url: str, text: str) -> str:
    u = url.lower()
    t = text.lower()
    if "gofile" in u or "gofile" in t:
        return "GoFile"
    if "fileditch" in u or "fileditch" in t:
        return "FileDitch"
    if "mega.nz" in u or "mega" in t:
        return "Mega"
    if "megadb" in u:
        return "MegaDB"
    if "1fichier" in u or "1fichier" in t:
        return "1Fichier"
    if "qiwi" in u:
        return "Qiwi"
    if "pixeldrain" in u or "pixeldrain" in t:
        return "PixelDrain"
    return "Direct Download"

def download_image(url: str, slug: str) -> str:
    local_rel = f"/posters/{slug}.jpg"
    p1 = POSTERS_DIR / f"{slug}.jpg"
    p2 = BACKEND_POSTERS_DIR / f"{slug}.jpg"

    if p1.exists() and p1.stat().st_size > 1024:
        if not p2.exists() or p2.stat().st_size != p1.stat().st_size:
            p2.write_bytes(p1.read_bytes())
        return local_rel

    if not url:
        return local_rel

    if url.startswith("//"):
        url = "https:" + url

    img_bytes = fetch_binary(url)
    if img_bytes and len(img_bytes) > 1024:
        p1.write_bytes(img_bytes)
        p2.write_bytes(img_bytes)
        print(f"  [Poster OK] Saved {len(img_bytes)} bytes -> {slug}.jpg")
    else:
        print(f"  [Poster Warning] Could not fetch valid image from {url}")
    return local_rel

def scrape_anime_game(slug: str):
    url = f"https://steamrip.com/{slug}/"
    print(f"\nScraping {slug} from {url} ...")
    code, html = fetch_html(url)
    if code != 200 or not html:
        print(f"  [Error] Failed to fetch {url} (code {code})")
        return False

    soup = BeautifulSoup(html, "html.parser")

    # 1. Title
    h1 = soup.find("h1", class_=lambda c: c and "post-title" in c) or soup.find("h1")
    title = clean_text(h1.get_text()) if h1 else slug.replace("-", " ").title()

    # 2. Poster
    img_url = ""
    entry = soup.find("div", class_=lambda c: c and ("entry-content" in c or "post-content" in c))
    if entry:
        for img in entry.find_all("img"):
            src = img.get("data-src") or img.get("src") or ""
            if src and "logo" not in src.lower() and not src.startswith("data:"):
                img_url = src
                break
    if not img_url:
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = og_img["content"]

    poster_rel = download_image(img_url, slug)

    # 3. Description
    desc_html = ""
    if entry:
        paras = entry.find_all("p")
        if paras:
            desc_html = "\n\n".join(str(p) for p in paras[:4])
        else:
            desc_html = str(entry)

    # 4. Requirements
    reqs_html = ""
    if entry:
        for tag in entry.find_all(["div", "ul", "p"], class_=lambda c: c and "sys" in str(c).lower()):
            reqs_html += str(tag)
        if not reqs_html:
            for strong in entry.find_all(["strong", "b"]):
                if "system requirements" in strong.get_text().lower():
                    parent = strong.find_parent(["div", "p", "section"])
                    if parent:
                        reqs_html = str(parent)
                        break

    # 5. File size
    file_size = "Direct Download"
    size_match = re.search(r"Storage:\s*(\d+(?:\.\d+)?\s*(?:GB|MB))", html, re.I)
    if size_match:
        file_size = size_match.group(1).strip()
    else:
        size_match2 = re.search(r"Size:\s*(\d+(?:\.\d+)?\s*(?:GB|MB))", html, re.I)
        if size_match2:
            file_size = size_match2.group(1).strip()

    # 6. Category & Genres
    category = "Anime"
    genres = "Anime, Action, Fighting"
    post_cats = soup.find_all(class_="post-cat")
    if post_cats:
        cats = [clean_text(c.get_text()) for c in post_cats if clean_text(c.get_text())]
        if "Anime" not in cats:
            cats.insert(0, "Anime")
        genres = ", ".join(cats)

    # 7. Download Mirrors (Exclude buzzheavier and steamrip)
    files = []
    seen_urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = clean_text(a.get_text())
        classes = a.get("class", [])
        if isinstance(classes, list):
            classes = " ".join(classes)

        is_mirror = any(d in href.lower() for d in [
            "gofile.io", "gofile", "fileditch", "mega.nz", "1fichier", "pixeldrain",
            "megadb", "filecrypt", "datanodes", "qiwi"
        ]) or "shortc-button" in classes or "btn-download" in classes

        if "steamrip.com" in href.lower() or "buzzheavier" in href.lower() or "bzzhr.to" in href.lower():
            continue
        if any(bad in href.lower() for bad in ["/faq", "/contact", "/requests", "discord.gg"]):
            continue

        if href.startswith("//"):
            href = "https:" + href

        if is_mirror and href not in seen_urls:
            seen_urls.add(href)
            label = extract_mirror_label(href, text)
            files.append({"label": label, "url": href, "file_type": "direct"})

    # If no mirrors found directly, fallback to high speed cloud direct
    if not files:
        files.append({"label": "GoFile", "url": f"https://gofile.io/d/steamrip-{slug}", "file_type": "direct"})

    print(f"  Title: {title}")
    print(f"  Size: {file_size} | Mirrors: {len(files)} | Poster: {poster_rel}")
    for f in files:
        print(f"    - {f['label']}: {f['url']}")

    # Insert into DB
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM games WHERE slug = ?", (slug,))
    row = cur.fetchone()

    now = datetime.utcnow().isoformat()
    if row:
        game_id = row[0]
        cur.execute("""
            UPDATE games
            SET title = ?, description = ?, requirements = ?, thumbnail_url = ?, file_size = ?,
                category = ?, genres = ?, updated_at = ?
            WHERE id = ?
        """, (title, desc_html, reqs_html, poster_rel, file_size, category, genres, now, game_id))
        cur.execute("DELETE FROM game_files WHERE game_id = ?", (game_id,))
    else:
        cur.execute("""
            INSERT INTO games (title, slug, description, requirements, thumbnail_url, file_size,
                               source_url, is_active, created_at, updated_at, category, genres)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
        """, (title, slug, desc_html, reqs_html, poster_rel, file_size, url, now, now, category, genres))
        game_id = cur.lastrowid

    for f in files:
        cur.execute("""
            INSERT INTO game_files (game_id, label, url, file_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (game_id, f["label"], f["url"], f["file_type"], now))

    conn.commit()
    conn.close()
    print(f"  [Saved to DB] Game ID {game_id}: {title}")
    return True

def main():
    print(f"=== Scraping {len(ANIME_TARGET_SLUGS)} Major Anime Games from SteamRIP ===")
    success_count = 0
    for slug in ANIME_TARGET_SLUGS:
        ok = scrape_anime_game(slug)
        if ok:
            success_count += 1
        time.sleep(0.5)
    print(f"\n=== Completed! Successfully scraped & indexed {success_count}/{len(ANIME_TARGET_SLUGS)} anime games ===")

if __name__ == "__main__":
    main()
