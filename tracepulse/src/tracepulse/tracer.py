import time
import random
import asyncio
import functools
import contextvars
from contextlib import contextmanager
from typing import Any, Callable, Optional, Dict

from . import backends
from .logger import logger
from .config import settings
from .utils import safe_repr

# Context variable for storing trace tags (Request IDs, User IDs, etc.)
_TRACE_CONTEXT: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar(
    "tracepulse.context", default=None
)


def set_context(tags: Dict[str, Any]):
    """Set context tags for the current execution flow. Returns a token for resetting."""
    return _TRACE_CONTEXT.set(tags)


def clear_context(token=None):
    """Reset context to previous state."""
    if token:
        _TRACE_CONTEXT.reset(token)
    else:
        _TRACE_CONTEXT.set(None)


def _get_context() -> Dict[str, Any]:
    v = _TRACE_CONTEXT.get()
    return v.copy() if isinstance(v, dict) else {}


def _should_record(sample_rate: float) -> bool:
    """Decide if this trace should be recorded based on sampling rate."""
    if not settings.ENABLED:
        return False
    # Use config default if function arg is default (1.0), else use function arg
    rate = sample_rate if sample_rate != 1.0 else settings.SAMPLE_RATE
    return rate >= 1.0 or random.random() < rate


def trace(_fn: Optional[Callable] = None, *, capture_args: Optional[bool] = None, tags: Optional[Dict[str, Any]] = None, sample_rate: float = 1.0):
    """
    Decorator to trace sync and async callables.
    Usage: @trace or @trace(capture_args=True, tags={'layer': 'db'})
    """
    
    def decorator(fn: Callable):
        fn_name = fn.__name__
        
        # Determine capture setting (decorator param overrides config)
        do_capture = capture_args if capture_args is not None else settings.CAPTURE_ARGS

        def _prepare_extra(args, kwargs):
            extra = _get_context()
            if tags:
                extra.update(tags)
            if do_capture:
                # Use safe_repr to prevent crashes
                extra["args"] = safe_repr(args)
                extra["kwargs"] = safe_repr(kwargs)
            return extra

        def _emit(event_type, name, extra, duration, status, error=None):
            payload = {
                "function": name,
                **extra,
                "duration_ms": duration,
                "status": status,
                "ts": time.time()
            }
            if error:
                payload["error"] = error
            
            # Log to console/file via logger
            log_method = logger.bind(function=name, **extra).success if status == "ok" else logger.bind(function=name, **extra).error
            log_msg = f"Execution {event_type}"
            log_method(log_msg)
            
            # Export to backends
            backends.export(payload)

        # -- ASYNC WRAPPER --
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                if not _should_record(sample_rate):
                    return await fn(*args, **kwargs)

                start = time.perf_counter()
                extra = _prepare_extra(args, kwargs)
                logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = await fn(*args, **kwargs)
                    duration = round((time.perf_counter() - start) * 1000, 2)
                    _emit("completed", fn_name, extra, duration, "ok")
                    return result
                except Exception as e:
                    duration = round((time.perf_counter() - start) * 1000, 2)
                    _emit("failed", fn_name, extra, duration, "error", str(e))
                    raise
            return async_wrapper

        # -- SYNC WRAPPER --
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                if not _should_record(sample_rate):
                    return fn(*args, **kwargs)

                start = time.perf_counter()
                extra = _prepare_extra(args, kwargs)
                logger.bind(function=fn_name, **extra).info("Execution started")

                try:
                    result = fn(*args, **kwargs)
                    duration = round((time.perf_counter() - start) * 1000, 2)
                    _emit("completed", fn_name, extra, duration, "ok")
                    return result
                except Exception as e:
                    duration = round((time.perf_counter() - start) * 1000, 2)
                    _emit("failed", fn_name, extra, duration, "error", str(e))
                    raise
            return sync_wrapper

    # Support both @trace and @trace(...)
    if callable(_fn):
        return decorator(_fn)
    return decorator


@contextmanager
def trace_block(name: str, *, tags: Optional[Dict[str, Any]] = None, sample_rate: float = 1.0):
    """
    Context manager for tracing arbitrary code blocks.
    Usage: with trace_block("my_block"): ...
    """
    if not _should_record(sample_rate):
        yield
        return

    start = time.perf_counter()
    extra = _get_context()
    if tags:
        extra.update(tags)
    
    logger.bind(function=name, **extra).info("Block started")
    
    try:
        yield
        duration = round((time.perf_counter() - start) * 1000, 2)
        logger.bind(function=name, **extra).success("Block completed")
        backends.export({"function": name, **extra, "duration_ms": duration, "status": "ok", "ts": time.time()})
    except Exception as e:
        duration = round((time.perf_counter() - start) * 1000, 2)
        logger.bind(function=name, **extra).error("Block failed")
        backends.export({"function": name, **extra, "duration_ms": duration, "status": "error", "error": str(e), "ts": time.time()})
        raise