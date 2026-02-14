import time
import uuid
import asyncio
import functools
from .logger import logger


CALL_STACK = []


def trace(fn):

    if asyncio.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):

            trace_id = str(uuid.uuid4())[:8]
            start = time.perf_counter()

            CALL_STACK.append(fn.__name__)

            logger.bind(
                trace_id=trace_id,
                depth=len(CALL_STACK)
            ).info(f"{fn.__name__} started")

            try:
                result = await fn(*args, **kwargs)

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    trace_id=trace_id,
                    duration_ms=round(duration, 2)
                ).success(f"{fn.__name__} completed")

                return result

            except Exception as e:

                logger.bind(
                    trace_id=trace_id,
                    error=str(e)
                ).error(f"{fn.__name__} failed")

                raise

            finally:
                CALL_STACK.pop()

        return async_wrapper

    else:

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):

            trace_id = str(uuid.uuid4())[:8]
            start = time.perf_counter()

            CALL_STACK.append(fn.__name__)

            logger.bind(
                trace_id=trace_id,
                depth=len(CALL_STACK)
            ).info(f"{fn.__name__} started")

            try:
                result = fn(*args, **kwargs)

                duration = (time.perf_counter() - start) * 1000

                logger.bind(
                    trace_id=trace_id,
                    duration_ms=round(duration, 2)
                ).success(f"{fn.__name__} completed")

                return result

            except Exception as e:

                logger.bind(
                    trace_id=trace_id,
                    error=str(e)
                ).error(f"{fn.__name__} failed")

                raise

            finally:
                CALL_STACK.pop()

        return sync_wrapper
