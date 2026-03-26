import json
from openai import OpenAI
from config import Config
from db import query

INTENT_MAP = {
    "count_late": {
        "sql": """
            SELECT COUNT(*) AS count FROM customers
            WHERE follow_up_at < now() AND status != 'closed'
        """,
        "format": lambda r: f"There are {r[0]['count']} customers with overdue follow-ups."
    },
    "list_late": {
        "sql": """
            SELECT name, phone, follow_up_at FROM customers
            WHERE follow_up_at < now() AND status != 'closed'
            ORDER BY follow_up_at ASC LIMIT 20
        """,
        "format": lambda r: format_customer_list(r, "late follow-ups")
    },
    "revenue_total": {
        "sql": "SELECT COALESCE(SUM(price), 0) AS total FROM orders WHERE status = 'paid'",
        "format": lambda r: f"Total revenue from paid orders: ${r[0]['total']:,.2f}"
    },
    "revenue_month": {
        "sql": """
            SELECT COALESCE(SUM(price), 0) AS total FROM orders
            WHERE status = 'paid' AND created_at >= date_trunc('month', now())
        """,
        "format": lambda r: f"Revenue this month: ${r[0]['total']:,.2f}"
    },
    "upcoming_departures": {
        "sql": """
            SELECT c.name, o.destination, o.departure_date, o.price
            FROM orders o JOIN customers c ON c.id = o.customer_id
            WHERE o.departure_date >= CURRENT_DATE AND o.status != 'cancelled'
            ORDER BY o.departure_date ASC LIMIT 10
        """,
        "format": lambda r: format_departures(r)
    },
    "customer_count": {
        "sql": "SELECT COUNT(*) AS count FROM customers",
        "format": lambda r: f"Total customers: {r[0]['count']}"
    },
    "open_tasks": {
        "sql": """
            SELECT t.title, t.due_date, c.name
            FROM tasks t JOIN customers c ON c.id = t.customer_id
            WHERE t.status = 'open'
            ORDER BY t.due_date ASC LIMIT 10
        """,
        "format": lambda r: format_tasks(r)
    },
    "orders_by_status": {
        "sql": """
            SELECT status, COUNT(*) AS count, COALESCE(SUM(price), 0) AS total
            FROM orders GROUP BY status
        """,
        "format": lambda r: format_order_stats(r)
    },
}

SYSTEM_PROMPT = """You are a CRM assistant for a flight ticket sales agency.
The user asks business questions. Classify the question into exactly one intent.

Available intents:
- count_late: How many customers have overdue follow-ups
- list_late: List customers with overdue follow-ups
- revenue_total: Total revenue from paid orders
- revenue_month: Revenue this month
- upcoming_departures: Upcoming flight departures
- customer_count: Total number of customers
- open_tasks: List open/pending tasks
- orders_by_status: Order statistics by status
- unknown: Question doesn't match any intent

Respond with JSON only: {"intent": "<intent_key>"}"""


def format_customer_list(rows, label):
    if not rows:
        return f"No customers with {label}."
    lines = [f"Customers with {label} ({len(rows)}):"]
    for r in rows:
        lines.append(f"  - {r['name']} ({r.get('phone', 'N/A')}) — follow-up: {r['follow_up_at']}")
    return "\n".join(lines)


def format_departures(rows):
    if not rows:
        return "No upcoming departures."
    lines = ["Upcoming departures:"]
    for r in rows:
        lines.append(f"  - {r['name']} → {r['destination']} on {r['departure_date']} (${r['price']:,.2f})")
    return "\n".join(lines)


def format_tasks(rows):
    if not rows:
        return "No open tasks."
    lines = ["Open tasks:"]
    for r in rows:
        lines.append(f"  - {r['title']} (due: {r['due_date']}) — customer: {r['name']}")
    return "\n".join(lines)


def format_order_stats(rows):
    if not rows:
        return "No orders found."
    lines = ["Order statistics:"]
    for r in rows:
        lines.append(f"  - {r['status']}: {r['count']} orders, ${r['total']:,.2f}")
    return "\n".join(lines)


def process_chat(message):
    if not Config.OPENAI_API_KEY:
        return "Chat is not configured. Please set OPENAI_API_KEY."

    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0,
            max_tokens=50,
            timeout=10,
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        intent = parsed.get("intent", "unknown")
    except Exception:
        intent = "unknown"

    if intent not in INTENT_MAP:
        return "I can answer questions about customers, orders, revenue, tasks, and upcoming departures. Try asking something like 'How many customers are late?' or 'Total revenue this month?'"

    try:
        intent_config = INTENT_MAP[intent]
        rows = query(intent_config["sql"])
        return intent_config["format"](rows)
    except Exception as e:
        return f"Sorry, I encountered an error while looking that up: {str(e)}"
