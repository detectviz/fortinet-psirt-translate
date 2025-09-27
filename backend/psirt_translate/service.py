"""Core service orchestration for fetching and translating advisories."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable, List, Optional

from .config import DEFAULT_OUTPUT_FILENAME
from .fetcher import fetch_feed
from .storage import AdvisoryStore, TranslationCache
from .translator import TranslatorService

logger = logging.getLogger(__name__)


class PSIRTService:
    def __init__(
        self,
        store: Optional[AdvisoryStore] = None,
        cache: Optional[TranslationCache] = None,
        translator: Optional[TranslatorService] = None,
    ) -> None:
        self.store = store or AdvisoryStore()
        self.cache = cache or TranslationCache()
        self.translator = translator or TranslatorService(self.cache)

    def refresh_advisories(self, feed_url: str, limit: Optional[int] = None) -> List[dict]:
        advisories = fetch_feed(feed_url, limit=limit)
        processed: List[dict] = []
        for item in advisories:
            translated_title = self.translator.translate(item.get("title", ""))
            translated_summary = self.translator.translate(item.get("summary", ""))
            processed.append(
                {
                    "title_en": item.get("title", ""),
                    "title_zh": translated_title,
                    "summary_en": item.get("summary", ""),
                    "summary_zh": translated_summary,
                    "link": item.get("link"),
                    "published": item.get("published"),
                    "id": item.get("id"),
                }
            )
        if processed:
            self.store.upsert_many(processed)
        else:
            logger.info("No advisories fetched; keeping existing store contents")
        return self.store.get_all()

    def export_to_file(self, advisories: Iterable[dict], output_path: Optional[Path] = None) -> Path:
        data = list(advisories)
        path = output_path or Path(DEFAULT_OUTPUT_FILENAME)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Wrote %d advisories to %s", len(data), path)
        return path

    def get_cached_advisories(self) -> List[dict]:
        return self.store.get_all()

    def reload_technical_terms(self) -> bool:
        """Reload technical terms from configuration file."""
        return self.translator.reload_technical_terms()

    def add_custom_technical_term(self, term: str) -> bool:
        """Add a custom technical term to prevent translation."""
        return self.translator.add_custom_term(term)

    def get_technical_terms_count(self) -> int:
        """Get the count of loaded technical terms."""
        return len(self.translator._technical_terms) if hasattr(self.translator, '_technical_terms') else 0
