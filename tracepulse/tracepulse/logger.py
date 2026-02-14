from loguru import logger
import sys
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


logger.remove()

logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "{extra} | "
        "{message}"
    ),
    level="INFO"
)

logger.add(
    LOG_DIR / "tracepulse.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    serialize=True
)
