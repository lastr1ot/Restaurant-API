from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from lifespan import lifespan
from middleware import measure_execution_time, rate_limit_middleware
from routers import health, orders
from routers.orders import OrderIsReady

app = FastAPI(title="Rest", lifespan=lifespan)

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(measure_execution_time)

app.include_router(orders.router)
app.include_router(health.router)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": "Database integrity error"})


@app.exception_handler(OrderIsReady)
async def order_ready_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=409, content={"detail": "Заказ готов"})
