from db import query, query_one, execute


def get_all_customers(status_filter=None):
    sql = """
        SELECT *,
            CASE
                WHEN follow_up_at < now() AND status != 'closed'
                THEN true ELSE false
            END AS is_late
        FROM customers
    """
    params = []
    if status_filter:
        sql += " WHERE status = %s"
        params.append(status_filter)
    sql += " ORDER BY created_at DESC"
    return query(sql, params if params else None)


def get_late_customers():
    return query("""
        SELECT *,
            true AS is_late
        FROM customers
        WHERE follow_up_at < now()
          AND status != 'closed'
        ORDER BY follow_up_at ASC
    """)


def get_customer_by_id(customer_id):
    return query_one("""
        SELECT *,
            CASE
                WHEN follow_up_at < now() AND status != 'closed'
                THEN true ELSE false
            END AS is_late
        FROM customers
        WHERE id = %s
    """, (customer_id,))


def create_customer(data):
    return query_one("""
        INSERT INTO customers (name, phone, status, follow_up_at)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """, (
        data["name"],
        data.get("phone"),
        data.get("status", "new"),
        data.get("follow_up_at"),
    ))


def update_customer(customer_id, data):
    fields = []
    values = []
    allowed = ["name", "phone", "status", "last_contact_at", "follow_up_at"]
    for key in allowed:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])
    if not fields:
        return get_customer_by_id(customer_id)
    values.append(customer_id)
    sql = f"UPDATE customers SET {', '.join(fields)} WHERE id = %s RETURNING *"
    return query_one(sql, values)


def delete_customer(customer_id):
    result = execute(
        "DELETE FROM customers WHERE id = %s RETURNING id",
        (customer_id,)
    )
    return len(result) > 0
