from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from config import settings
from database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.queue = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))

    yield

    await app.state.queue.close()
    await app.state.redis.aclose()
    await engine.dispose()
