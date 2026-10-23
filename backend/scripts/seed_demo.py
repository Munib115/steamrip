"""Seed the database with demo data so the app runs without scraping a third party.

Only run this locally. It inserts games if the table is empty.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models import Game, GameFile

DEMO_GAMES = [
    {
        "title": "Demo Adventure",
        "slug": "demo-adventure",
        "description": "A short demo game used for local development and UI testing.",
        "requirements": "OS: Windows/macOS\nCPU: 2 cores\nRAM: 4 GB\nStorage: 500 MB",
        "thumbnail_url": None,
        "files": [
            {"label": "Part 1", "url": "https://example.local/files/demo-adventure-part1.zip", "file_type": "direct"}
        ],
    },
    {
        "title": "Racing Prototype",
        "slug": "racing-prototype",
        "description": "An open-world racing prototype demo.",
        "thumbnail_url": None,
        "files": [
            {"label": "Mirror 1", "url": "https://example.local/files/racing-prototype-mirror1.zip", "file_type": "direct"},
            {"label": "Mirror 2", "url": "https://example.local/files/racing-prototype-mirror2.zip", "file_type": "indirect"},
        ],
    },
    {
        "title": "Puzzle Quest",
        "slug": "puzzle-quest",
        "description": "A tile-matching puzzle game with a level editor.",
        "thumbnail_url": None,
        "files": [
            {"label": "Full game", "url": "https://example.local/files/puzzle-quest-full.zip", "file_type": "direct"}
        ],
    },
    {
        "title": "Sci-Fi Explorer",
        "slug": "sci-fi-explorer",
        "description": "Procedurally generated space exploration demo.",
        "thumbnail_url": None,
        "files": [
            {"label": "Part 1", "url": "https://example.local/files/scifi-explorer-p1.zip", "file_type": "direct"},
            {"label": "Part 2", "url": "https://example.local/files/scifi-explorer-p2.zip", "file_type": "direct"},
        ],
    },
    {
        "title": "Pixel Dungeon",
        "slug": "pixel-dungeon",
        "description": "Rogue-like dungeon crawler with pixel art.",
        "thumbnail_url": None,
        "files": [
            {"label": "Download", "url": "https://example.local/files/pixel-dungeon.zip", "file_type": "indirect"}
        ],
    },
]


async def main() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Game).limit(1))).scalar_one_or_none()
        if existing:
            print("Database already seeded. Skipping.")
            return
        for g in DEMO_GAMES:
            game = Game(
                title=g["title"],
                slug=g["slug"],
                description=g["description"],
                requirements=g.get("requirements"),
                source_url=f"https://example.local/games/{g['slug']}",
                thumbnail_url=g.get("thumbnail_url"),
                direct_file_url=g["files"][0]["url"] if g["files"] else None,
                download_url=f"https://example.local/games/{g['slug']}",
            )
            session.add(game)
            await session.flush()
            for idx, f in enumerate(g["files"]):
                session.add(
                    GameFile(
                        game_id=game.id,
                        label=f["label"],
                        url=f["url"],
                        file_type=f.get("file_type"),
                    )
                )
        await session.commit()
    print("Seeded demo games.")


if __name__ == "__main__":
    asyncio.run(main())