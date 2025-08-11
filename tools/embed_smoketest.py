from __future__ import annotations
import sys
from typing import List

def test_hf():
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    emb = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        normalize=True,
    )
    vecs: List[List[float]] = emb.get_text_embedding_batch(["hello", "world"])
    assert len(vecs) == 2 and all(len(v)>0 for v in vecs)
    print("HuggingFace OK:", len(vecs[0]))

if __name__ == "__main__":
    try:
        test_hf()
    except Exception as e:
        print("EMBED TEST FAILED:", repr(e), file=sys.stderr)
        sys.exit(1)
