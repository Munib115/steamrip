"""Async, polite web scraper for game archive listings.

IMPORTANT: Only scrape websites you own or have explicit permission to scrape.
Respect robots.txt, terms of service, and applicable law. This module is a
general-purpose framework; selectors are configured via environment variables.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import urllib.robotparser
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from lxml import html
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Game, GameFile

logger = logging.getLogger(__name__)

USER_AGENT = "GameArchiveBot/1.0 (compatible; +https://example.local/bot; mailto:admin@example.local)"
REQUEST_TIMEOUT = 30.0
RATE_LIMIT_DELAY = float(os.getenv("SCRAPE_RATE_LIMIT_DELAY", "1.5"))
MAX_PAGES = int(os.getenv("SCRAPE_MAX_PAGES", "5"))
DEFAULT_BASE_URL = os.getenv("SCRAPE_BASE_URL", "http://127.0.0.1:8000/fixtures/")

# XPath selectors - override via environment variables to match a target site.
SEL_CARD = os.getenv(
    "SCRAPE_CARD_SELECTOR",
    "//li[contains(@class,'post-item')] | //article[contains(@class,'game')] | //article",
)
SEL_TITLE = os.getenv(
    "SCRAPE_TITLE_SELECTOR",
    ".//h2[contains(@class,'post-title')]/a/text() | .//h2/a/text() | .//h2/text()",
)
SEL_DETAIL_LINK = os.getenv(
    "SCRAPE_DETAIL_LINK_SELECTOR",
    ".//h2[contains(@class,'post-title')]/a/@href | .//h2/a/@href | .//a/@href",
)
SEL_THUMB = os.getenv(
    "SCRAPE_THUMB_SELECTOR",
    ".//img/@data-src | .//img/@data-lazy-src | .//noscript//img/@src | .//img/@src",
)
SEL_NEXT_PAGE = os.getenv("SCRAPE_NEXT_PAGE_SELECTOR", "//a[contains(@class,'next')]/@href")

# Detail page selectors
SEL_DESC = os.getenv(
    "SCRAPE_DESC_SELECTOR",
    "//div[contains(@class,'entry-content')]//p//text() | //div[contains(@class,'description')]//p//text()",
)
SEL_DOWNLOAD = os.getenv(
    "SCRAPE_DOWNLOAD_SELECTOR",
    "//a[contains(@class,'shortc-button') or contains(@class,'download') or contains(@class,'btn-download')]/@href",
)
SEL_REQUIREMENTS = os.getenv("SCRAPE_REQ_SELECTOR", "//div[contains(@class,'requirements')]//text()")


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


class RobotsCache:
    """In-memory robots.txt cache keyed by origin."""

    def __init__(self) -> None:
        self._cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    async def allowed(self, client: httpx.AsyncClient, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = self._cache.get(robots_url)
        if rp is None:
            try:
                resp = await client.get(robots_url, timeout=10.0)
                lines = resp.text.splitlines() if resp.status_code == 200 else []
            except Exception:
                lines = []
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.parse(lines)
            self._cache[robots_url] = rp
        return rp.can_fetch(USER_AGENT, url)


robots_txt = RobotsCache()


async def fetch(client: httpx.AsyncClient, url: str) -> httpx.Response:
    """Fetch a URL politely: robots.txt check, rate limit, raise on HTTP error."""
    if not await robots_txt.allowed(client, url):
        raise RuntimeError(f"Disallowed by robots.txt: {url}")
    response = await client.get(url, follow_redirects=True, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    await asyncio.sleep(RATE_LIMIT_DELAY)
    return response


def _first(values: list[Any], default: Any = None) -> Any:
    return values[0] if values else default

async def scrape_detail(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """Scrape a single game detail page."""
    response = await fetch(client, url)
    tree = html.fromstring(response.content)
    tree.make_links_absolute(url)

    description = " ".join(t.strip() for t in tree.xpath(SEL_DESC) if t.strip())
    raw_links = tree.xpath(SEL_DOWNLOAD)
    requirements = " ".join(t.strip() for t in tree.xpath(SEL_REQUIREMENTS) if t.strip())

    files = []
    for link in raw_links:
        absolute = urljoin(url, link)
        label = link.rsplit("/", 1)[-1] or "Download"
        files.append({"label": label, "url": absolute, "file_type": "direct"})

    og_posters = tree.xpath("//meta[@property='og:image']/@content")
    poster_url = og_posters[0] if og_posters else None

    return {
        "url": url,
        "description": description or None,
        "files": files,
        "requirements": requirements or None,
        "poster_url": poster_url,
    }


async def scrape_listing_page(
    client: httpx.AsyncClient, url: str
) -> tuple[list[dict[str, Any]], str | None]:
    """Scrape a listing page. Returns (games, next_page_url)."""
    response = await fetch(client, url)
    tree = html.fromstring(response.content)
    tree.make_links_absolute(url)

    games: list[dict[str, Any]] = []
    for card in tree.xpath(SEL_CARD):
        title = _first(card.xpath(SEL_TITLE))
        if not title:
            continue
        title = title.strip()
        detail_path = _first(card.xpath(SEL_DETAIL_LINK))
        detail_url = urljoin(url, detail_path) if detail_path else None
        thumbs = [t for t in card.xpath(SEL_THUMB) if not str(t).startswith("data:")]
        thumb = thumbs[0] if thumbs else None
        thumb_url = urljoin(url, thumb) if thumb else None
        games.append(
            {
                "title": title,
                "slug": slugify(title),
                "detail_url": detail_url,
                "thumbnail_url": thumb_url,
            }
        )

    next_paths = tree.xpath(SEL_NEXT_PAGE)
    next_url = urljoin(url, next_paths[0]) if next_paths else None
    return games, next_url


async def _upsert_game(session: AsyncSession, data: dict[str, Any]) -> int | None:
    """Insert a game if its slug is not already present. Returns new id or None."""
    existing = (
        await session.execute(select(Game).where(Game.slug == data["slug"]))
    ).scalar_one_or_none()
    if existing:
        return None

    detail: dict[str, Any] = {}
    if data.get("detail_url"):
        try:
            async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as detail_client:
                detail = await scrape_detail(detail_client, data["detail_url"])
        except Exception as exc:  # noqa: BLE001 - a broken detail page must not abort the run
            logger.warning("Skipping detail page %s: %s", data["detail_url"], exc)
            detail = {}

    files = detail.get("files") or []
    game = Game(
        title=data["title"],
        slug=data["slug"],
        description=detail.get("description"),
        requirements=detail.get("requirements"),
        source_url=data.get("detail_url"),
        thumbnail_url=data.get("thumbnail_url") or detail.get("poster_url"),
        direct_file_url=files[0].get("url") if files else None,
        download_url=data.get("detail_url"),
    )
    session.add(game)
    await session.flush()

    for idx, f in enumerate(files):
        session.add(
            GameFile(
                game_id=game.id,
                label=f.get("label") or f"Part {idx + 1}",
                url=f.get("url"),
                file_type=f.get("file_type"),
            )
        )
    return game.id


async def scrape_all(
    base_url: str | None = None, max_pages: int | None = None
) -> dict[str, int]:
    """Iterate listing pages and persist newly discovered games.

    Returns a stats dict: {pages, games_found, games_saved}.
    """
    base_url = base_url or DEFAULT_BASE_URL
    max_pages = max_pages or MAX_PAGES

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    stats = {"pages": 0, "games_found": 0, "games_saved": 0}

    async with httpx.AsyncClient(
        headers=headers, follow_redirects=True, timeout=REQUEST_TIMEOUT
    ) as client:
        url = base_url
        for _ in range(max_pages):
            if not url:
                break
            stats["pages"] += 1
            try:
                games, next_url = await scrape_listing_page(client, url)
            except Exception as exc:  # noqa: BLE001 - one bad page must not abort the run
                logger.warning("Skipping listing page %s: %s", url, exc)
                break
            stats["games_found"] += len(games)

            async with AsyncSessionLocal() as session:
                saved = 0
                for game in games:
                    if await _upsert_game(session, game) is not None:
                        saved += 1
                await session.commit()
            stats["games_saved"] += saved
            url = next_url

    return stats