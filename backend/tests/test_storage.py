from pathlib import Path

from psirt_translate.storage import AdvisoryStore, TranslationCache


def test_translation_cache_roundtrip(tmp_path: Path):
    cache = TranslationCache(path=tmp_path / "cache.json")
    assert cache.get("hello") is None
    cache.set("hello", "你好")
    assert cache.get("hello") == "你好"


def test_advisory_store_upsert(tmp_path: Path):
    store = AdvisoryStore(path=tmp_path / "advisories.json")
    store.upsert_many([
        {"link": "a", "published": "2024-01-01", "title_en": "A"},
        {"link": "b", "published": "2024-01-02", "title_en": "B"},
    ])
    items = store.get_all()
    assert len(items) == 2
    # Ensure ordering by published desc
    assert items[0]["link"] == "b"

    store.upsert_many([
        {"link": "a", "published": "2024-01-03", "title_en": "A2"},
    ])
    items = store.get_all()
    assert items[0]["link"] == "a"
    assert items[0]["title_en"] == "A2"
