from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
import hashlib
from config import CHUNK_SIZE, CHUNK_OVERLAP


class CodeSplitter : 

    def __init__(self, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _get_splitter(self, language):
        LANG_MAP = {
            "python" : Language.PYTHON,
            "javascript" : Language.JS,
            "java" : Language.JAVA,
            "go" : Language.GO,
            "cpp" : Language.CPP,
            "rust" : Language.RUST,
        }
        if language in LANG_MAP:
            return RecursiveCharacterTextSplitter.from_language(
                language = LANG_MAP[language],
                chunk_size = self.chunk_size,
                chunk_overlap = self.chunk_overlap
            )
        else:
            return RecursiveCharacterTextSplitter(
                chunk_size = self.chunk_size,
                chunk_overlap = self.chunk_overlap
            )

    def _split_one(self, doc):
        language = doc["metadata"]["language"]
        content = doc["content"]
        splitter = self._get_splitter(language)
        raw_chunks = splitter.split_text(content)
        result = []
        for i, chunk_text in enumerate(raw_chunks):
            unique_string = chunk_text + doc["metadata"]["file_path"] + str(i)
            chunk_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
            result.append({
                "content" : chunk_text,
                "metadata" : {
                    **doc["metadata"],
                    "chunk_index" : i,
                    "total_chunks" : len(raw_chunks),
                    "chunk_id" : chunk_id,
                }
            })
        return result
    
    def split(self, documents):
        all_chunks = []
        for doc in documents:
            chunks = self._split_one(doc)
            all_chunks.extend(chunks)
        return all_chunks
