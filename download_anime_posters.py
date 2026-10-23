import sqlite3
from pathlib import Path
from curl_cffi import curl
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
DB_PATH = BACKEND_DIR / "games.db"
POSTERS_DIR = ROOT_DIR / "posters"
BACKEND_POSTERS_DIR = BACKEND_DIR / "posters"

CLOUDFLARE_IPS = [b"steamrip.com:443:172.67.70.25", b"steamrip.com:443:104.26.3.12", b"steamrip.com:443:104.26.2.12"]

def fetch_binary(url: str) -> bytes:
    if url.startswith("/"):
        url = "https://steamrip.com" + url
    elif url.startswith("//"):
        url = "https:" + url

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
        else:
            print(f"  [Error {code}] fetching {url}")
    except Exception as e:
        print(f"  [Curl error] {e} on {url}")
    finally:
        c.close()
    return b""

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, slug, source_url FROM games WHERE id >= 4869 ORDER BY id")
    rows = cur.fetchall()

    for gid, slug, source_url in rows:
        p1 = POSTERS_DIR / f"{slug}.jpg"
        p2 = BACKEND_POSTERS_DIR / f"{slug}.jpg"

        if p1.exists() and p1.stat().st_size > 1024:
            print(f"[{gid}] {slug} poster already exists ({p1.stat().st_size} bytes)")
            continue

        print(f"[{gid}] Fetching poster for {slug} from {source_url} ...")
        # Fetch page to get img src
        c = curl.Curl()
        c.setopt(curl.CurlOpt.URL, source_url.encode("utf-8"))
        c.setopt(curl.CurlOpt.RESOLVE, CLOUDFLARE_IPS)
        c.setopt(curl.CurlOpt.FOLLOWLOCATION, 1)
        c.setopt(curl.CurlOpt.ACCEPT_ENCODING, b"")
        c.setopt(curl.CurlOpt.TIMEOUT, 20)
        c.impersonate("chrome124")
        buf = []
        c.setopt(curl.CurlOpt.WRITEFUNCTION, lambda data: buf.append(data) or len(data))
        c.perform()
        html = b"".join(buf).decode("utf-8", errors="ignore")
        c.close()

        soup = BeautifulSoup(html, "html.parser")
        img_url = ""
        entry = soup.find("div", class_=lambda cl: cl and ("entry-content" in cl or "post-content" in cl))
        if entry:
            for img in entry.find_all("img"):
                src = img.get("data-src") or img.get("src") or ""
                if src and "logo" not in src.lower() and not src.startswith("data:"):
                    img_url = src
                    break
        if not img_url:
            og = soup.find("meta", property="og:image")
            if og:
                img_url = og.get("content", "")

        if img_url:
            data = fetch_binary(img_url)
            if data and len(data) > 1024:
                p1.write_bytes(data)
                p2.write_bytes(data)
                print(f"  -> SUCCESS! Saved {len(data)} bytes to {slug}.jpg")
            else:
                print(f"  -> FAILED to download from {img_url}")

if __name__ == "__main__":
    main()
