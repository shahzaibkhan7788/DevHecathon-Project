import json
import os

KV_FILE = "rag_metadata.json"

def load_kv():
    if not os.path.exists(KV_FILE):
        return {}
    try:
        with open(KV_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_kv(data):
    with open(KV_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def add_document_metadata(doc_id, metadata):
    db = load_kv()
    db[doc_id] = metadata
    save_kv(db)

def get_document_metadata(doc_id):
    db = load_kv()
    return db.get(doc_id)

def list_documents():
    db = load_kv()
    return list(db.values())
