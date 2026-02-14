import time
import asyncio
import functools
import contextvars
from .logger import logger
from typing import Any, Callable, Optional, Dictfrom .logger import loggerfrom typing import Any, Callable, Optional, Dictfrom .logger import logger


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


def trace(_fn: Optional[Callable] = None, *, capture_args: bool = False, tags: Optional[Dict[str, Any]] = None):
    """Decorator to trace sync and async callables.

    Can be used as `@trace` or `@trace(capture_args=True, tags={...})`.
    """

    def decorator(fn: Callable):
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                fn_name = fn.__name__

                extra = _get_context()
                if tags:
                    extra.update(tags)

                if capture_args:
                    try:
                        extra["args"] = str(args)[:200]
                        extra["kwargs"] = str(kwargs)[:200]
                    except Exception:
                        extra["args"] = "<unserializable>"

                logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = await fn(*args, **kwargs)

                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)

                    logger.bind(function=fn_name, **extra).success("Execution completed")
                    return result

                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)
                    extra["error"] = str(e)

                    logger.bind(function=fn_name, **extra).error("Execution failed")
                    raise

            return async_wrapper

        else:

            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                fn_name = fn.__name__

                extra = _get_context()
                if tags:
                    extra.update(tags)

                if capture_args:
                    try:
                        extra["args"] = str(args)[:200]
                        extra["kwargs"] = str(kwargs)[:200]
                    except Exception:
                        extra["args"] = "<unserializable>"

                logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = fn(*args, **kwargs)

                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)

                    logger.bind(function=fn_name, **extra).success("Execution completed")
                    return result

                except Exception as e:
                    duration = (time.perf_counter() - start) * 1000
                    extra["duration_ms"] = round(duration, 2)
                    extra["error"] = str(e)

                    logger.bind(function=fn_name, **extra).error("Execution failed")
                    raise

            return sync_wrapper

    # Support both @trace and @trace(...)
    if callable(_fn):
        return decorator(_fn)
    return decorator
