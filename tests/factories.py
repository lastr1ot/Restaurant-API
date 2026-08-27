def make_order_payload(
    table_id: int = 1, items: list[dict] | None = None, total_price: float = 100.0
):
    def_items = [{"name": "Pizza", "quantity": 1, "price": 100.0}]
    return {
        "table_id": table_id,
        "items": items or def_items,
        "total_price": total_price,
    }
