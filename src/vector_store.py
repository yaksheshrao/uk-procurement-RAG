"""Build and query a FAISS index over sentence-transformer embeddings."""
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, embedding_model: str):
        self.model = SentenceTransformer(embedding_model)
        self.index = None
        self.docs = []

    def build(self, docs: list[dict], index_path: str, docs_path: str) -> None:
        self.docs = docs
        texts = [d["text"] for d in docs]
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, show_progress_bar=True, normalize_embeddings=True
        )
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine
        self.index.add(embeddings.astype(np.float32))
        faiss.write_index(self.index, index_path)
        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False)

    def load(self, index_path: str, docs_path: str) -> None:
        self.index = faiss.read_index(index_path)
        with open(docs_path, encoding="utf-8") as f:
            self.docs = json.load(f)

    def search(self, query: str, k: int = 20) -> list[dict]:
        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        scores, idx = self.index.search(q.astype(np.float32), k)
        results = []
        for score, i in zip(scores[0], idx[0]):
            if i == -1:
                continue
            doc = dict(self.docs[i])
            doc["score"] = float(score)
            results.append(doc)
        return results
