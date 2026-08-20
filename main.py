from fastapi import FastAPI, HTTPException, Depends
from models import OrderStatus, OrderCreate, OrderResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import asyncio
from database import Base, OrderDB

engine = create_async_engine("sqlite+aiosqlite:///./restaraunt.db", echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(title="Rest", lifespan=lifespan)
async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session



@app.post("/order", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    db_order = OrderDB(
        table_id = order.table_id,
        items = ", ".join(order.items),
        total_price = order.total_price,
        status = OrderStatus.NEW.value
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    return OrderResponse(
        id = db_order.id,
        table_id = db_order.table_id,
        items = order.items,
        total_price = db_order.total_price,
        status = db_order.status
    )

@app.get("/orders", response_model=list[OrderResponse])
async def get_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OrderDB))
    orders = result.scalars().all()
    return [
        OrderResponse(
            id = o.id,
            table_id = o.table_id,
            items = o.items.split(", "),
            total_price = o.total_price,
            status = o.status
        )
        for o in orders
    ]

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.get(OrderDB, order_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Заказ {order_id} не найден")

    return OrderResponse(
        id = result.id,
        table_id = result.table_id,
        items = result.items.split(", "),
        total_price = result.total_price,
        status = result.status
    )

@app.patch("/orders/{order_id}/status")
async def update_order_status(order_id: int, new_status: OrderStatus, db: AsyncSession = Depends(get_db)):
    result = await db.get(OrderDB, order_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Заказ{order_id} не найден")

    result.status = new_status.value
    await db.commit()
    return {
        "message": "Статус обновлен", 
        "order_id": order_id,
        "status": new_status.value
    }