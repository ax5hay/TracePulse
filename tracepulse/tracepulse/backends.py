"""Simple backends for Tracepulse.

Current implementation: a very small file-backed exporter that appends
JSON-lines with trace events. This is intentionally tiny and synchronous
so it is safe as an optional helper.
"""
from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Dict, Any, Optional

_file_path: Optional[Path] = None
_lock = Lock()


def enable_file_backend(path: str) -> None:
    """Enable writing trace events to a newline-delimited JSON file."""
    global _file_path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    _file_path = p


def disable_backend() -> None:
    global _file_path
    _file_path = None


def _write_event(event: Dict[str, Any]) -> None:
    if _file_path is None:
        return
    s = json.dumps(event, default=str, separators=(',', ':'))
    with _lock:
        with _file_path.open('a', encoding='utf-8') as fh:
            fh.write(s + "\n")


def export(event: Dict[str, Any]) -> None:
    """Export a single trace event to the enabled backend(s)."""
    _write_event(event)
