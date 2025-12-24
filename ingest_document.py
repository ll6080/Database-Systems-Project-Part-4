# ingest_document.py
# Purpose:
# Register an unstructured text document into the database
# so it can be used by the predictive module.
#
# Run:
#   python ingest_document.py data/doc_high_1.txt 1

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json

DB_PATH = "insurance.db"

# -------------------------------
# Validate input
# -------------------------------
if len(sys.argv) != 3:
    print("Usage: python ingest_document.py <text_file_path> <customer_id>")
    sys.exit(1)

file_path = Path(sys.argv[1])
customer_id = int(sys.argv[2])

if not file_path.exists():
    print(f"❌ File not found: {file_path}")
    sys.exit(1)

# -------------------------------
# Read text file
# -------------------------------
text = file_path.read_text(encoding="utf-8", errors="ignore")

# Basic metadata stored as JSON
metadata = {
    "filename": file_path.name,
    "char_length": len(text),
    "ingested_at": datetime.now().isoformat()
}

# -------------------------------
# Insert into database
# -------------------------------
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# Insert document record
cur.execute("""
INSERT INTO UnstructuredDocument
(doc_type, storage_location, timestamp, json_metadata)
VALUES (?, ?, ?, ?)
""", (
    "TextReport",
    str(file_path),
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    json.dumps(metadata)
))

doc_id = cur.lastrowid

# Link document to customer
cur.execute("""
INSERT INTO DocumentLink (doc_id, entity_type, entity_id)
VALUES (?, 'Customer', ?)
""", (doc_id, customer_id))

conn.commit()
conn.close()

print("✅ Document ingested successfully")
print(f"Document ID: {doc_id}")
print(f"Linked to Customer ID: {customer_id}")
print(f"Stored file path: {file_path}")
