# Tracepulse

[![Version](https://img.shields.io/badge/version-0.1.5-blue.svg)]
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]

<!-- NOTE: The dynamic PyPI badges (pypi/v, pypi/pyversions, pypi/dm) will show valid data after the package is published to PyPI under the same name. Currently these are shown as local/static badges to avoid "not found" images. -->

Lightweight execution tracing and performance observability for synchronous and asynchronous Python code.

Table of Contents
- Features
- Quickstart
- Usage
  - Sync example
  - Async example
- Configuration & Context
- Advanced
- Suggested features
- License
- Release / PyPI

Tracepulse provides a simple decorator-based tracer that records function start/end, duration (ms precision), exceptions, and structured logs compatible with Loguru. It's intentionally minimal and safe for production use.

**Highlights**
- Zero configuration decorator: `@trace`
- Works with sync and async callables
- Structured, minimal overhead logs
- Integrates with `loguru` for flexible output

## Features

- Sync and Async tracing
- Structured execution logs (function name, args summary, duration)
- Failure telemetry capture (exception type, message, traceback)
- Duration measurement (millisecond precision)
- Loguru-backed logging integration (fallbacks to stdlib logging if `loguru` is unavailable)
- Minimal surface area and runtime overhead

## Quickstart

Install (from PyPI after publishing):

```bash
# once published to PyPI
pip install tracepulse
```

Then add the tracer to a function:

```python
from tracepulse import trace

@trace
def compute():
    return sum(range(1_000_000))

compute()
```

## Usage

Sync example

```python
from tracepulse import trace

@trace
def heavy_work(x):
    # your work here
    return x * 2

heavy_work(10)
```

Async example

```python
import asyncio
from tracepulse import trace

@trace
async def fetch():
    await asyncio.sleep(1)

asyncio.run(fetch())
```

Notes:
- `@trace` can be applied to any callable; it preserves function signature and return value.
- For heavy throughput code, prefer adding `@trace` at higher-level boundaries (handlers, tasks) rather than inner hot loops.

## Configuration & Context

- `set_level(level_str)` — programmatically adjust console logging level (e.g., `set_level("DEBUG")`).
- `set_context(dict)` — attach context tags to subsequent traces (returns a token). Example:

```python
from tracepulse import set_context, clear_context

token = set_context({"request_id": "abcd-1234"})
# traces will include `request_id`
clear_context(token)  # reset
```

These helpers let you add lightweight, application-level context to trace events without a heavy propagation system.

New helpers

- `enable_file_backend(path)` — write trace events as newline-delimited JSON to `path`.
- `trace_block(name, tags=None, sample_rate=1.0)` — context manager for tracing arbitrary code blocks.
- `trace(..., sample_rate=0.1)` — decorator now supports sampling via `sample_rate` (0.0-1.0).

## Advanced

- Logging: Tracepulse uses `loguru` internally by default; if `loguru` is not installed the package falls back to the stdlib `logging` module so basic demos and imports still work.
- Data captured: function name, arg summary (optional), start timestamp, end timestamp, duration_ms, exception info (if any), and optional context tags.

## Suggested / Future Features

- Pluggable backends (send traces to file/HTTP/OTel)
- Context propagation across threads/processes
- Sampled tracing to reduce overhead for very high throughput
- Richer argument serialization and PII scrubbing hooks
- CLI tooling to visualize recent traces locally




## Release / PyPI
Steps:

```bash

python -m build
python -m twine upload dist/*

## Changelog

- v0.1.1 — Documentation improvements, README refresh, version bump
- v0.1.2 — Added context helpers, runtime `set_level`, and demo CLI
- v0.1.3 — Added backend exporter (file), `trace_block`, sampling support, and README beautification


