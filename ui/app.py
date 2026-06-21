import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import logging
import shutil
import time

from ingest.repo_loader import repo_loader as RepoLoader
from ingest.code_splitter import CodeSplitter
from ingest.embedder import Embedder
from retrieval.vector_store import VectorStore
from retrieval.retriever import HybridRetriever
from agent.graph import build_graph, run

logging.basicConfig(level=logging.INFO)

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    * { font-family: 'Inter', sans-serif; }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    [data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
    visibility: visible !important;
    transform: none !important;
    left: 0 !important;
    min-width: 300px !important;
    }
    [data-testid="stSidebarContent"] {
    visibility: visible !important;
    display: flex !important;
    }
    [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    }

    /* Cards */
    .feature-card {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        background: rgba(255,255,255,0.12); o
        border-color: rgba(99,102,241,0.5);
        transform: translateY(-2px);
    }

    /* Hero title */
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .hero-sub {
        text-align: center;
        color: rgba(255,255,255,0.55);
        font-size: 1.1rem;
        margin-bottom: 32px;
    }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .status-ready {
        background: rgba(16,185,129,0.15);
        border: 1px solid rgba(16,185,129,0.35);
        color: #10b981;
    }
    .status-idle {
        background: rgba(156,163,175,0.15);
        border: 1px solid rgba(156,163,175,0.3);
        color: #9ca3af;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 18px 18px 4px 18px;
        padding: 14px 18px;
        margin: 8px 0;
        color: white;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    .chat-assistant {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        color: rgba(255,255,255,0.9);
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Stats bar */
    .stat-item {
        text-align: center;
        padding: 12px;
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stat-number {
        font-size: 1.6rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .stat-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.5);
        margin-top: 2px;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(102,126,234,0.4) !important;
    }

    /* Progress steps */
    .step-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        color: rgba(255,255,255,0.7);
        font-size: 0.88rem;
    }
    .step-done { color: #10b981; }
    .step-active { color: #a78bfa; }

    /* Source citation */
    .source-chip {
        display: inline-block;
        background: rgba(102,126,234,0.15);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 8px;
        padding: 3px 10px;
        font-size: 0.78rem;
        color: #a78bfa;
        margin: 2px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }

    /* Hide streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    /* Chat input */
    .stChatInput > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px !important;
    }
            
    [data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 300px !important;
    transform: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────
defaults = {
    "chat_history":  [],
    "repo_indexed":  False,
    "graph":         None,
    "retriever":     None,
    "chunk_count":   0,
    "file_count":    0,
    "current_repo":  "",
    "vs":            None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper: clean all old data ────────────────────────────────────────────
def clean_old_data():
    """Delete old vector store and cloned repo before indexing new one."""
    # Close existing Qdrant client
    # if st.session_state.vs is not None:
    #     try:
    #         st.session_state.vs.close()
    #     except Exception:
    #         pass
    #     st.session_state.vs = None

    # Reset session
    st.session_state.vs           = None
    st.session_state.graph        = None
    st.session_state.retriever    = None
    st.session_state.repo_indexed = False
    st.session_state.chat_history = []
    st.session_state.chunk_count  = 0
    st.session_state.file_count   = 0


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='font-size:2.5rem;'>🧠</div>
        <div style='font-size:1.2rem; font-weight:700; color:white; margin-top:6px;'>CodeMind AI</div>
        <div style='font-size:0.78rem; color:rgba(255,255,255,0.45); margin-top:4px;'>Codebase Intelligence</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.1); margin: 10px 0 20px;'>
    """, unsafe_allow_html=True)

    # Status
    if st.session_state.repo_indexed:
        st.markdown(f"""
        <div class='status-badge status-ready'>
            ✅ &nbsp; Ready — {st.session_state.chunk_count} chunks indexed
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-size:0.75rem; color:rgba(255,255,255,0.4); margin: 8px 0 16px; word-break:break-all;'>
            📦 {st.session_state.current_repo.split('/')[-1]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='status-badge status-idle'>⬤ &nbsp; No repo indexed</div>
        <br>
        """, unsafe_allow_html=True)

    st.markdown("<div style='color:rgba(255,255,255,0.7); font-size:0.88rem; font-weight:600; margin-bottom:8px;'>📁 Index a Repository</div>", unsafe_allow_html=True)

    repo_url = st.text_input(
        "",
        placeholder="https://github.com/user/repo",
        label_visibility="collapsed",
    )

    index_btn = st.button("🚀 Index Repository", use_container_width=True)

    if index_btn:
        if not repo_url.strip():
            st.error("Please enter a GitHub URL.")
        else:
            # ── Clean old data first ──────────────────────────────────
            clean_old_data()
            time.sleep(0.5)

            progress_placeholder = st.empty()

            try:
                steps = [
                    ("📥", "Cloning repository..."),
                    ("✂️", "Chunking code..."),
                    ("🔢", "Creating embeddings..."),
                    ("💾", "Storing in vector DB..."),
                    ("🧠", "Building AI agent..."),
                ]

                def show_steps(done_up_to):
                    html = ""
                    for i, (icon, label) in enumerate(steps):
                        if i < done_up_to:
                            html += f"<div class='step-item step-done'>✓ {icon} {label}</div>"
                        elif i == done_up_to:
                            html += f"<div class='step-item step-active'>⟳ {icon} {label}</div>"
                        else:
                            html += f"<div class='step-item'>○ {icon} {label}</div>"
                    progress_placeholder.markdown(html, unsafe_allow_html=True)

                # Step 1: Clone
                show_steps(0)
                loader    = RepoLoader(repo_url.strip())
                documents = loader.load()

                # Step 2: Chunk
                show_steps(1)
                splitter = CodeSplitter()
                chunks   = splitter.split(documents)
                chunks   = chunks[:500]

                # Step 3: Embed
                show_steps(2)
                embedder   = Embedder()
                texts      = [c["content"] for c in chunks]
                embeddings = embedder.embed(texts)

                # Step 4: Store
                show_steps(3)
                vs = VectorStore()
                vs.upsert(chunks, embeddings)
                st.session_state.vs = vs

                # Step 5: Build agent
                show_steps(4)
                retriever = HybridRetriever(vs, embedder)
                retriever.build_bm25_index(chunks)
                graph     = build_graph(retriever)

                # Done
                progress_placeholder.empty()

                st.session_state.graph        = graph
                st.session_state.retriever = retriever
                st.session_state.repo_indexed = True
                st.session_state.chunk_count  = len(chunks)
                st.session_state.file_count   = len(documents)
                st.session_state.current_repo = repo_url.strip()
                st.session_state.chat_history = []

                st.success(f"✅ Done! {len(chunks)} chunks ready.")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                progress_placeholder.empty()
                st.error(f"❌ Error: {e}")

    # Stats
    if st.session_state.repo_indexed:
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin:20px 0;'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-item'>
                <div class='stat-number'>{st.session_state.file_count}</div>
                <div class='stat-label'>Files</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-item'>
                <div class='stat-number'>{st.session_state.chunk_count}</div>
                <div class='stat-label'>Chunks</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🗑️ Clear & Index New Repo", use_container_width=True):
            clean_old_data()
            st.rerun()

    # Features info
    st.markdown("""
    <hr style='border-color:rgba(255,255,255,0.1); margin:20px 0;'>
    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem; line-height:1.8;'>
        🔍 Hybrid Vector + BM25 Search<br>
        🧠 Self-RAG Relevance Grading<br>
        🌐 Web Search Fallback<br>
        ⚡ Groq LLM (Llama 3.3 70B)<br>
        📦 Qdrant Vector Database
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════

if not st.session_state.repo_indexed:
    # ── Landing page ──────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-title'>CodeMind AI</div>
    <div class='hero-sub'>Chat with any GitHub repository using AI</div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size:2rem; margin-bottom:12px;'>🔍</div>
            <div style='color:white; font-weight:600; margin-bottom:8px;'>Hybrid Search</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem; line-height:1.6;'>
                Combines semantic vector search with BM25 keyword search for best results.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size:2rem; margin-bottom:12px;'>🧠</div>
            <div style='color:white; font-weight:600; margin-bottom:8px;'>Self-RAG Agent</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem; line-height:1.6;'>
                Automatically retries with better queries when results aren't relevant enough.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size:2rem; margin-bottom:12px;'>⚡</div>
            <div style='color:white; font-weight:600; margin-bottom:8px;'>Instant Answers</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem; line-height:1.6;'>
                Powered by Groq's ultra-fast Llama 3.3 70B model with cited sources.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How to use
    st.markdown("""
    <div class='feature-card' style='max-width:600px; margin:0 auto;'>
        <div style='color:white; font-weight:600; margin-bottom:16px; font-size:1rem;'>🚀 How to Get Started</div>
        <div style='color:rgba(255,255,255,0.65); font-size:0.88rem; line-height:2;'>
            <b style='color:#a78bfa;'>1.</b> Paste any GitHub repository URL in the sidebar<br>
            <b style='color:#a78bfa;'>2.</b> Click <b>Index Repository</b> and wait for processing<br>
            <b style='color:#a78bfa;'>3.</b> Ask anything about the codebase in plain English<br>
            <b style='color:#a78bfa;'>4.</b> Get AI-powered answers with exact file citations
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Chat interface ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:12px; margin-bottom:24px;'>
        <div style='font-size:1.4rem; font-weight:700; color:white;'>💬 Chat with</div>
        <div style='background:rgba(102,126,234,0.2); border:1px solid rgba(102,126,234,0.4);
                    border-radius:8px; padding:4px 12px; font-size:0.85rem; color:#a78bfa; font-weight:500;'>
            {st.session_state.current_repo.split('/')[-1]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    chat_container = st.container()

    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='text-align:center; padding:40px; color:rgba(255,255,255,0.35);'>
                <div style='font-size:2.5rem; margin-bottom:12px;'>💭</div>
                <div style='font-size:1rem;'>Ask anything about the codebase...</div>
                <div style='font-size:0.82rem; margin-top:8px; color:rgba(255,255,255,0.25);'>
                    e.g. "How does authentication work?" or "Where is the database connection?"
                </div>
            </div>
            """, unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"<div style='color:white;'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                with st.chat_message("assistant", avatar="🧠"):
                    st.markdown(msg["content"])

                    # Source citations
                    if msg.get("sources"):
                        sources = msg["sources"]
                        unique_files = list(set([
                            s.get("metadata", {}).get("file_path", "unknown")
                            for s in sources
                        ]))

                        chips = "".join([
                            f"<span class='source-chip'>📄 {f.split(chr(92))[-1].split('/')[-1]}</span>"
                            for f in unique_files[:5]
                        ])
                        st.markdown(f"<div style='margin-top:8px;'>{chips}</div>", unsafe_allow_html=True)

                        with st.expander(f"📎 View {len(sources)} source chunks"):
                            for i, src in enumerate(sources, 1):
                                meta = src.get("metadata", {})
                                st.markdown(f"**`{meta.get('file_path', 'unknown')}`** — chunk {meta.get('chunk_index', 0)+1}/{meta.get('total_chunks', 1)}")
                                st.code(src.get("content", "")[:500], language=meta.get("language", "text"))
                                if i < len(sources):
                                    st.markdown("---")

    # Chat input
    if prompt := st.chat_input("Ask anything about the codebase..."):

        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("🔍 Searching and thinking..."):
                result = run(prompt, st.session_state.graph)

            answer  = result["answer"]
            sources = result["sources"]

            st.markdown(answer)

            if sources:
                unique_files = list(set([
                    s.get("metadata", {}).get("file_path", "unknown")
                    for s in sources
                ]))
                chips = "".join([
                    f"<span class='source-chip'>📄 {f.split(chr(92))[-1].split('/')[-1]}</span>"
                    for f in unique_files[:5]
                ])
                st.markdown(f"<div style='margin-top:8px;'>{chips}</div>", unsafe_allow_html=True)

                with st.expander(f"📎 View {len(sources)} source chunks"):
                    for i, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(f"**`{meta.get('file_path', 'unknown')}`** — chunk {meta.get('chunk_index', 0)+1}/{meta.get('total_chunks', 1)}")
                        st.code(src.get("content", "")[:500], language=meta.get("language", "text"))
                        if i < len(sources):
                            st.markdown("---")

        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": answer,
            "sources": sources,
        })

        st.rerun()
