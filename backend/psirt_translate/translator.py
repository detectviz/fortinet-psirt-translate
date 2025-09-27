"""Translation helpers with caching and graceful fallbacks."""
from __future__ import annotations

import logging
from typing import Optional

try:  # pragma: no cover - import guard
    from googletrans import Translator as GoogleTranslator
except Exception as exc:  # pragma: no cover - graceful degradation
    GoogleTranslator = None  # type: ignore[assignment]

from .storage import TranslationCache

logger = logging.getLogger(__name__)


class TranslatorService:
    """Translate text to Traditional Chinese with caching."""

    def __init__(self, cache: Optional[TranslationCache] = None) -> None:
        self.cache = cache or TranslationCache()
        self._translator = None

    def _get_translator(self) -> Optional[GoogleTranslator]:  # type: ignore[name-defined]
        if self._translator is None and GoogleTranslator is not None:
            try:
                self._translator = GoogleTranslator(service_urls=["translate.googleapis.com"])
            except Exception as exc:  # pragma: no cover - network issues
                logger.error("Failed to initialise Google translator: %s", exc)
                self._translator = None
        return self._translator

    def translate(self, text: str) -> str:
        if not text:
            return ""
        cached = self.cache.get(text)
        if cached:
            logger.debug("Hit translation cache")
            return cached

        translator = self._get_translator()
        if translator is None:
            logger.warning("Translator unavailable, returning original text")
            return text

        try:
            result = translator.translate(text, dest="zh-TW")
            translated_text = getattr(result, "text", text)
            if translated_text:
                self.cache.set(text, translated_text)
            return translated_text
        except Exception as exc:  # pragma: no cover - googletrans errors are hard to predict
            logger.error("Translation failed: %s", exc)
            return text
