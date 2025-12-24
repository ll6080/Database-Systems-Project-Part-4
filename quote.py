# quote.py
# Run:
#   python3 quote.py 1 1
# args: <customer_id> <product_id>

import sqlite3
import sys
from datetime import datetime

DB_PATH = "insurance.db"

def main(customer_id: int, product_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.execute("""
        SELECT p.product_name, p.base_price, p.status
        FROM Product p
        WHERE p.product_id = ?
    """, (product_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Product not found.")
    name, price, status = row

    # Log quote event
    cur.execute("""
        INSERT INTO Activity(policy_id, customer_id, activity_type, activity_timestamp, notes)
        VALUES (?, ?, 'QuoteGenerated', ?, ?)
    """, (
        1,  # demo policy_id placeholder (or NULL if you later allow it)
        customer_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"Quote generated for product_id={product_id} ({name}). base_price={price}."
    ))

    conn.commit()
    conn.close()

    print("=== QUOTE ===")
    print(f"Customer ID: {customer_id}")
    print(f"Product: {name} (status={status})")
    print(f"Quoted Price (base_price): {price}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 quote.py <customer_id> <product_id>")
        sys.exit(1)
    main(int(sys.argv[1]), int(sys.argv[2]))
