# seed_data.py
# Inserts baseline demo data into insurance.db so ML can modify it later
# Run: python seed_data.py

import sqlite3
from datetime import date, timedelta

DB_PATH = "insurance.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# -------------------------------
# Insert Region
# -------------------------------
cur.execute("""
INSERT INTO DimRegion (country, state, city)
VALUES ('USA', 'WA', 'Seattle')
""")
region_id = cur.lastrowid

# -------------------------------
# Insert Customer
# -------------------------------
cur.execute("""
INSERT INTO Customer (region_id, first_name, last_name, date_of_birth, gender)
VALUES (?, 'Emily', 'Liu', '1999-05-12', 'Female')
""", (region_id,))
customer_id = cur.lastrowid

# -------------------------------
# Insert Product
# -------------------------------
cur.execute("""
INSERT INTO Product (product_name, effective_from, effective_to, status)
VALUES ('Standard Health Plan', '2025-01-01', '2026-12-31', 'ACTIVE')
""")
product_id = cur.lastrowid

# -------------------------------
# Insert Policy
# -------------------------------
cur.execute("""
INSERT INTO Policy (product_id, issue_date, status)
VALUES (?, '2025-01-15', 'ACTIVE')
""", (product_id,))
policy_id = cur.lastrowid

# -------------------------------
# Insert PolicyParty (Customer is the insured)
# -------------------------------
cur.execute("""
INSERT INTO PolicyParty (policy_id, customer_id, role_code)
VALUES (?, ?, 'INSURED')
""", (policy_id, customer_id))

# -------------------------------
# Insert Premium Payments (3 future payments)
# -------------------------------
today = date.today()
amount = 200.00

for i in range(1, 4):
    due = today + timedelta(days=30 * i)
    cur.execute("""
    INSERT INTO PremiumPayment (policy_id, due_date, amount, payment_status)
    VALUES (?, ?, ?, 'SCHEDULED')
    """, (policy_id, due.isoformat(), amount))

# -------------------------------
# Insert baseline Health Risk Factors
# -------------------------------
cur.execute("""
INSERT INTO HealthRiskFactors
(customer_id, observation_date, smoking_status, alcohol_use, physical_activity_level, blood_pressure)
VALUES (?, ?, 'Unknown', 'Unknown', 'Moderate', 'Normal')
""", (customer_id, today.isoformat()))

conn.commit()
conn.close()

print("✅ Demo data inserted successfully.")
print(f"Customer ID: {customer_id}")
print(f"Policy ID: {policy_id}")
