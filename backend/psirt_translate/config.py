"""Configuration utilities for the PSIRT translation service."""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_FEED_URL = "https://www.fortiguard.com/rss/ir.xml"
TRANSLATION_CACHE_PATH = DATA_DIR / "translation_cache.json"
ADVISORY_STORE_PATH = DATA_DIR / "advisories.json"

DEFAULT_OUTPUT_FILENAME = "psirt_advisories.json"

# Scheduling defaults
DEFAULT_INTERVAL_MINUTES = 24 * 60
