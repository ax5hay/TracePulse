from typing import Any
from .config import settings

def safe_repr(obj: Any) -> str:
    """
    Safely return a string representation of an object.
    Catches exceptions during str() conversion to prevent crashing the app.
    Truncates long strings to avoid massive log files.
    """
    try:
        s = str(obj)
        if len(s) > settings.MAX_ARG_LENGTH:
            return s[:settings.MAX_ARG_LENGTH] + "..."
        return s
    except Exception:
        return "<unserializable>"