

import logging
from rank_bm25 import BM25Okapi

from retrieval.vector_store import VectorStore
from ingest.embedder import Embedder
from config import TOP_K

logger = logging.getLogger(__name__)


class HybridRetriever:

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder     = embedder
        self.bm25         = None
        self.corpus       = []   

    def build_bm25_index(self, chunks: list[dict]):
        self.corpus = chunks
        tokenized = [chunk["content"].lower().split() for chunk in chunks]
        self.bm25  = BM25Okapi(tokenized)
        logger.info(f"BM25 index built with {len(chunks)} chunks")

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        candidates = top_k * 2

        vector_results = self._vector_search(query, candidates)
        bm25_results   = self._bm25_search(query, candidates)

        return self._rrf_fuse(vector_results, bm25_results, top_k)


    def _vector_search(self, query: str, top_k: int) -> list[dict]:
        query_vector = self.embedder.embed_query(query)
        return self.vector_store.search(query_vector, top_k)

    def _bm25_search(self, query: str, top_k: int) -> list[dict]:
        if self.bm25 is None:
            logger.warning("BM25 index not built. Returning empty results.")
            return []

        tokenized_query = query.lower().split()
        scores          = self.bm25.get_scores(tokenized_query)

        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:   
                chunk = self.corpus[idx]
                results.append({
                    "content":  chunk["content"],
                    "score":    float(scores[idx]),
                    "metadata": chunk["metadata"],
                })

        return results

    def _rrf_fuse(
        self,
        vector_results: list[dict],
        bm25_results:   list[dict],
        top_k:          int,
        k:              int = 60,      
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion.

        Formula: score(doc) = sum of 1/(k + rank) across all rankers
        Does NOT need score normalisation — only uses rank position.
        """
        rrf_scores  = {}   
        chunk_map   = {}   

        def _chunk_id(result):
            return result["metadata"].get("chunk_id", result["content"][:32])

        for rank, result in enumerate(vector_results):
            cid = _chunk_id(result)
            rrf_scores[cid]  = rrf_scores.get(cid, 0) + 1 / (k + rank + 1)
            chunk_map[cid]   = result


        for rank, result in enumerate(bm25_results):
            cid = _chunk_id(result)
            rrf_scores[cid]  = rrf_scores.get(cid, 0) + 1 / (k + rank + 1)
            chunk_map[cid]   = result


        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]

        fused = []
        for cid in sorted_ids:
            result              = dict(chunk_map[cid])
            result["rrf_score"] = rrf_scores[cid]
            fused.append(result)

        return fused
