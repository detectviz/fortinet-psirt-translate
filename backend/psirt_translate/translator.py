"""Translation helpers with caching and graceful fallbacks."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional, Set

try:  # pragma: no cover - import guard
    from googletrans import Translator as GoogleTranslator
except Exception as exc:  # pragma: no cover - graceful degradation
    GoogleTranslator = None  # type: ignore[assignment]

from .storage import TranslationCache

logger = logging.getLogger(__name__)


class TranslatorService:
    """Translate text to Traditional Chinese with caching."""

    def __init__(self, cache: Optional[TranslationCache] = None, technical_terms_file: Optional[Path] = None) -> None:
        self.cache = cache or TranslationCache()
        self._translator = None
        self._loop = None
        self._technical_terms_file = technical_terms_file or Path(__file__).parent / "technical_terms.json"
        self._technical_terms: Set[str] = set()
        self._tech_term_pattern: Optional[re.Pattern] = None

        # Load technical terms from config file
        self._load_technical_terms()

    def _load_technical_terms(self) -> None:
        """Load technical terms from JSON configuration file."""
        try:
            if self._technical_terms_file.exists():
                with open(self._technical_terms_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Combine all term categories into a single set
                self._technical_terms = set()
                for category_terms in data.values():
                    if isinstance(category_terms, list):
                        self._technical_terms.update(category_terms)

                logger.info(f"Loaded {len(self._technical_terms)} technical terms from {self._technical_terms_file}")

                # Recompile regex pattern
                self._tech_term_pattern = re.compile(
                    r'\b(' + '|'.join(re.escape(term) for term in self._technical_terms) + r')\b',
                    re.IGNORECASE
                )
            else:
                logger.warning(f"Technical terms file not found: {self._technical_terms_file}")
                self._technical_terms = set()
                self._tech_term_pattern = None

        except Exception as exc:
            logger.error(f"Failed to load technical terms from {self._technical_terms_file}: {exc}")
            self._technical_terms = set()
            self._tech_term_pattern = None

    def reload_technical_terms(self) -> bool:
        """Reload technical terms from configuration file. Returns True if successful."""
        try:
            self._load_technical_terms()
            return True
        except Exception as exc:
            logger.error(f"Failed to reload technical terms: {exc}")
            return False

    def add_custom_term(self, term: str) -> bool:
        """Add a custom technical term to the list."""
        try:
            if term not in self._technical_terms:
                self._technical_terms.add(term)

                # Reload from file and add the new term
                if self._technical_terms_file.exists():
                    with open(self._technical_terms_file, 'r+', encoding='utf-8') as f:
                        data = json.load(f)
                        if "custom_terms" not in data:
                            data["custom_terms"] = []
                        if term not in data["custom_terms"]:
                            data["custom_terms"].append(term)

                        # Write back to file
                        f.seek(0)
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        f.truncate()

                # Recompile pattern
                self._tech_term_pattern = re.compile(
                    r'\b(' + '|'.join(re.escape(t) for t in self._technical_terms) + r')\b',
                    re.IGNORECASE
                )
                logger.info(f"Added custom technical term: {term}")
                return True
            return False
        except Exception as exc:
            logger.error(f"Failed to add custom term '{term}': {exc}")
            return False

    def _get_translator(self) -> Optional[GoogleTranslator]:  # type: ignore[name-defined]
        if self._translator is None and GoogleTranslator is not None:
            try:
                self._translator = GoogleTranslator(service_urls=["translate.googleapis.com"])
            except Exception as exc:  # pragma: no cover - network issues
                logger.error("Failed to initialise Google translator: %s", exc)
                self._translator = None
        return self._translator

    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def _protect_technical_terms(self, text: str) -> tuple[str, dict[str, str]]:
        """Replace technical terms with placeholders to prevent translation.

        Returns:
            tuple: (protected_text, term_mapping)
        """
        if not self._tech_term_pattern:
            return text, {}

        protected_terms = {}
        placeholder_counter = 0

        def replace_match(match):
            nonlocal placeholder_counter
            term = match.group(0)
            # Use a placeholder that won't be affected by translation
            placeholder = f"[TECH_{placeholder_counter}]"
            protected_terms[placeholder] = term
            placeholder_counter += 1
            return placeholder

        protected_text = self._tech_term_pattern.sub(replace_match, text)
        return protected_text, protected_terms

    def _restore_technical_terms(self, text: str, term_mapping: dict[str, str]) -> str:
        """Restore technical terms from placeholders."""
        for placeholder, original_term in term_mapping.items():
            # Google Translate may change case, so we need to handle case variations
            # Use regex to find placeholders regardless of case changes
            import re
            # Escape special regex characters and create case-insensitive pattern
            escaped_placeholder = re.escape(placeholder)
            pattern = re.compile(escaped_placeholder, re.IGNORECASE)
            text = pattern.sub(original_term, text)
        return text

    def _protect_technical_terms(self, text: str) -> tuple[str, dict[str, str]]:
        """Replace technical terms with placeholders to prevent translation.

        Returns:
            tuple: (protected_text, term_mapping)
        """
        if not self._tech_term_pattern:
            return text, {}

        protected_terms = {}
        placeholder_counter = 0

        def replace_match(match):
            nonlocal placeholder_counter
            term = match.group(0)
            # Use a placeholder that won't be affected by translation
            placeholder = f"[TECH_{placeholder_counter}]"
            protected_terms[placeholder] = term
            placeholder_counter += 1
            return placeholder

        protected_text = self._tech_term_pattern.sub(replace_match, text)
        return protected_text, protected_terms

    async def _translate_async(self, text: str) -> str:
        """Async translation method."""
        translator = self._get_translator()
        if translator is None:
            return text

        try:
            result = await translator.translate(text, dest="zh-TW")
            return getattr(result, "text", text)
        except Exception as exc:
            logger.error("Async translation failed: %s", exc)
            return text

    def translate(self, text: str) -> str:
        if not text:
            return ""
        cached = self.cache.get(text)
        if cached:
            logger.debug("Hit translation cache")
            return cached

        try:
            # Protect technical terms before translation
            protected_text, term_mapping = self._protect_technical_terms(text)

            # Skip translation if text only contains technical terms
            if not term_mapping:
                # No technical terms found, translate normally
                loop = self._get_event_loop()
                translated_text = loop.run_until_complete(self._translate_async(text))
            elif protected_text == text:
                # Text consists only of technical terms, no translation needed
                translated_text = text
            else:
                # Translate the protected text
                loop = self._get_event_loop()
                translated_protected = loop.run_until_complete(self._translate_async(protected_text))

                # Only proceed if translation succeeded and returned different text
                if translated_protected and translated_protected != protected_text:
                    # Restore technical terms
                    translated_text = self._restore_technical_terms(translated_protected, term_mapping)
                else:
                    # Translation failed or returned same text, don't translate
                    translated_text = text

            # Only cache if we have a valid translation that's different from original
            if translated_text and translated_text != text and not any(f"[TECH_{i}]" in translated_text for i in range(10)):
                self.cache.set(text, translated_text)
            return translated_text
        except Exception as exc:  # pragma: no cover - googletrans errors are hard to predict
            logger.error("Translation failed: %s", exc)
            # Don't cache failed translations
            return text
