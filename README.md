# CodeMind AI 🧠

> Chat with any GitHub repository using AI — powered by Groq, Qdrant, and LangGraph.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green)
![Groq](https://img.shields.io/badge/Groq-Llama3.3--70B-orange)

## What is this?

CodeMind AI lets you paste any public GitHub repository URL and instantly chat with its codebase. Ask questions in plain English and get accurate answers with exact file citations.

## Tech Stack

- **LLM** — Groq (Llama 3.3 70B)
- **Embeddings** — sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB** — Qdrant (in-memory)
- **Search** — Hybrid BM25 + Vector with RRF fusion
- **Agent** — LangGraph Self-RAG
- **Web Search** — Tavily
- **UI** — Streamlit

## Setup

```bash
git clone https://github.com/yourusername/codebase-rag
cd codebase-rag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run:

```bash
streamlit run ui/app.py
```

## Get API Keys

- Groq — https://console.groq.com
- Tavily — https://tavily.com
