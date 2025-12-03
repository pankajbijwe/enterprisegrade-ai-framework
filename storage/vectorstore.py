# storage/vectorstore.py
import os
import pickle
import numpy as np
from typing import List, Dict

# Try FAISS first, fallback to hnswlib if FAISS not available
try:
    import faiss
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False
    import hnswlib

from services.llm_client import OpenAIClient

class VectorStore:
    def __init__(self, path: str, dim: int = None):
        self.path = path
        self.dim = dim  # will be set on first add if None
        self._init_store()

    def _init_store(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        meta_path = self.path + ".meta"
        if os.path.exists(meta_path):
            with open(meta_path, "rb") as f:
                meta = pickle.load(f)
                self.dim = meta["dim"]
                self.ids = meta["ids"]
                self.metadatas = meta["metadatas"]
        else:
            self.ids = []
            self.metadatas = []
        if _HAS_FAISS:
            self.index = None
            if os.path.exists(self.path + ".index"):
                self.index = faiss.read_index(self.path + ".index")
        else:
            # hnswlib fallback
            self.index = None
            if os.path.exists(self.path + ".hnsw"):
                self.index = hnswlib.Index(space='cosine', dim=self.dim)
                self.index.load_index(self.path + ".hnsw")

    def add_documents(self, chunks: List[Dict]) -> List[str]:
        client = OpenAIClient()
        embeddings = []
        for c in chunks:
            emb = client.embed_text(c["text"])
            emb = np.array(emb, dtype="float32")
            embeddings.append(emb)
            self.metadatas.append({"id": c["id"], "text": c["text"]})
            self.ids.append(c["id"])

        arr = np.vstack(embeddings)
        if self.dim is None:
            self.dim = arr.shape[1]

        if _HAS_FAISS:
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.dim)
            faiss.normalize_L2(arr)
            self.index.add(arr)
            faiss.write_index(self.index, self.path + ".index")
        else:
            # hnswlib init or add
            if self.index is None:
                self.index = hnswlib.Index(space='cosine', dim=self.dim)
                self.index.init_index(max_elements=100000, ef_construction=200, M=16)
            ids = list(range(len(self.ids) - len(chunks), len(self.ids)))
            self.index.add_items(arr, ids)
            self.index.save_index(self.path + ".hnsw")

        # persist metadata
        with open(self.path + ".meta", "wb") as f:
            pickle.dump({"dim": self.dim, "ids": self.ids, "metadatas": self.metadatas}, f)
        return [m["id"] for m in self.metadatas[-len(chunks):]]

    def query(self, embedding, top_k=5):
        import numpy as np
        vec = np.array(embedding, dtype="float32").reshape(1, -1)
        if _HAS_FAISS:
            faiss.normalize_L2(vec)
            D, I = self.index.search(vec, top_k)
            results = []
            for score, idx in zip(D[0], I[0]):
                if idx < 0:
                    continue
                meta = self.metadatas[idx]
                results.append({"id": meta["id"], "text": meta["text"], "score": float(score)})
            return results
        else:
            labels, distances = self.index.knn_query(vec, k=top_k)
            results = []
            for label, dist in zip(labels[0], distances[0]):
                if label < 0:
                    continue
                meta = self.metadatas[label]
                # hnswlib returns distance; convert to similarity proxy
                score = float(1.0 - dist)
                results.append({"id": meta["id"], "text": meta["text"], "score": score})
            return results