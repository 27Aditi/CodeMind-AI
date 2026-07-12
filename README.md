# CodeMind AI 

> Chat with any GitHub repository using AI — understand any codebase instantly.

[[Live Demo](https://img.shields.io/badge/Live%20Demo-codemind--ai.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit)](https://codemind-ai.streamlit.app/)
[Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
[LangGraph](https://img.shields.io/badge/LangGraph-Agent-green?style=for-the-badge)
[Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange?style=for-the-badge)
[Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-purple?style=for-the-badge)

---

## Live Demo

**[https://codemind-ai.streamlit.app/](https://codemind-ai.streamlit.app/)**

Paste any public GitHub repository URL and start chatting with its codebase instantly — no setup required.

---

## What is CodeMind AI?

CodeMind AI is an AI-powered tool that lets you have a conversation with any GitHub repository. Instead of manually reading through hundreds of files, just ask questions in plain English and get accurate answers with exact file citations.

Whether you're onboarding to a new codebase, doing a code review, or trying to understand how a library works internally — CodeMind AI has you covered.

---

## Features

- **Hybrid Search** — Combines semantic vector search with BM25 keyword search using Reciprocal Rank Fusion (RRF) for maximum retrieval accuracy
- **Self-RAG Agent** — Automatically grades retrieved chunks for relevance, rewrites queries when needed, and retries until it gets good results
- **Web Search Fallback** — Falls back to Tavily web search when the codebase doesn't contain the answer
- **File Citations** — Every answer includes exact file paths and source code chunks so you can verify
- **Blazing Fast** — Powered by Groq's ultra-fast inference engine running Llama 3.3 70B
- **Beautiful UI** — Clean, modern chat interface built with Streamlit

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — Llama 3.3 70B |
| Agent Framework | LangGraph (Self-RAG) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Database | Qdrant (in-memory) |
| Keyword Search | BM25 via rank-bm25 |
| Web Search | Tavily |
| Frontend | Streamlit |
| Repo Loading | GitPython |

---

## Project Structure

```
codemind-ai/
├── agent/
│   ├── graph.py          # LangGraph Self-RAG agent
│   ├── grader.py         # Relevance grader + query rewriter
│   └── tools.py          # Code search + web search tools
├── ingest/
│   ├── repo_loader.py    # GitHub repo cloner + file reader
│   ├── code_splitter.py  # Language-aware code chunker
│   └── embedder.py       # Sentence transformer embeddings
├── retrieval/
│   ├── vector_store.py   # Qdrant in-memory vector store
│   └── retriever.py      # Hybrid BM25 + vector retriever with RRF
├── ui/
│   └── app.py            # Streamlit frontend
├── config.py             # Configuration and constants
├── requirements.txt      # Dependencies
└── .env                  # API keys (not committed)
```

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/27Aditi/codemind-ai
cd codemind-ai
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API keys

Create a `.env` file in the root folder:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get your keys here:
- **Groq** → https://console.groq.com
- **Tavily** → https://tavily.com

### 5. Run

```bash
streamlit run ui/app.py
```

Open **http://localhost:8501** in your browser.

---

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | 1500 | Characters per chunk |
| `CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `TOP_K` | 6 | Results to retrieve |
| `MIN_RELEVANCE_SCORE` | 0.5 | Minimum relevance threshold |
| `GROQ_MODEL` | llama-3.3-70b-versatile | LLM model |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embedding model |

---

## Supported File Types

Python, JavaScript, TypeScript, JSX, TSX, Java, C, C++, Go, Rust, Ruby, PHP, C#, Swift, Kotlin, Markdown, JSON, YAML, HTML, CSS, Shell, Jupyter Notebooks

---

## Contributing

Pull requests are welcome! Feel free to open an issue for bugs or feature requests.

---

## License

MIT License — feel free to use this project for anything.
