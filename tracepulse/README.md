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
