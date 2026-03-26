from db import query, query_one, execute


def get_orders_by_customer(customer_id):
    return query("""
        SELECT * FROM orders
        WHERE customer_id = %s
        ORDER BY created_at DESC
    """, (customer_id,))


def create_order(customer_id, data):
    return query_one("""
        INSERT INTO orders (customer_id, destination, departure_date, return_date, price, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """, (
        customer_id,
        data["destination"],
        data["departure_date"],
        data.get("return_date"),
        data["price"],
        data.get("status", "offer"),
    ))


def update_order(order_id, data):
    fields = []
    values = []
    allowed = ["destination", "departure_date", "return_date", "price", "status"]
    for key in allowed:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])
    if not fields:
        return query_one("SELECT * FROM orders WHERE id = %s", (order_id,))
    values.append(order_id)
    sql = f"UPDATE orders SET {', '.join(fields)} WHERE id = %s RETURNING *"
    return query_one(sql, values)


def delete_order(order_id):
    result = execute(
        "DELETE FROM orders WHERE id = %s RETURNING id",
        (order_id,)
    )
    return len(result) > 0
