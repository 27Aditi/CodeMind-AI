from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

class Embedder :
    def __init__(self, model_name = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        if len(texts) == 0:
            return []
        vectors = self.model.encode(
            texts,
            batch_size = 64,
            normalize_embeddings = True,
            show_progress_bar = True 
        )
        return vectors.tolist()
    
    def embed_query(self, query):
        prefix = "Represent this sentence for searching relevant passages: "
        vector = self.model.encode(
            prefix + query,
            normalize_embeddings = True
        )
        return vector.tolist()