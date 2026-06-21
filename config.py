import os
from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"   


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


EMBEDDING_MODEL = "all-MiniLM-L6-v2"  


QDRANT_PATH = "./qdrant_storage"   
QDRANT_COLLECTION = "codebase"      


SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".cpp", ".c", ".go", ".rs",
    ".rb", ".php", ".cs", ".swift", ".kt",
    ".md", ".txt", ".yaml", ".yml", ".json",
    ".html", ".css", ".sh", ".env.example", ".ipynb"
]


IGNORED_DIRS = [
    ".git", "__pycache__", "node_modules", ".venv",
    "venv", "env", "dist", "build", ".next",
    ".cache", "coverage", ".pytest_cache"
]


CHUNK_SIZE = 1500


CHUNK_OVERLAP = 200


TOP_K = 6


MIN_RELEVANCE_SCORE = 0.5


REPO_CLONE_DIR = "./cloned_repo"    
