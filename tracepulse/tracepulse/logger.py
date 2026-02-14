"""Logging helpers for Tracepulse.

This module prefers `loguru` but falls back to the stdlib `logging` module
when `loguru` is not available so basic demos and imports still work.
"""
from pathlib import Path
from typing import Optional, Any, Dict

# Try to import loguru; if not available create a minimal shim.
try:
    from loguru import logger  # type: ignore
    _HAS_LOGURU = True
except Exception:
    _HAS_LOGURU = False

import sys
import logging


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


if _HAS_LOGURU:
    # Keep track of the stdout sink so we can reconfigure level at runtime
    _STDOUT_SINK_ID: Optional[int] = None


    def _setup_logger(level: str = "INFO") -> None:
        global _STDOUT_SINK_ID
        logger.remove()
        _STDOUT_SINK_ID = logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level}</level> | "
                "{extra} | "
                "{message}"
            ),
            level=level,
        )

        logger.add(
            LOG_DIR / "tracepulse.log",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            serialize=True,
        )


    def set_level(level: str) -> None:
        """Set logging level for console output at runtime."""
        _setup_logger(level)


    # Initialize with default
    _setup_logger("INFO")

else:
    # Minimal stdlib logging shim with `bind` API used by the tracer.
    _root = logging.getLogger("tracepulse")
    _root.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    )
    if not _root.handlers:
        _root.addHandler(ch)


    class _SimpleLogger:
        def bind(self, **extra: Any) -> "_SimpleLogger":
            # simple shim: attach extras to the instance for the next call
            self._extra = extra
            return self

        def _fmt(self, msg: str) -> str:
            extra = getattr(self, "_extra", None)
            if extra:
                try:
                    return f"{extra} | {msg}"
                finally:
                    self._extra = None
            return msg

        def info(self, msg: str, *args, **kwargs) -> None:
            _root.info(self._fmt(msg), *args, **kwargs)

        def success(self, msg: str, *args, **kwargs) -> None:
            # no success level in stdlib; map to INFO
            _root.info(self._fmt(msg), *args, **kwargs)

        def error(self, msg: str, *args, **kwargs) -> None:
            _root.error(self._fmt(msg), *args, **kwargs)

    logger = _SimpleLogger()


    def set_level(level: str) -> None:
        lvl = getattr(logging, level.upper(), None)
        if lvl is None:
            return
        _root.setLevel(lvl)


__all__ = ["logger", "set_level", "LOG_DIR"]
