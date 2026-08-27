import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import OrderDB
from dependencies import get_db, get_queue, get_redis
from schemas import OrderCreate, OrderResponse, OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

ORDERS_CACHE_KEY = "orders:list"
ORDERS_CACHE_TTL = 60


class OrderIsReady(Exception):
    """Заказ уже готов"""


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    r=Depends(get_redis),
    q=Depends(get_queue),
):
    db_order = OrderDB(
        table_id=order.table_id,
        items=[item.model_dump(mode="json") for item in order.items],
        total_price=order.total_price,
        status=OrderStatus.NEW.value,
    )
    db.add(db_order)
    await db.commit()
    await r.delete(ORDERS_CACHE_KEY)
    await db.refresh(db_order)

    await q.enqueue_job("send_order_notif", db_order.id, db_order.table_id)

    return OrderResponse(
        id=db_order.id,
        table_id=db_order.table_id,
        items=db_order.items,
        total_price=db_order.total_price,
        status=db_order.status,
    )


@router.get("", response_model=list[OrderResponse])
async def get_all_orders(db: AsyncSession = Depends(get_db), r=Depends(get_redis)):
    cached = await r.get(ORDERS_CACHE_KEY)
    if cached is not None:
        return json.loads(cached)

    result = await db.execute(select(OrderDB))
    orders = result.scalars().all()

    data = [
        OrderResponse(
            id=o.id, table_id=o.table_id, items=o.items, total_price=o.total_price, status=o.status
        )
        for o in orders
    ]

    await r.set(
        ORDERS_CACHE_KEY, json.dumps([d.model_dump(mode="json") for d in data]), ex=ORDERS_CACHE_TTL
    )
    return data


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.get(OrderDB, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return OrderResponse(
        id=result.id,
        table_id=result.table_id,
        items=result.items,
        total_price=result.total_price,
        status=result.status,
    )


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int, new_status: OrderStatus, db: AsyncSession = Depends(get_db), r=Depends(get_redis)
):
    result = await db.get(OrderDB, order_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Заказ {order_id} не найден")

    if result.status == OrderStatus.READY.value:
        raise OrderIsReady()

    result.status = new_status.value
    await db.commit()
    await r.delete(ORDERS_CACHE_KEY)

    return {"message": "Статус обновлен", "order_id": order_id, "status": new_status.value}


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int, order: OrderCreate, db: AsyncSession = Depends(get_db), r=Depends(get_redis)
):
    result = await db.get(OrderDB, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    result.table_id = order.table_id
    result.items = [item.model_dump(mode="json") for item in order.items]
    result.total_price = order.total_price
    await db.commit()
    await r.delete(ORDERS_CACHE_KEY)
    await db.refresh(result)

    return OrderResponse(
        id=result.id,
        table_id=result.table_id,
        items=result.items,
        total_price=result.total_price,
        status=result.status,
    )
