from __future__ import annotations

import logging
import os
from typing import Iterable


def configure_logging(extra_loggers: Iterable[str] | None = None) -> None:
    """Configure application logging.

    Respects LOG_LEVEL env var (default INFO). Sets a concise format and
    enables DEBUG for selected libraries when requested.
    """

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    # Quiet overly verbose loggers unless explicitly debugging
    noisy = [
        "uvicorn.access",
        "urllib3",
    ]
    for name in noisy:
        logging.getLogger(name).setLevel(logging.WARNING if level > logging.DEBUG else level)

    # Optionally elevate specific loggers
    if extra_loggers:
        for name in extra_loggers:
            logging.getLogger(name).setLevel(level)

