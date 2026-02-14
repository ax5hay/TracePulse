import sys
import logging
from typing import Any
from pathlib import Path
from .config import settings

# Try to import loguru
try:
    from loguru import logger as _loguru_logger # type: ignore
    _HAS_LOGURU = True
except ImportError:
    _HAS_LOGURU = False

logger: Any = None

def _configure_loguru():
    global logger
    logger = _loguru_logger
    logger.remove()
    
    # Console Sink
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {extra} | {message}",
        level=settings.LOG_LEVEL,
    )
    
    # File Sink (Rotating)
    log_path = Path(settings.LOG_DIR) / "tracepulse.log"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        serialize=True,
        level=settings.LOG_LEVEL
    )

def _configure_stdlib():
    global logger
    _root = logging.getLogger("tracepulse")
    _root.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    
    if not _root.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
        _root.addHandler(ch)

    # Shim class to mimic loguru's .bind() API
    class _SimpleLogger:
        def bind(self, **extra: Any):
            self._extra = extra
            return self

        def _fmt(self, msg: str):
            extra = getattr(self, "_extra", None)
            if extra:
                # Flatten extras for simple display
                return f"{extra} | {msg}" 
            return msg

        def info(self, msg, *args, **kwargs):
            _root.info(self._fmt(msg), *args, **kwargs)
        
        def success(self, msg, *args, **kwargs):
            # Stdlib doesn't have success, map to info
            _root.info(self._fmt(msg), *args, **kwargs)
            
        def error(self, msg, *args, **kwargs):
            _root.error(self._fmt(msg), *args, **kwargs)
            
        def warning(self, msg, *args, **kwargs):
            _root.warning(self._fmt(msg), *args, **kwargs)

    logger = _SimpleLogger()


if _HAS_LOGURU:
    _configure_loguru()
else:
    _configure_stdlib()


def set_level(level: str):
    """Runtime level switcher."""
    # Note: Complex runtime switching for loguru/stdlib is simplified here 
    # to avoid bloated code. For v1.0, restart is recommended for level changes.
    pass