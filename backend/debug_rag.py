import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "faqs.json")

print("🔍 DEBUGGING RAG SYSTEM...")
print(f"📂 Looking for file at: {DATA_FILE}")

# 2. Load JSON
documents = []
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Print first item to verify structure
            print(f"✅ JSON Loaded! Found {len(data)} items.")
            print(f"👀 First Item Sample: {data[0]['question']}")
            
            # Prepare documents for indexing
            documents = [f"Question: {item['question']} Answer: {item['answer']}" for item in data]
    except Exception as e:
        print(f"❌ JSON ERROR: {e}")
        exit()
else:
    print("❌ ERROR: faqs.json file NOT found!")
    exit()

# 3. Build Index
print("\n⚙️ Building FAISS Index (please wait)...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(documents, convert_to_numpy=True).astype('float32')
    
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    print("✅ Index Built Successfully!")
except Exception as e:
    print(f"❌ MODEL/FAISS ERROR: {e}")
    exit()

# 4. TEST SEARCH
test_query = "rgpv helpline contact details"
print(f"\n🧪 TESTING QUERY: '{test_query}'")

query_embedding = model.encode(test_query, convert_to_numpy=True).astype('float32').reshape(1, -1)
D, I = index.search(query_embedding, k=3)

print("\n--- RESULTS ---")
for rank, idx in enumerate(I[0]):
    print(f"#{rank+1} (Score: {D[0][rank]:.4f})")
    if idx < len(documents):
        print(f"📄 FOUND: {documents[idx]}")
    else:
        print("❌ INDEX OUT OF BOUNDS")
    print("---")