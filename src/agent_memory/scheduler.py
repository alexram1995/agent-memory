import asyncio

class InferenceScheduler:
    """Serialize generation requests to avoid competing GPU inference."""
    def __init__(self, max_queue=20):
        self._lock = asyncio.Lock()
        self.max_queue = max_queue
        self._waiting = 0

    async def run(self, fn, *args, **kwargs):
        if self._waiting >= self.max_queue:
            raise RuntimeError("Inference queue is full")
        self._waiting += 1
        try:
            async with self._lock:
                return await fn(*args, **kwargs)
        finally:
            self._waiting -= 1
