"""Basic tests for Tracepulse."""
import asyncio
from tracepulse import trace, trace_block, set_context, clear_context


def test_sync_trace():
    """Test sync function tracing."""
    @trace
    def add(a, b):
        return a + b

    result = add(2, 3)
    assert result == 5


def test_async_trace():
    """Test async function tracing."""
    @trace
    async def async_add(a, b):
        await asyncio.sleep(0.01)
        return a + b

    result = asyncio.run(async_add(2, 3))
    assert result == 5


def test_trace_block():
    """Test trace_block context manager."""
    with trace_block("test_operation", tags={"test": True}):
        x = sum(range(100))
    assert x == 4950


def test_context():
    """Test context helpers."""
    token = set_context({"request_id": "test-123"})
    assert token is not None
    clear_context(token)


def test_sampling():
    """Test sampling works without errors."""
    @trace(sample_rate=0.5)
    def maybe_traced():
        return 42

    result = maybe_traced()
    assert result == 42


if __name__ == "__main__":
    test_sync_trace()
    test_async_trace()
    test_trace_block()
    test_context()
    test_sampling()
    print("All tests passed!")
