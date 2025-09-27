"""Persistent storage helpers for the PSIRT translation pipeline."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .config import ADVISORY_STORE_PATH, TRANSLATION_CACHE_PATH

logger = logging.getLogger(__name__)


@dataclass
class TranslationCache:
    """Simple JSON-backed cache for translated text."""

    path: Path = TRANSLATION_CACHE_PATH
    _data: Dict[str, str] = field(default_factory=dict, init=False)
    _loaded: bool = field(default=False, init=False)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
                logger.debug("Loaded %d cached translations", len(self._data))
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse translation cache: %s", exc)
                self._data = {}
        self._loaded = True

    def get(self, text: str) -> Optional[str]:
        self._ensure_loaded()
        return self._data.get(text)

    def set(self, text: str, translation: str) -> None:
        self._ensure_loaded()
        self._data[text] = translation
        self._persist()

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class AdvisoryStore:
    """Persisted list of advisories that have been processed."""

    path: Path = ADVISORY_STORE_PATH
    _items: Dict[str, dict] = field(default_factory=dict, init=False)
    _loaded: bool = field(default=False, init=False)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                self._items = {item["link"]: item for item in raw}
                logger.debug("Loaded %d advisories from store", len(self._items))
            except json.JSONDecodeError as exc:
                logger.warning("Failed to parse advisory store: %s", exc)
                self._items = {}
        self._loaded = True

    def get_all(self) -> List[dict]:
        self._ensure_loaded()
        return sorted(self._items.values(), key=lambda item: item.get("published", ""), reverse=True)

    def upsert_many(self, advisories: Iterable[dict]) -> None:
        self._ensure_loaded()
        updated = 0
        for advisory in advisories:
            key = advisory.get("link")
            if not key:
                continue
            existing = self._items.get(key)
            if existing != advisory:
                self._items[key] = advisory
                updated += 1
        if updated:
            logger.info("Persisting %d updated advisories", updated)
            self._persist()

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        items = self.get_all()
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
