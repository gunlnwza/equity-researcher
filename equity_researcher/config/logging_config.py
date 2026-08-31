import logging
import os
from logging.config import dictConfig


DEFAULT_LOG_LEVEL = "INFO"


def configure_logging() -> None:
    """Configure application logging from the LOG_LEVEL environment variable."""
    level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    if level not in logging.getLevelNamesMapping():
        raise ValueError(f"Invalid LOG_LEVEL: {level}")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": level,
                    "stream": "ext://sys.stderr",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
            "loggers": {
                "httpx": {"level": "WARNING"},
                "openai": {"level": "WARNING"},
            },
        }
    )
