import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.rag.rag_engine import build_vector_store_from_mongo, search_rag

build_vector_store_from_mongo()

query = "divyang pension kitna milta hai"
results = search_rag(query)

print("\n--- TOP MATCHES ---\n")

for result in results:
    print(result)
    print("\n-------------------\n")
