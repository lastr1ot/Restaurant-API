import asyncio

from arq.connections import RedisSettings

from config import settings


async def send_order_notif(ctx, order_id: int, table_id: int):
    print(f"wait {order_id}, {table_id}")
    await asyncio.sleep(3)
    print(f"ready {order_id}")


class WorkerSettings:
    functions = [send_order_notif]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
