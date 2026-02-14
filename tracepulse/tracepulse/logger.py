import sys
from pathlib import Path
from loguru import logger


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


logger.remove()

logger.add(
    sys.stdout,
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "trace={extra[trace_id]} | "
        "{message}"
    ),
    level="INFO"
)

logger.add(
    LOG_DIR / "tracepulse.json",
    serialize=True,
    rotation="10 MB"
)
