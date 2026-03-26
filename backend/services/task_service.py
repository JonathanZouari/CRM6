from db import query, query_one, execute


def get_tasks_by_customer(customer_id):
    return query("""
        SELECT * FROM tasks
        WHERE customer_id = %s
        ORDER BY due_date ASC
    """, (customer_id,))


def create_task(customer_id, data):
    return query_one("""
        INSERT INTO tasks (customer_id, title, due_date, status)
        VALUES (%s, %s, %s, %s)
        RETURNING *
    """, (
        customer_id,
        data["title"],
        data["due_date"],
        data.get("status", "open"),
    ))


def update_task(task_id, data):
    fields = []
    values = []
    allowed = ["title", "due_date", "status"]
    for key in allowed:
        if key in data:
            fields.append(f"{key} = %s")
            values.append(data[key])
    if not fields:
        return query_one("SELECT * FROM tasks WHERE id = %s", (task_id,))
    values.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s RETURNING *"
    return query_one(sql, values)


def delete_task(task_id):
    result = execute(
        "DELETE FROM tasks WHERE id = %s RETURNING id",
        (task_id,)
    )
    return len(result) > 0
