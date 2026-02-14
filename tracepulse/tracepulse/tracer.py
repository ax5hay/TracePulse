import time
import random
import asyncio
import functools
import contextvars
from . import backends
from .logger import logger
from contextlib import contextmanager
from typing import Any, Callable, Optional, Dict


_TRACE_CONTEXT: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "tracepulse.context", default=None
)


def set_context(tags: Dict[str, Any]):
    """Set a trace context (returns a token for later reset)."""
    return _TRACE_CONTEXT.set(tags)


def clear_context(token=None):
    """Clear or reset the trace context. If `token` provided, resets to previous."""
    if token is not None:
        _TRACE_CONTEXT.reset(token)
    else:
        _TRACE_CONTEXT.set(None)


def _get_context() -> Dict[str, Any]:
    v = _TRACE_CONTEXT.get()
    return v.copy() if isinstance(v, dict) else {}


def trace(_fn: Optional[Callable] = None, *, capture_args: bool = False, tags: Optional[Dict[str, Any]] = None, sample_rate: float = 1.0):
    """Decorator to trace sync and async callables.

    Can be used as `@trace` or `@trace(capture_args=True, tags={...})`.
    """

    def decorator(fn: Callable):
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                fn_name = fn.__name__
                # decide whether to record this invocation (sampling)
                should_record = float(sample_rate) >= 1.0 or random.random() < float(sample_rate)

                extra = _get_context()
                if tags:
                    extra.update(tags)

                if capture_args:
                    try:
                        extra["args"] = str(args)[:200]
                        extra["kwargs"] = str(kwargs)[:200]
                    except Exception:
                        extra["args"] = "<unserializable>"

                if should_record:
                    logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = await fn(*args, **kwargs)

                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)

                    if should_record:
                        logger.bind(function=fn_name, **extra).success("Execution completed")
                    # Export to backend if configured
                    try:
                        backends.export({
                            "function": fn_name,
                            **extra,
                            "duration_ms": extra.get("duration_ms"),
                            "status": "ok",
                            "ts": time.time(),
                        })
                    except Exception:
                        pass
                    return result

                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)
                    extra["error"] = str(e)

                    logger.bind(function=fn_name, **extra).error("Execution failed")
                    if should_record:
                        try:
                            backends.export({
                                "function": fn_name,
                                **extra,
                                "status": "error",
                                "ts": time.time(),
                            })
                        except Exception:
                            pass
                    raise

            return async_wrapper

        else:

            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                fn_name = fn.__name__

                should_record = float(sample_rate) >= 1.0 or random.random() < float(sample_rate)

                extra = _get_context()
                if tags:
                    extra.update(tags)

                if capture_args:
                    try:
                        extra["args"] = str(args)[:200]
                        extra["kwargs"] = str(kwargs)[:200]
                    except Exception:
                        extra["args"] = "<unserializable>"

                if should_record:
                    logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = fn(*args, **kwargs)

                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)

                    if should_record:
                        logger.bind(function=fn_name, **extra).success("Execution completed")
                        try:
                            backends.export({
                                "function": fn_name,
                                **extra,
                                "duration_ms": extra.get("duration_ms"),
                                "status": "ok",
                                "ts": time.time(),
                            })
                        except Exception:
                            pass
                    return result

                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)
                    extra["error"] = str(e)

                    if should_record:
                        logger.bind(function=fn_name, **extra).error("Execution failed")
                        try:
                            backends.export({
                                "function": fn_name,
                                **extra,
                                "status": "error",
                                "ts": time.time(),
                            })
                        except Exception:
                            pass
                    raise

            return sync_wrapper

    # Support both @trace and @trace(...)
    if callable(_fn):
        return decorator(_fn)
    return decorator


@contextmanager
def trace_block(name: str, *, tags: Optional[Dict[str, Any]] = None, sample_rate: float = 1.0):
    """Context manager for tracing an arbitrary code block.

    Example:

        with trace_block("startup", tags={"phase":"init"}):
            do_startup()

    """
    start = time.perf_counter()
    extra = _get_context()
    if tags:
        extra.update(tags)

    should_record = float(sample_rate) >= 1.0 or random.random() < float(sample_rate)
    if should_record:
        logger.bind(function=name, **extra).info("Block started")
    try:
        yield
        duration = (time.perf_counter() - start) * 1000
        extra["duration_ms"] = round(duration, 2)
        if should_record:
            logger.bind(function=name, **extra).success("Block completed")
            try:
                backends.export({"function": name, **extra, "status": "ok", "ts": time.time()})
            except Exception:
                pass
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        extra["duration_ms"] = round(duration, 2)
        extra["error"] = str(e)
        if should_record:
            logger.bind(function=name, **extra).error("Block failed")
            try:
                backends.export({"function": name, **extra, "status": "error", "ts": time.time()})
            except Exception:
                pass
        raise
