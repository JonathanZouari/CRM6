"""Seed script — inserts sample data into the database."""
import os
import sys
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)


def seed():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Clear existing data
    cur.execute("DELETE FROM tasks")
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM customers")

    now = datetime.utcnow()

    # Customers
    customers = [
        ("Alice Johnson", "+1-555-0101", "new", now - timedelta(days=2), now + timedelta(days=1)),
        ("Bob Martinez", "+1-555-0102", "in_progress", now - timedelta(days=5), now - timedelta(days=2)),  # LATE
        ("Carol Williams", "+1-555-0103", "in_progress", now - timedelta(days=1), now + timedelta(days=3)),
        ("David Chen", "+1-555-0104", "new", None, now - timedelta(hours=6)),  # LATE
        ("Eva Rossi", "+1-555-0105", "closed", now - timedelta(days=10), None),
        ("Frank Müller", "+1-555-0106", "in_progress", now - timedelta(days=3), now - timedelta(days=1)),  # LATE
        ("Grace Kim", "+1-555-0107", "new", None, now + timedelta(days=5)),
        ("Hiro Tanaka", "+1-555-0108", "closed", now - timedelta(days=7), None),
        ("Isabel Santos", "+1-555-0109", "in_progress", now - timedelta(hours=12), now + timedelta(days=2)),
        ("James O'Brien", "+1-555-0110", "new", None, now - timedelta(hours=3)),  # LATE
    ]

    customer_ids = []
    for name, phone, status, last_contact, follow_up in customers:
        cur.execute("""
            INSERT INTO customers (name, phone, status, last_contact_at, follow_up_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (name, phone, status, last_contact, follow_up))
        customer_ids.append(cur.fetchone()["id"])

    # Orders
    orders = [
        (customer_ids[0], "Paris", now + timedelta(days=14), now + timedelta(days=21), 850.00, "offer"),
        (customer_ids[0], "London", now + timedelta(days=30), now + timedelta(days=37), 620.00, "offer"),
        (customer_ids[1], "Tokyo", now + timedelta(days=7), now + timedelta(days=14), 1450.00, "paid"),
        (customer_ids[1], "Bangkok", now + timedelta(days=45), None, 980.00, "offer"),
        (customer_ids[2], "New York", now + timedelta(days=10), now + timedelta(days=17), 1200.00, "paid"),
        (customer_ids[3], "Rome", now + timedelta(days=21), now + timedelta(days=28), 750.00, "offer"),
        (customer_ids[4], "Dubai", now - timedelta(days=5), now - timedelta(days=1), 1100.00, "paid"),
        (customer_ids[5], "Barcelona", now + timedelta(days=3), now + timedelta(days=10), 680.00, "offer"),
        (customer_ids[5], "Amsterdam", now + timedelta(days=60), None, 540.00, "cancelled"),
        (customer_ids[6], "Sydney", now + timedelta(days=25), now + timedelta(days=32), 2100.00, "offer"),
        (customer_ids[7], "Cancun", now - timedelta(days=14), now - timedelta(days=7), 890.00, "paid"),
        (customer_ids[8], "Istanbul", now + timedelta(days=18), now + timedelta(days=25), 720.00, "paid"),
        (customer_ids[8], "Athens", now + timedelta(days=40), now + timedelta(days=47), 650.00, "offer"),
        (customer_ids[9], "Berlin", now + timedelta(days=5), now + timedelta(days=12), 580.00, "offer"),
    ]

    for cid, dest, dep, ret, price, status in orders:
        cur.execute("""
            INSERT INTO orders (customer_id, destination, departure_date, return_date, price, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (cid, dest, dep.date(), ret.date() if ret else None, price, status))

    # Tasks
    tasks = [
        (customer_ids[0], "Send Paris itinerary options", now + timedelta(days=1), "open"),
        (customer_ids[0], "Follow up on London pricing", now + timedelta(days=3), "open"),
        (customer_ids[1], "Confirm Tokyo hotel reservation", now - timedelta(days=1), "open"),  # overdue
        (customer_ids[2], "Send travel insurance info", now + timedelta(days=2), "open"),
        (customer_ids[3], "Call about Rome visa requirements", now - timedelta(hours=5), "open"),  # overdue
        (customer_ids[5], "Email Barcelona flight options", now + timedelta(days=1), "open"),
        (customer_ids[6], "Prepare Sydney package quote", now + timedelta(days=4), "open"),
        (customer_ids[8], "Send Istanbul booking confirmation", now - timedelta(days=2), "done"),
        (customer_ids[8], "Follow up on Athens interest", now + timedelta(days=5), "open"),
        (customer_ids[9], "Call about Berlin departure preferences", now + timedelta(days=1), "open"),
    ]

    for cid, title, due, status in tasks:
        cur.execute("""
            INSERT INTO tasks (customer_id, title, due_date, status)
            VALUES (%s, %s, %s, %s)
        """, (cid, title, due.date(), status))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Seeded {len(customers)} customers, {len(orders)} orders, {len(tasks)} tasks")


if __name__ == "__main__":
    seed()
