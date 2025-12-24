import json
import sqlite3
from pathlib import Path
from datetime import datetime
from joblib import load

DB_PATH = "insurance.db"
VEC_PATH = Path("models/tfidf.joblib")
MODEL_PATH = Path("models/risk_model.joblib")
STATE_PATH = Path("predictive_module/model_state.json")

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def read_text(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def get_model_version():
    if not STATE_PATH.exists():
        return "v?"
    try:
        s = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return f"v{s.get('model_version', '?')}"
    except Exception:
        return "v?"

def compute_factor(conn, n_docs=10):
    vectorizer = load(VEC_PATH)
    model = load(MODEL_PATH)

    cur = conn.cursor()
    cur.execute("""
        SELECT doc_id, storage_location, timestamp
        FROM UnstructuredDocument
        ORDER BY timestamp DESC
        LIMIT ?
    """, (n_docs,))
    rows = cur.fetchall()

    texts = []
    used = []
    for doc_id, loc, ts in rows:
        t = read_text(loc).strip()
        if t:
            texts.append(t)
            used.append(doc_id)

    if not texts:
        raise ValueError("No readable text documents found to compute risk.")

    X = vectorizer.transform(texts)
    probs = model.predict_proba(X)[:, 1]
    avg_risk = float(probs.mean())

    factor = 1.0 + clamp(avg_risk, 0.0, 0.25)
    return avg_risk, factor, used

def main(product_id=1, policy_id=1, customer_id=1):
    if not VEC_PATH.exists() or not MODEL_PATH.exists():
        raise FileNotFoundError("Model artifacts missing. Run train_or_retrain first.")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Read old price
    cur.execute("SELECT product_name, base_price FROM Product WHERE product_id=?", (product_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Product {product_id} not found.")
    product_name, old_price = row
    if old_price is None:
        raise ValueError("Product.base_price is NULL. Set an initial base_price first.")

    avg_risk, factor, doc_ids = compute_factor(conn)
    new_price = round(float(old_price) * factor, 2)

    # Update price
    cur.execute("UPDATE Product SET base_price=? WHERE product_id=?", (new_price, product_id))

    # Log explanation
    model_version = get_model_version()
    note = (
        f"Predictive pricing update ({model_version}). "
        f"Computed avg_high_risk_prob={avg_risk:.3f} from docs={doc_ids}. "
        f"Applied factor={factor:.3f} to Product '{product_name}' base_price: {old_price} -> {new_price}."
    )
    cur.execute("""
        INSERT INTO Activity(policy_id, customer_id, activity_type, activity_timestamp, notes)
        VALUES (?, ?, 'PricingUpdatedByPredictiveModel', ?, ?)
    """, (policy_id, customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), note))

    conn.commit()
    conn.close()

    print("✅ Transactional pricing updated successfully")
    print(f"Product: {product_name} (product_id={product_id})")
    print(f"Old base_price={old_price} -> New base_price={new_price} (factor={factor:.3f})")
    print("Activity log written with explainability details.")

if __name__ == "__main__":
    main()
