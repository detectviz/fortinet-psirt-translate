"""FastAPI application exposing PSIRT advisory endpoints."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from psirt_translate.config import DEFAULT_FEED_URL
from psirt_translate.service import PSIRTService

logger = logging.getLogger(__name__)

app = FastAPI(title="Fortinet PSIRT 公告翻譯器", version="1.0.0")
service = PSIRTService()


@app.get("/api/advisories")
def list_advisories(refresh: bool = False, limit: Optional[int] = None, feed_url: str = DEFAULT_FEED_URL):
    if refresh:
        logger.info("Refreshing advisories via API")
        advisories = service.refresh_advisories(feed_url, limit=limit)
    else:
        advisories = service.get_cached_advisories()
        if not advisories:
            advisories = service.refresh_advisories(feed_url, limit=limit)
    return {"items": advisories}


@app.post("/api/advisories/refresh")
def refresh_advisories(feed_url: str = DEFAULT_FEED_URL, limit: Optional[int] = None):
    advisories = service.refresh_advisories(feed_url, limit=limit)
    return {"items": advisories}


@app.get("/api/advisories/export")
def export_advisories(file_name: Optional[str] = None):
    advisories = service.get_cached_advisories()
    if not advisories:
        advisories = service.refresh_advisories(DEFAULT_FEED_URL)
    export_path = service.export_to_file(advisories, Path(file_name) if file_name else None)
    if not export_path.exists():
        raise HTTPException(status_code=500, detail="Export file not found")
    return FileResponse(export_path)


@app.post("/api/technical-terms/reload")
def reload_technical_terms():
    """Reload technical terms from configuration file."""
    success = service.reload_technical_terms()
    if success:
        count = service.get_technical_terms_count()
        return {"message": f"Successfully reloaded {count} technical terms"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reload technical terms")


@app.post("/api/technical-terms/add")
def add_technical_term(term: str):
    """Add a custom technical term to prevent translation."""
    if not term or not term.strip():
        raise HTTPException(status_code=400, detail="Term cannot be empty")

    term = term.strip()
    success = service.add_custom_technical_term(term)
    if success:
        return {"message": f"Successfully added technical term: {term}"}
    else:
        raise HTTPException(status_code=400, detail=f"Term already exists or failed to add: {term}")


@app.get("/api/technical-terms/count")
def get_technical_terms_count():
    """Get the count of loaded technical terms."""
    count = service.get_technical_terms_count()
    return {"count": count}
