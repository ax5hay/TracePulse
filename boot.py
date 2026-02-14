import os
from pathlib import Path


# =====================================
# Project Metadata
# =====================================

PROJECT_NAME = "tracepulse"
AUTHOR = "Akshay Bajpai"
DESCRIPTION = "Execution tracing & performance observability for Python services"


# =====================================
# Helper: File Writer
# =====================================

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[created] {path}")


root = Path(PROJECT_NAME)


# =====================================
# tracer.py
# =====================================

tracer_code = '''
import time
import functools
import asyncio
from .logger import logger


def trace(fn):
    """
    Execution tracing decorator supporting sync and async functions.
    Captures runtime duration, structured logs, and failure telemetry.
    """

    if asyncio.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):

            start = time.perf_counter()
            fn_name = fn.__name__

            logger.bind(function=fn_name).info("Execution started")

            try:
                result = await fn(*args, **kwargs)

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    function=fn_name,
                    duration_ms=round(duration, 2)
                ).success("Execution completed")

                return result

            except Exception as e:

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    function=fn_name,
                    duration_ms=round(duration, 2),
                    error=str(e)
                ).error("Execution failed")

                raise

        return async_wrapper

    else:

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):

            start = time.perf_counter()
            fn_name = fn.__name__

            logger.bind(function=fn_name).info("Execution started")

            try:
                result = fn(*args, **kwargs)

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    function=fn_name,
                    duration_ms=round(duration, 2)
                ).success("Execution completed")

                return result

            except Exception as e:

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    function=fn_name,
                    duration_ms=round(duration, 2),
                    error=str(e)
                ).error("Execution failed")

                raise

        return sync_wrapper
'''


# =====================================
# logger.py
# =====================================

logger_code = '''
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
'''


# =====================================
# __init__.py
# =====================================

init_code = '''
from .tracer import trace

__all__ = ["trace"]
'''


# =====================================
# pyproject.toml
# =====================================

pyproject_code = f'''
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{PROJECT_NAME}"
version = "0.1.0"
description = "{DESCRIPTION}"
authors = [{{ name="{AUTHOR}" }}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = ["loguru"]

[project.urls]
Homepage = "https://github.com/yourusername/{PROJECT_NAME}"
'''


# =====================================
# LICENSE
# =====================================

license_code = '''
MIT License

Copyright (c) 2026 Akshay Bajpai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
'''


# =====================================
# README.md
# =====================================

readme_code = '''
# Tracepulse

![PyPI](https://img.shields.io/pypi/v/tracepulse)
![License](https://img.shields.io/badge/license-MIT-blue)
![Downloads](https://img.shields.io/pypi/dm/tracepulse)

Tracepulse is a lightweight execution tracing and performance observability layer designed for backend and AI workloads where runtime visibility is critical.

It provides structured execution telemetry across synchronous and asynchronous code paths with minimal overhead.

---

## Why Tracepulse Exists

Modern AI and service pipelines execute complex multi-step logic, often without runtime transparency.

Tracepulse introduces deterministic tracing at the function boundary, enabling:

- Runtime performance visibility
- Failure surface detection
- Observability without external infra

---

## Features

- Sync + Async tracing
- Structured execution logs
- Failure telemetry capture
- Duration measurement (ms precision)
- Loguru-backed logging
- Zero configuration setup

---

## Installation

pip install tracepulse

---

## Usage

from tracepulse import trace

@trace
def compute():
    return sum(range(1_000_000))

compute()

---

## Async Example

import asyncio
from tracepulse import trace

@trace
async def fetch():
    await asyncio.sleep(1)

asyncio.run(fetch())

---

## Philosophy

Tracepulse is built on the principle that observability should exist at the code boundary — not only in external monitoring systems.

It is intentionally minimal, extensible, and production-safe.

---

## License

MIT
'''


# =====================================
# Create Files
# =====================================

write_file(root / "tracepulse" / "tracer.py", tracer_code)
write_file(root / "tracepulse" / "logger.py", logger_code)
write_file(root / "tracepulse" / "__init__.py", init_code)

write_file(root / "pyproject.toml", pyproject_code)
write_file(root / "README.md", readme_code)
write_file(root / "LICENSE", license_code)

print("\nTracepulse repository scaffolded successfully.")
print("Next steps:")
print("1. cd tracepulse")
print("2. git init")
print("3. python -m build")
print("4. twine upload dist/*")
