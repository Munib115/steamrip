"""Local fixture site.

Serves realistic, self-hosted HTML (listing pages + detail pages) so the
scraper can be exercised end-to-end without contacting any third party.

The markup here intentionally mirrors the default XPath selectors in
app/scraper.py, so the default configuration works out of the box.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, Response

router = APIRouter(tags=["fixtures"])

# Fictional demo titles - not real-world products.
GAMES = [
    ("neon-drift", "Neon Drift"),
    ("castle-blackwood", "Castle Blackwood"),
    ("ember-circuit", "Ember Circuit"),
    ("tide-runner", "Tide Runner"),
    ("glass-harbor", "Glass Harbor"),
    ("paper-kingdom", "Paper Kingdom"),
    ("rust-and-rune", "Rust and Rune"),
    ("midnight-market", "Midnight Market"),
    ("copper-meadow", "Copper Meadow"),
    ("solar-archive", "Solar Archive"),
    ("velvet-circus", "Velvet Circus"),
    ("northwind-pass", "Northwind Pass"),
]

DESCRIPTIONS = {
    "neon-drift": (
        "A high-speed arcade racer set in a rain-soaked retro-future city.",
        "Build your chassis, tune the handling, and race the night circuit.",
    ),
    "castle-blackwood": (
        "A tactical strategy game about defending a sprawling forest keep.",
        "Manage resources, fortify the walls, and outlast the long siege.",
    ),
    "ember-circuit": (
        "A physics puzzle game where you route energy through a broken grid.",
        "Every conduit is a tradeoff between power, heat, and control.",
    ),
}

DEFAULT_DESC = (
    "An independent open-source style demo project released for free.",
    "This entry exists to exercise listing pagination, detail parsing, and "
    "multi-file download handling in the scraper.",
)

REQUIREMENTS = [
    "OS: Windows 10 64-bit / Linux",
    "CPU: 4 cores, 3.0 GHz",
    "RAM: 8 GB",
    "Storage: 2 GB available space",
    "GPU: DirectX 11 compatible",
]

PAGE_SIZE = 6


def _render_listing(page: int, total_pages: int) -> str:
    start = (page - 1) * PAGE_SIZE
    items = GAMES[start : start + PAGE_SIZE]

    cards = []
    for slug, title in items:
        cards.append(
            f"""
    <article class="game-card">
      <h2><a href="/fixtures/{slug}.html">{title}</a></h2>
      <img class="thumb" src="/fixtures/static/{slug}.png" alt="{title}">
    </article>"""
        )

    if page < total_pages:
        next_link = (
            f'<a class="next" href="/fixtures/?page={page + 1}">Next &rarr;</a>'
        )
    else:
        next_link = '<span class="next disabled">Next &rarr;</span>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Game Archive - Listing (page {page}/{total_pages})</title>
</head>
<body>
  <main class="listing">
    <h1>Game Archive Demo</h1>
    <div class="cards">
{''.join(cards)}
    </div>
    <nav class="pagination">
      {next_link}
    </nav>
  </main>
</body>
</html>"""


def _render_detail(slug: str, title: str) -> str:
    desc1, desc2 = DESCRIPTIONS.get(slug, DEFAULT_DESC)
    reqs = "".join(f"<li>{r}</li>" for r in REQUIREMENTS)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
</head>
<body>
  <article class="game-detail">
    <h1>{title}</h1>
    <img class="thumb" src="/fixtures/static/{slug}.png" alt="{title}">

    <div class="description">
      <p>{desc1}</p>
      <p>{desc2}</p>
    </div>

    <div class="requirements">
      <ul>
        {reqs}
      </ul>
    </div>

    <div class="downloads">
      <a class="download" href="/fixtures/files/{slug}.zip">Main file ({slug}.zip)</a>
      <a class="download" href="/fixtures/files/{slug}-patch.zip">Patch ({slug}-patch.zip)</a>
    </div>
  </article>
</body>
</html>"""


@router.get("/fixtures/", response_class=HTMLResponse)
async def fixtures_listing(page: int = Query(1, ge=1)) -> HTMLResponse:
    """Paginated listing page used as the default scrape target."""
    total_pages = max(1, -(-len(GAMES) // PAGE_SIZE))
    page = min(page, total_pages)
    return HTMLResponse(_render_listing(page, total_pages))


@router.get("/fixtures/{slug}.html", response_class=HTMLResponse)
async def fixtures_detail(slug: str) -> HTMLResponse:
    """Detail page for a single game."""
    lookup = dict(GAMES)
    if slug not in lookup:
        return HTMLResponse(
            "<!DOCTYPE html><html><body><h1>404 Not Found</h1></body></html>",
            status_code=404,
        )
    return HTMLResponse(_render_detail(slug, lookup[slug]))


@router.get("/fixtures/static/{name}.png")
async def fixtures_placeholder(name: str):
    """Tiny 1x1 PNG placeholder so <img> tags resolve without external assets."""
    import base64

    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    return Response(content=png, media_type="image/png")


@router.get("/fixtures/files/{name}")
async def fixtures_file(name: str):
    """Fake downloadable file so /download/{id} has a real target to redirect to."""
    payload = f"Demo archive placeholder for {name}\n".encode()
    return Response(
        content=payload,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )