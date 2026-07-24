import asyncio
import os

DELAY=int(os.getenv("RELAY_DELAY_SECONDS","7"))

async def throttle():
    await asyncio.sleep(DELAY)


async def execute(task):
    await throttle()
    return await task()
