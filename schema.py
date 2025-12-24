# schema.py
# Creates the project schema in a local SQLite database (insurance.db).
# Run: python schema.py

import sqlite3
from pathlib import Path

DB_PATH = Path("insurance.db")

DDL_STATEMENTS = [
    # Important: SQLite requires PRAGMA foreign_keys = ON per connection to enforce FKs.

    # --- Dimension / reference tables ---
    """
    CREATE TABLE IF NOT EXISTS DimRegion (
        region_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        country     TEXT NOT NULL,
        state       TEXT,
        city        TEXT
    );
    """,

    # --- Core insurance domain ---
    """
    CREATE TABLE IF NOT EXISTS Customer (
        customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        region_id     INTEGER NOT NULL,
        first_name    TEXT NOT NULL,
        last_name     TEXT NOT NULL,
        date_of_birth TEXT,         -- store as 'YYYY-MM-DD'
        gender        TEXT,
        FOREIGN KEY (region_id) REFERENCES DimRegion(region_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Product (
        product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name   TEXT NOT NULL,
        effective_from TEXT,        -- 'YYYY-MM-DD'
        effective_to   TEXT,        -- 'YYYY-MM-DD'
        status         TEXT NOT NULL
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Policy (
        policy_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id  INTEGER NOT NULL,
        issue_date  TEXT NOT NULL,  -- 'YYYY-MM-DD'
        status      TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS PremiumPayment (
        premium_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id      INTEGER NOT NULL,
        due_date       TEXT NOT NULL,       -- 'YYYY-MM-DD'
        amount         NUMERIC NOT NULL,    -- SQLite uses dynamic typing; NUMERIC is fine
        payment_status TEXT NOT NULL,
        FOREIGN KEY (policy_id) REFERENCES Policy(policy_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    # M:N relationship resolution with role_code in composite PK
    """
    CREATE TABLE IF NOT EXISTS PolicyParty (
        policy_id   INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        role_code   TEXT NOT NULL,
        PRIMARY KEY (policy_id, customer_id, role_code),
        FOREIGN KEY (policy_id) REFERENCES Policy(policy_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Activity (
        activity_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id          INTEGER NOT NULL,
        customer_id        INTEGER NOT NULL,
        activity_type      TEXT NOT NULL,
        activity_timestamp TEXT NOT NULL,   -- ISO8601 'YYYY-MM-DD HH:MM:SS'
        notes              TEXT,
        FOREIGN KEY (policy_id) REFERENCES Policy(policy_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    # --- Healthcare analytics extensions ---
    """
    CREATE TABLE IF NOT EXISTS HealthRiskFactors (
        risk_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id              INTEGER NOT NULL,
        observation_date         TEXT NOT NULL, -- 'YYYY-MM-DD'
        smoking_status           TEXT,
        alcohol_use              TEXT,
        physical_activity_level  TEXT,
        blood_pressure           TEXT,
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS ChronicDiseaseOutcomes (
        outcome_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id    INTEGER NOT NULL,
        diagnosis_date TEXT NOT NULL, -- 'YYYY-MM-DD'
        disease_type   TEXT NOT NULL,
        severity       TEXT,
        FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS ExternalDiseaseRate (
        rate_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        region_id    INTEGER NOT NULL,
        year         INTEGER NOT NULL,
        disease_code TEXT NOT NULL,
        FOREIGN KEY (region_id) REFERENCES DimRegion(region_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,

    # --- Unstructured data integration ---
    """
    CREATE TABLE IF NOT EXISTS UnstructuredDocument (
        doc_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_type         TEXT NOT NULL,   -- e.g., 'LabReport', 'ClaimForm', 'Imaging'
        storage_location TEXT NOT NULL,   -- path or URI to the text file
        timestamp        TEXT NOT NULL,   -- ISO8601 'YYYY-MM-DD HH:MM:SS'
        json_metadata    TEXT            -- store JSON as TEXT
    );
    """,

    # Polymorphic link table: cannot enforce entity_id as FK because entity_type varies.
    """
    CREATE TABLE IF NOT EXISTS DocumentLink (
        doc_id      INTEGER NOT NULL,
        entity_type TEXT NOT NULL,     -- e.g., 'Customer', 'Policy', 'Activity'
        entity_id   INTEGER NOT NULL,
        PRIMARY KEY (doc_id, entity_type, entity_id),
        FOREIGN KEY (doc_id) REFERENCES UnstructuredDocument(doc_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """,
]

INDEX_STATEMENTS = [
    # Helpful indexes for Part 4 “query optimization” write-up
    "CREATE INDEX IF NOT EXISTS IX_Customer_RegionId ON Customer(region_id);",
    "CREATE INDEX IF NOT EXISTS IX_Policy_ProductId ON Policy(product_id);",
    "CREATE INDEX IF NOT EXISTS IX_PremiumPayment_Policy_DueDate ON PremiumPayment(policy_id, due_date);",
    "CREATE INDEX IF NOT EXISTS IX_HealthRiskFactors_Customer_Date ON HealthRiskFactors(customer_id, observation_date);",
    "CREATE INDEX IF NOT EXISTS IX_Activity_Policy_Time ON Activity(policy_id, activity_timestamp);",
    "CREATE INDEX IF NOT EXISTS IX_DocumentLink_Entity ON DocumentLink(entity_type, entity_id, doc_id);",
    "CREATE INDEX IF NOT EXISTS IX_UnstructuredDocument_Time ON UnstructuredDocument(timestamp);",
]

def create_schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        for ddl in DDL_STATEMENTS:
            cur.execute(ddl)

        for idx in INDEX_STATEMENTS:
            cur.execute(idx)

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    create_schema(DB_PATH)
    print(f"✅ Schema created/updated successfully at: {DB_PATH.resolve()}")
    print("Tip: Use a SQLite viewer (e.g., DB Browser for SQLite) to inspect tables.")
