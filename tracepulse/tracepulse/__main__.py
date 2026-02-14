import asyncio
from . import trace, set_context, clear_context

@trace
def demo_sync(x):
    return x * 2

@trace(capture_args=True, tags={"demo": True})
async def demo_async(n):
    await asyncio.sleep(0.1)
    return sum(range(n))


def main():
    token = set_context({"request_id": "demo-123"})
    print("Running sync demo")
    print(demo_sync(3))

    print("Running async demo")
    asyncio.run(demo_async(1000))

    clear_context(token)


if __name__ == "__main__":
    main()
