import os
import shutil
from git import Repo, GitCommandError
from config import REPO_CLONE_DIR, SUPPORTED_EXTENSIONS, IGNORED_DIRS
import subprocess
import time, sys


import stat

def force_remove(func, path, exc_info):
    """Windows pe read-only files ko delete karne ke liye."""
    try : 
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception: 
        pass

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".md": "markdown",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".sh": "shell",
    ".env.example": "env",
    ".ipynb": "python"
}

class repo_loader:

    def __init__(self, repo_url, clone_dir = REPO_CLONE_DIR):
        self.repo_url = repo_url
        self.clone_dir = clone_dir

    def _clone_or_pull(self):
        def _clone_or_pull(self):
    if os.path.exists(self.clone_dir):
        if sys.platform == "win32":
            abs_path = os.path.abspath(self.clone_dir)
            for root, dirs, files in os.walk(abs_path):
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), 0o777)
                    except:
                        pass
            shutil.rmtree(abs_path, onexc=force_remove)
        else:
            shutil.rmtree(self.clone_dir)
        time.sleep(1)

    try:
        print(f"Cloning {self.repo_url} ...")
        Repo.clone_from(self.repo_url, self.clone_dir)
        print("Clone successful!")
    except GitCommandError as e:
        print(f"Clone failed: {e}")
        raise ValueError(f"Failed to clone: {e}")


    def _read_files(self):
        documents = []
        for root, dirs, files in os.walk(self.clone_dir):
            print(f"Current folder: {root}")
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in SUPPORTED_EXTENSIONS: continue
                full_path = os.path.join(root, file)
                try: 
                    content = open(full_path).read()
                except UnicodeDecodeError:
                    continue
                if len(content) < 20:
                    continue
                rel_path = os.path.relpath(full_path, self.clone_dir)
                documents.append({
                    'content': content,
                    'metadata': {   'file_path' : rel_path, 
                                    'language' : EXTENSION_TO_LANGUAGE[ext], 
                                    'repo_url' : self.repo_url, 
                                    'file_size' : len(content),
                                    'extension' : ext}})
        return documents

    def load(self):
        self._clone_or_pull()
        return self._read_files()

    def clean(self):
        shutil.rmtree(self.clone_dir)
