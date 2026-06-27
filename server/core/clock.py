# server/core/clock.py
import asyncio

class Clock:
    def __init__(self, fps: int=60):
        self.fps = fps
        self.frame = 0
        self._condition = asyncio.Condition()

    async def run(self):
        while True:
            await asyncio.sleep(1 / self.fps)
            async with self._condition:
                self.frame += 1
                self._condition.notify_all()

    async def wait(self):
        async with self._condition:
            await self._condition.wait()