"""RSS feed fetching utilities."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List, Optional

import feedparser

logger = logging.getLogger(__name__)


def _format_datetime(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        parsed = feedparser._parse_date(value)  # type: ignore[attr-defined]
        if not parsed:
            return value
        return datetime(*parsed[:6]).isoformat()
    except Exception:  # pragma: no cover - defensive
        return value


def fetch_feed(feed_url: str, limit: Optional[int] = None) -> List[dict]:
    """Fetch advisories from the provided RSS feed."""
    logger.info("Fetching PSIRT feed from %s", feed_url)
    parsed = feedparser.parse(feed_url)
    if parsed.bozo:
        logger.warning("Feed parsing reported issues: %s", parsed.bozo_exception)

    entries: Iterable = parsed.get("entries", [])
    advisories: List[dict] = []
    for entry in entries:
        advisories.append(
            {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link"),
                "published": _format_datetime(entry.get("published")),
                "id": entry.get("id") or entry.get("guid") or entry.get("link"),
            }
        )
        if limit and len(advisories) >= limit:
            break
    logger.info("Fetched %d advisories from feed", len(advisories))
    return advisories
