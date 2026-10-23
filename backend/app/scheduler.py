"""APScheduler-based periodic scraper runner."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.scraper import scrape_all

scheduler: Optional[BackgroundScheduler] = None


def _job() -> None:
    asyncio.run(scrape_all())


def start_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        return
    interval_hours = int(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        _job,
        "interval",
        hours=interval_hours,
        id="scrape_all",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    global scheduler
    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=False)
    scheduler = None