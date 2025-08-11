# C:\AgentUr1\tools\init_qdrant.py
from __future__ import annotations
import os, sys
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

def main():
    url = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
    collection = os.environ.get("QDRANT_COLLECTION", "documents")
    vector_size = int(os.environ.get("QDRANT_VECTOR_SIZE", "768"))
    distance = os.environ.get("QDRANT_DISTANCE", "Cosine")
    client = QdrantClient(url=url)
    existing = [c.name for c in client.get_collections().collections]
    if collection not in existing:
        print(f"Creating collection '{collection}' ...")
        client.recreate_collection(
            collection_name=collection,
            vectors_config=qm.VectorParams(size=vector_size, distance=getattr(qm.Distance, distance))
        )
    else:
        print(f"Collection '{collection}' already exists.")
    print("OK")
if __name__ == "__main__":
    main()

