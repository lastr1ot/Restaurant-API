import time

from fastapi import Request
from fastapi.responses import JSONResponse

RATE_LIMIT = 10
RATE_WINDOW = 60


async def rate_limit_middleware(request: Request, call_next):
    r = request.app.state.redis
    host = request.client.host if request.client else "unknown"
    key = f"rate:{host}"

    count = await r.incr(key)
    if count == 1:
        await r.expire(key, RATE_WINDOW)

    if count > RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Слишком много запросов"})

    return await call_next(request)


async def measure_execution_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    process_time = end_time - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f} sec"
    print(f"{request.method} {request.url} выполнился за {process_time:.4f} sec")
    return response
