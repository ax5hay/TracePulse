import os
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration loaded from Environment Variables."""
    ENABLED: bool = os.getenv("TRACEPULSE_ENABLED", "true").lower() == "true"
    SAMPLE_RATE: float = float(os.getenv("TRACEPULSE_SAMPLE_RATE", "1.0"))
    LOG_LEVEL: str = os.getenv("TRACEPULSE_LOG_LEVEL", "INFO").upper()
    LOG_DIR: str = os.getenv("TRACEPULSE_LOG_DIR", "logs")
    CAPTURE_ARGS: bool = os.getenv("TRACEPULSE_CAPTURE_ARGS", "false").lower() == "true"
    # Max length for captured arguments to prevent log bloating
    MAX_ARG_LENGTH: int = int(os.getenv("TRACEPULSE_MAX_ARG_LENGTH", "500"))

settings = Config()