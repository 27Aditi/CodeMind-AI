

from langchain_core.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

from retrieval.retriever import HybridRetriever
from config import TAVILY_API_KEY, TOP_K


def build_code_search_tool(retriever: HybridRetriever) -> Tool:

    def search_code(query: str) -> str:
        results = retriever.search(query, top_k=TOP_K)

        if not results:
            return "No relevant code found for this query."

        output = []
        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            output.append(
                f"[{i}] File: {meta.get('file_path', 'unknown')} "
                f"(chunk {meta.get('chunk_index', 0) + 1}/{meta.get('total_chunks', 1)})\n"
                f"{'-' * 50}\n"
                f"{r['content']}\n"
            )

        return "\n".join(output)

    return Tool(
        name="search_codebase",
        func=search_code,
        description=(
            "Search the indexed GitHub codebase for relevant code chunks. "
            "Use this for questions about how the code works, where features "
            "are implemented, or to find existing patterns and functions. "
            "Input should be a search query string."
        ),
    )


def build_web_search_tool() -> Tool:
    tavily = TavilySearchResults(
        max_results=3,
        tavily_api_key=TAVILY_API_KEY,
    )

    def search_web(query: str) -> str:
        results = tavily.invoke(query)

        if not results:
            return "No web results found."

        output = []
        for i, r in enumerate(results, 1):
            output.append(
                f"[{i}] {r.get('url', '')}\n"
                f"{r.get('content', '')}\n"
            )

        return "\n".join(output)

    return Tool(
        name="search_web",
        func=search_web,
        description=(
            "Search the web for documentation, library references, or concepts "
            "not found in the codebase. Use this when the question requires "
            "external knowledge about how a library or framework works."
        ),
    )
