# purchase_policy.py
# Run:
#   python3 purchase_policy.py 1 1
# args: <customer_id> <product_id>

import sqlite3
import sys
from datetime import datetime, date, timedelta

DB_PATH = "insurance.db"

def main(customer_id: int, product_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Read current base_price
    cur.execute("SELECT product_name, base_price, status FROM Product WHERE product_id=?", (product_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Product not found.")
    product_name, base_price, status = row
    if base_price is None:
        raise ValueError("base_price is NULL.")

    # Create Policy
    cur.execute("""
        INSERT INTO Policy(product_id, issue_date, status)
        VALUES (?, ?, 'ACTIVE')
    """, (product_id, date.today().isoformat()))
    policy_id = cur.lastrowid

    # Link customer to policy
    cur.execute("""
        INSERT INTO PolicyParty(policy_id, customer_id, role_code)
        VALUES (?, ?, 'INSURED')
    """, (policy_id, customer_id))

    # Create 3 scheduled payments based on current base_price
    for i in range(1, 4):
        due = date.today() + timedelta(days=30 * i)
        cur.execute("""
            INSERT INTO PremiumPayment(policy_id, due_date, amount, payment_status)
            VALUES (?, ?, ?, 'SCHEDULED')
        """, (policy_id, due.isoformat(), float(base_price)))

    # Log purchase
    cur.execute("""
        INSERT INTO Activity(policy_id, customer_id, activity_type, activity_timestamp, notes)
        VALUES (?, ?, 'PolicyPurchased', ?, ?)
    """, (
        policy_id,
        customer_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"Policy purchased using current base_price={base_price} for product '{product_name}'."
    ))

    conn.commit()
    conn.close()

    print("=== PURCHASE COMPLETE ===")
    print(f"Customer ID: {customer_id}")
    print(f"New Policy ID: {policy_id}")
    print(f"Product: {product_name}")
    print(f"Price used: {base_price}")
    print("Payment schedule: 3 payments created in PremiumPayment.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 purchase_policy.py <customer_id> <product_id>")
        sys.exit(1)
    main(int(sys.argv[1]), int(sys.argv[2]))
