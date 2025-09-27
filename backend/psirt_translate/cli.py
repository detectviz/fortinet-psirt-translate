"""Command line interface for the PSIRT translation pipeline."""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from .config import DEFAULT_FEED_URL
from .service import PSIRTService

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fortinet PSIRT advisory fetcher and translator")
    parser.add_argument("--feed-url", default=DEFAULT_FEED_URL, help="RSS feed URL to fetch")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of advisories to fetch")
    parser.add_argument("--output", type=Path, help="Optional output file path for JSON export")
    parser.add_argument("--interval", type=int, default=0, help="Repeat execution every N minutes (0 to disable)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def run_once(service: PSIRTService, feed_url: str, limit: Optional[int], output: Optional[Path]) -> None:
    advisories = service.refresh_advisories(feed_url, limit=limit)
    if output:
        service.export_to_file(advisories, output)
    else:
        print(advisories)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    service = PSIRTService()

    interval = args.interval or 0

    if interval <= 0:
        run_once(service, args.feed_url, args.limit, args.output)
        return 0

    logger.info("Starting scheduled execution every %s minutes", interval)
    try:
        while True:
            run_once(service, args.feed_url, args.limit, args.output)
            logger.info("Sleeping for %s minutes", interval)
            time.sleep(interval * 60)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        return 0
    except Exception as exc:  # pragma: no cover - defensive scheduling loop
        logger.exception("Scheduled execution failed: %s", exc)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
