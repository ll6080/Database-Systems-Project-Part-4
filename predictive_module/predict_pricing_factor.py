import sqlite3
from pathlib import Path
from joblib import load

DB_PATH = "insurance.db"
VEC_PATH = Path("models/tfidf.joblib")
MODEL_PATH = Path("models/risk_model.joblib")

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def fetch_recent_docs(n=5):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()
    cur.execute("""
        SELECT doc_id, storage_location, timestamp
        FROM UnstructuredDocument
        ORDER BY timestamp DESC
        LIMIT ?
    """, (n,))
    rows = cur.fetchall()
    conn.close()
    return rows

def read_text(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def main():
    if not VEC_PATH.exists() or not MODEL_PATH.exists():
        print("❌ Model artifacts not found. Run: python predictive_module/train_or_retrain.py")
        return

    vectorizer = load(VEC_PATH)
    model = load(MODEL_PATH)

    docs = fetch_recent_docs(5)
    texts = []
    used_docs = []

    for doc_id, loc, ts in docs:
        t = read_text(loc).strip()
        if t:
            texts.append(t)
            used_docs.append((doc_id, ts))

    if not texts:
        print("❌ No readable recent text documents found.")
        return

    X = vectorizer.transform(texts)
    # probability of class 1 (high risk)
    probs = model.predict_proba(X)[:, 1]
    avg_risk = float(probs.mean())

    # Map avg_risk to pricing factor (1.00 to 1.25)
    factor = 1.0 + clamp(avg_risk, 0.0, 0.25)

    print("✅ Predictive pricing factor computed from unstructured documents")
    print(f"Docs used: {used_docs}")
    print(f"Average high-risk probability: {avg_risk:.3f}")
    print(f"Pricing factor: {factor:.3f}")
    print("Use this factor in Step 4 to update Product.base_price.")

if __name__ == "__main__":
    main()
