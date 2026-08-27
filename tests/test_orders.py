import pytest
from conftest import app, get_db
from factories import make_order_payload


async def test_create_order(client, queue):
    payload = {
        "table_id": 5,
        "items": [
            {"name": "Pizza", "quantity": 1, "price": 500.0},
            {"name": "Cola", "quantity": 2, "price": 245.25},
        ],
        "total_price": 990.5,
    }
    resp = await client.post("/orders", json=payload)
    assert resp.status_code == 201
    assert len(queue.jobs) == 1

    data = resp.json()
    assert data["table_id"] == 5
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Pizza"
    assert data["status"] == "new"
    assert "id" in data


async def test_get_order_not_found(client):
    resp = await client.get("/orders/0")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Заказ не найден"}


async def test_get_order_invalid_id(client):
    resp = await client.get("/orders/a")
    assert resp.status_code == 422


async def test_update_status(client, queue):
    payload = make_order_payload(
        table_id=5,
        items=[
            {"name": "Pizza", "quantity": 1, "price": 800},
            {"name": "Sushi", "quantity": 1, "price": 400},
        ],
        total_price=1200,
    )
    resp = await client.post("/orders", json=payload)
    assert resp.status_code == 201
    order_id = resp.json()["id"]
    assert len(queue.jobs) == 1

    resp = await client.patch(f"/orders/{order_id}/status", params={"new_status": "cooking"})
    assert resp.json() == {"message": "Статус обновлен", "order_id": order_id, "status": "cooking"}

    resp = await client.get(f"/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cooking"


@pytest.mark.parametrize(
    "payload",
    [
        {"table_id": 1, "items": [{"name": "X", "quantity": 1, "price": 10}], "total_price": -5},
        {"table_id": 2, "items": [], "total_price": 100},
        {"table_id": -3, "items": [{"name": "X", "quantity": 1, "price": 10}], "total_price": 100},
    ],
)
async def test_create_order_valid_error(client, payload, queue):
    resp = await client.post("/orders", json=payload)
    assert resp.status_code == 422
    assert queue.jobs == []


async def test_job_enqueued_with_args(client, queue):
    resp = await client.post("/orders", json=make_order_payload(table_id=5, total_price=1000))
    assert resp.status_code == 201
    assert len(queue.jobs) == 1
    name, args, kwargs = queue.jobs[0]
    assert name == "send_order_notif"
    assert args == (resp.json()["id"], 5)


async def test_invalid_order_does_not_enqueue(client, queue):
    resp = await client.post("/orders", json=make_order_payload(total_price=-5))
    assert resp.status_code == 422
    assert queue.jobs == []


async def test_process_time_header(client):
    resp = await client.get("/orders")
    assert resp.status_code == 200
    assert "X-Process-Time" in resp.headers
    value = resp.headers["X-Process-Time"]
    number = float(value.replace(" sec", ""))
    assert number >= 0


async def test_ready_order_status_conflict(client, queue):
    resp = await client.post(
        "/orders",
        json=make_order_payload(
            table_id=6, items=[{"name": "Pepper", "quantity": 1, "price": 600}], total_price=600
        ),
    )
    assert resp.status_code == 201
    assert len(queue.jobs) == 1
    order_id = resp.json()["id"]

    resp = await client.patch(f"/orders/{order_id}/status", params={"new_status": "ready"})
    assert resp.status_code == 200
    assert len(queue.jobs) == 1

    resp = await client.patch(f"/orders/{order_id}/status", params={"new_status": "cooking"})
    assert resp.status_code == 409

    resp = await client.get(f"/orders/{order_id}")
    assert resp.json()["status"] == "ready"


async def test_db_down_return_500(client, queue):
    async def broken_get_db():
        raise RuntimeError("DB down")

    app.dependency_overrides[get_db] = broken_get_db
    resp = await client.post("/orders", json=make_order_payload())
    assert resp.status_code == 500
    assert queue.jobs == []
    app.dependency_overrides.clear()


async def test_update_status_not_found(client):
    resp = await client.patch("/orders/999/status", params={"new_status": "cooking"})
    assert resp.status_code == 404


async def test_orders_cached_after_get(client):
    await client.post("/orders", json=make_order_payload())
    await client.get("/orders")
    cached = await client.get("/orders")
    assert cached.status_code == 200
    assert len(cached.json()) == 1


async def test_cache_invalidated_on_post(client):
    await client.get("/orders")
    await client.post("/orders", json=make_order_payload())
    resp = await client.get("/orders")
    assert len(resp.json()) == 1


async def test_rate_limit_exceeded(client):
    for _ in range(10):
        resp = await client.get("/orders")
        assert resp.status_code == 200
    resp = await client.get("/orders")
    assert resp.status_code == 429


async def test_get_orders_empty(client):
    resp = await client.get("/orders")
    assert resp.status_code == 200
    assert resp.json() == []
