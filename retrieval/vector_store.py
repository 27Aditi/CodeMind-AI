

import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from config import QDRANT_PATH, QDRANT_COLLECTION, TOP_K

logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self, path: str = QDRANT_PATH, collection: str = QDRANT_COLLECTION):
        self.collection = collection
        self.client = QdrantClient(":memory:")
        self._ensure_collection()

    def _ensure_collection(self, fresh : bool = False):
        existing = [c.name for c in self.client.get_collections().collections]
        if fresh and self.collection in existing:
            self.client.delete_collection(self.collection)
            existing = []
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection}")
        else:
            logger.info(f"Using existing collection: {self.collection}")

    def upsert(self, chunks: list[dict], embeddings: list[list[float]]) -> int:
        points = []
        for chunk, vector in zip(chunks, embeddings):
            point_id = int(chunk["metadata"]["chunk_id"], 16) % (2**63)
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    **chunk["metadata"],
                    "content": chunk["content"],
                }
            ))

        for i in range(0, len(points), 100):
            self.client.upsert(
                collection_name=self.collection,
                points=points[i:i + 100],
            )

        logger.info(f"Upserted {len(points)} points into Qdrant")
        return len(points)

    def search(self, query_vector: list[float], top_k: int = TOP_K) -> list[dict]:
        hits = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        ).points

        results = []
        for hit in hits:
            payload = dict(hit.payload)
            content = payload.pop("content", "")
            results.append({
                "content":  content,
                "score":    hit.score,
                "metadata": payload,
            })

        return results

    def delete_and_recreate(self):
        self._ensure_collection(fresh = True)

    def count(self) -> int:
        return self.client.count(collection_name=self.collection).count

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass
        import os, shutil, time
        from config import QDRANT_PATH
        time.sleep(0.5)
        if os.path.exists(QDRANT_PATH):
            try:
                shutil.rmtree(QDRANT_PATH)
            except Exception:
                pass
