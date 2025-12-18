from __future__ import annotations

"""
Central logging configuration for the PROLY Payroll Management System.

Import and call configure_logging() once at application startup.
"""

import logging
import os


def configure_logging(level: int | None = None) -> None:
    """
    Configure root logging for the application.

    Log level can be overridden via the LOG_LEVEL environment variable
    (e.g., DEBUG, INFO, WARNING, ERROR).
    """
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


