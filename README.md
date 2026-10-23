# SteamRip Game Archive Scraper & Frontend

> ⚠️ **Legal / ethical notice.** This is a **general-purpose web-scraping archive framework**. Do **not** use it to scrape or redistribute copyrighted material (e.g. cracked games from SteamRip or similar sites) unless you own the content or have explicit written permission. Respect `robots.txt`, each site's Terms of Service, rate limits, and the laws of your jurisdiction. The default scraper target is a local fixture so nothing third-party is contacted out of the box.

## What this is

A lightweight game-archive application:

* **Backend (FastAPI + SQLite):** async scraper (`httpx` + `lxml`/`cssselect`), SQLAlchemy/aiosqlite database, paginated + searchable API, file download endpoint, optional `APScheduler` refresh job.
* **Frontend (Vite + Tailwind CSS):** responsive game grid, search, pagination, lazy image loading, game detail pages, download buttons with progress (`nprogress`).
* **Deployment:** Vite static site on Vercel; FastAPI backend on a persistent host (see Phase 3 notes below).

## Repository layout

```
streamrip/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, CORS, lifespan (DB + scheduler)
│   │   ├── database.py      # async SQLAlchemy + aiosqlite session
│   │   ├── models.py        # Game / GameFile SQLAlchemy models
│   │   ├── schemas.py       # Pydantic v2 schemas
│   │   ├── scraper.py       # polite httpx/lxml scraper (robots.txt, rate limit, dedupe)
│   │   ├── scheduler.py     # APScheduler periodic scrape
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── games.py     # GET /games, GET /games/{id}
│   │       ├── download.py  # GET /download/{id} (redirect or proxy)
│   │       └── fixtures.py  # built-in demo HTML site at /fixtures/
│   ├── scripts/
│   │   └── seed_demo.py     # seed demo data (no third-party scraping)
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── src/
│       ├── main.js          # router, rendering, lazy images, downloads
│       ├── api.js           # fetch wrapper around FastAPI endpoints
│       └── style.css        # Tailwind layers
├── vercel.json              # Vercel config for the Vite frontend
└── .gitignore
```

## Phase 1 — Backend

### Install

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # edit as needed
```

> **Python version note:** this repo was tested with Python 3.14 in this environment. `lxml`, `sqlalchemy` and `uvicorn` may need source builds on very new Python versions. If you hit missing wheels, use Python 3.11 or 3.12.

### Seed demo data (no third-party contact)

```bash
python scripts/seed_demo.py
```

### Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API docs.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/games` | Paginated list (`?page=`, `?page_size=`, `?search=`) |
| GET | `/games/{id}` | Single game with files |
| GET | `/download/{id}` | 302 redirect to file URL; `?proxy=1` streams through the server |
| GET | `/download/{id}?file_id={fileId}` | 302 redirect to a **specific** file of a multi-file game |
| GET | `/fixtures/` | Local demo listing site (default scrape target) |
| GET | `/fixtures/{slug}.html` | Local demo detail page |

`GET /games` returns `{ items, total, page, page_size, pages }`.

### Built-in demo site (fixture)

The backend ships a small self-hosted HTML site so the scraper can be exercised
end-to-end without contacting any third party. It is mounted at `/fixtures/`
and its markup intentionally matches the default XPath selectors.

```bash
# terminal 1 - start the API
uvicorn app.main:app --reload --port 8000

# terminal 2 - scrape the built-in demo site
python -c "import asyncio; from app.scraper import scrape_all; print(asyncio.run(scrape_all()))"
# -> {'pages': 2, 'games_found': 12, 'games_saved': 12}
```

Then browse `http://localhost:8000/games` to see the scraped results.

### Scraper configuration

All scraper behavior is driven by environment variables in `.env` — **no code changes needed to retarget**:

* `SCRAPE_BASE_URL` — listing URL to crawl
* `SCRAPE_MAX_PAGES` — max listing pages
* `SCRAPE_RATE_LIMIT_DELAY` — seconds between requests (politeness)
* `SCRAPE_CARD_SELECTOR`, `SCRAPE_TITLE_SELECTOR`, `SCRAPE_DETAIL_LINK_SELECTOR`, `SCRAPE_THUMB_SELECTOR`, `SCRAPE_NEXT_PAGE_SELECTOR` — XPath for listing cards
* `SCRAPE_DESC_SELECTOR`, `SCRAPE_DOWNLOAD_SELECTOR`, `SCRAPE_REQ_SELECTOR` — XPath for detail pages

The scraper:
1. Fetches `robots.txt` per origin and honors `can_fetch`.
2. Rate-limits every request (`SCRAPE_RATE_LIMIT_DELAY`).
3. De-duplicates by `slug` (insert-or-ignore).
4. Skips broken detail pages and listing pages instead of aborting the run.
5. Stores `description`, `requirements`, thumbnail, and one `GameFile` row per
   download link found on the detail page.

### Scheduled refresh

Set `ENABLE_SCHEDULER=true` and `SCRAPE_INTERVAL_HOURS` in `.env`; the FastAPI lifespan starts an `APScheduler` background job that calls `scrape_all()` on the interval.

## Phase 2 — Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, proxies to http://localhost:8000
npm run build      # -> frontend/dist
npm run preview
```

Features:
* Responsive Tailwind grid of game cards
* Search + pagination (`/games?search=&page=`)
* Lazy image loading via `IntersectionObserver`
* Client-side routing (`/`, `/game/:id`) with history API
* Download button → `GET /download/{id}?file_id=…` with `nprogress` progress bar

Set `VITE_API_URL` (e.g. in Vercel project settings or `.env`) to point the build at your production backend.

## Phase 3 — Deployment

### Frontend → Vercel

`vercel.json` is configured at the repo root:

* Build: `cd frontend && npm install && npm run build`
* Output: `frontend/dist`
* SPA fallback: all non-asset routes serve `/index.html`

Add `VITE_API_URL=<your-backend-url>` as a Vercel **Environment Variable** (it is read at Vite build time).

### Backend → do NOT put on Vercel serverless

FastAPI + SQLite + APScheduler **does not fit Vercel serverless functions**:
* the filesystem is ephemeral/read-only (SQLite won't persist),
* there is no long-running process for `APScheduler`,
* large file streaming is unsuitable for serverless.

**Recommended:** host the FastAPI backend on a persistent platform (Railway, Render, Fly.io, DigitalOcean App Platform, EC2, etc.) with a persistent disk or a managed database, and run the scraper scheduler there. Keep the Vite frontend on Vercel.

If you must use Vercel for the API, you would need to:
* replace SQLite with an external DB (e.g. Supabase/Neon Postgres),
* replace `APScheduler` with Vercel Cron + a serverless function that triggers the scrape,
* serve files from object storage (S3/R2) rather than streaming through functions.

## Monitoring

* Backend: `/health` endpoint + uvicorn/access logs; watch scraper `stats` (`pages`, `games_found`, `games_saved`) and robots.txt rejections.
* Frontend: Vercel analytics + browser console for failed fetch/downloads.

## Safety checklist before pointing at a real site

- [ ] You own the site or have written permission to scrape it.
- [ ] `robots.txt` permits the user-agent/paths you will fetch.
- [ ] Rate limit is set high enough not to burden the host.
- [ ] You are not redistributing copyrighted binaries without rights.

## License

MIT — adapt as needed; the legal notice above still applies to how you use it.