import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DB_PATH = "insurance.db"
MODELS_DIR = Path("models")
STATE_PATH = Path("predictive_module/model_state.json")

HIGH_RISK_KEYWORDS = {"cancer", "tumor", "metastatic", "oncology", "severe", "malignant"}

def ensure_dirs():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"last_trained_timestamp": None, "model_version": 0}

def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")

def fetch_documents(cur) -> List[Tuple[int, str, str]]:
    # returns: (doc_id, storage_location, timestamp)
    cur.execute("""
        SELECT doc_id, storage_location, timestamp
        FROM UnstructuredDocument
        ORDER BY timestamp ASC
    """)
    return cur.fetchall()

def read_text_file(path_str: str) -> str:
    p = Path(path_str)
    if not p.exists():
        # If storage_location is relative, try relative to project root
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def weak_label(text: str) -> int:
    t = text.lower()
    return 1 if any(k in t for k in HIGH_RISK_KEYWORDS) else 0

from typing import Optional
def has_new_data(docs: List[Tuple[int, str, str]], last_ts: Optional[str]) -> bool:
    if not docs:
        return False
    newest = docs[-1][2]  # timestamp string
    if last_ts is None:
        return True
    # ISO-like strings compare well lexicographically if consistent format
    return newest > last_ts

def main():
    ensure_dirs()
    state = load_state()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    docs = fetch_documents(cur)
    conn.close()

    if not docs:
        print("❌ No documents found in UnstructuredDocument. Ingest some .txt first.")
        return

    if not has_new_data(docs, state["last_trained_timestamp"]):
        print("✅ No new unstructured documents since last training. Skipping retrain.")
        print(f"Last trained timestamp: {state['last_trained_timestamp']}")
        return

    texts = []
    labels = []
    usable = 0

    for doc_id, storage_location, ts in docs:
        text = read_text_file(storage_location).strip()
        if not text:
            continue
        texts.append(text)
        labels.append(weak_label(text))
        usable += 1

    if usable < 4:
        print("⚠️ Not enough usable text documents to train a stable model (need ~4+).")
        print("Add more .txt docs and ingest them.")
        return

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=5000)
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression(max_iter=1000)
    model.fit(X, labels)

    dump(vectorizer, MODELS_DIR / "tfidf.joblib")
    dump(model, MODELS_DIR / "risk_model.joblib")

    # Update state
    newest_ts = docs[-1][2]
    state["last_trained_timestamp"] = newest_ts
    state["model_version"] = int(state.get("model_version", 0)) + 1
    save_state(state)

    print("✅ Model trained/retrained successfully.")
    print(f"Usable documents: {usable}")
    print(f"Last trained timestamp set to: {newest_ts}")
    print(f"Model version: v{state['model_version']}")
    print("Saved: models/tfidf.joblib, models/risk_model.joblib, predictive_module/model_state.json")

if __name__ == "__main__":
    main()
