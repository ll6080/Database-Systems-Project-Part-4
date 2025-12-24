import csv
import sqlite3

DB = "insurance.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

with open("data/external_cancer_rates.csv", "r") as f:
    reader = csv.DictReader(f)
    for r in reader:
        state = r["state"]
        year = int(r["year"])
        value = float(r["rate_value"])

        # get or create region
        cur.execute("SELECT region_id FROM DimRegion WHERE state=?", (state,))
        row = cur.fetchone()
        if row:
            region_id = row[0]
        else:
            cur.execute(
                "INSERT INTO DimRegion(country,state,city) VALUES ('USA',?,NULL)", (state,)
            )
            region_id = cur.lastrowid

        cur.execute("""
        INSERT INTO ExternalDiseaseRate(region_id, year, disease_code, rate_value)
        VALUES (?, ?, 'CANCER', ?)
        """, (region_id, year, value))

conn.commit()
conn.close()
print("External cancer dataset imported.")
