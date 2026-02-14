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
