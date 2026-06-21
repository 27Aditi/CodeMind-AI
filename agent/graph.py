

import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from agent.tools import build_code_search_tool, build_web_search_tool
from agent.grader import RelevanceGrader
from retrieval.retriever import HybridRetriever
from config import GROQ_API_KEY, GROQ_MODEL, MIN_RELEVANCE_SCORE

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    query:            str
    original_query:   str
    retrieved_chunks: list[dict]
    web_results:      str
    relevance_score:  float
    retry_count:      int
    final_answer:     str
    needs_web_search: bool



GENERATE_PROMPT = """You are an expert software engineer assistant.
Answer the question using the provided code context.
Always cite specific file paths when referencing code.
If generating new code, match the style of the existing codebase.

Question: {query}

Code Context:
{code_context}

{web_context}

Answer:"""


def build_graph(retriever: HybridRetriever) -> object:
    grader      = RelevanceGrader()
    llm         = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
    code_tool   = build_code_search_tool(retriever)
    web_tool    = build_web_search_tool()


    def router_node(state: AgentState) -> AgentState:
        query = state["query"].lower()
        web_keywords = ["what is", "explain", "documentation", "how to install",
                        "library", "framework", "error", "exception"]
        needs_web = any(kw in query for kw in web_keywords)

        return {
            **state,
            "original_query":   state["query"],
            "needs_web_search": needs_web,
            "retry_count":      state.get("retry_count", 0),
        }

    def retrieve_node(state: AgentState) -> AgentState:
        results = retriever.search(state["query"])
        return {**state, "retrieved_chunks": results}

    def grade_node(state: AgentState) -> AgentState:
        score = grader.grade(state["query"], state["retrieved_chunks"])
        return {
            **state,
            "relevance_score": score,
            "retry_count":     state.get("retry_count", 0) + 1,
        }

    def rewrite_node(state: AgentState) -> AgentState:
        new_query = grader.rewrite_query(state["query"])
        return {**state, "query": new_query}

    def web_search_node(state: AgentState) -> AgentState:
        results = web_tool.func(state["original_query"])
        return {**state, "web_results": results}

    def generate_node(state: AgentState) -> AgentState:
        code_context = "\n\n".join([
            f"File: {r['metadata'].get('file_path', 'unknown')}\n{r['content']}"
            for r in state.get("retrieved_chunks", [])
        ])

        web_context = ""
        if state.get("web_results"):
            web_context = f"Web Search Results:\n{state['web_results']}"

        prompt = GENERATE_PROMPT.format(
            query=state["original_query"],
            code_context=code_context or "No code context found.",
            web_context=web_context,
        )

        answer = llm.invoke(prompt).content
        return {**state, "final_answer": answer}

    def route_after_grade(state: AgentState) -> str:
        if state["relevance_score"] >= MIN_RELEVANCE_SCORE:
            return "generate"
        if state["retry_count"] >= 2:
            return "generate"   
        return "rewrite"

    def route_after_router(state: AgentState) -> str:
        if state["needs_web_search"]:
            return "web_search"
        return "retrieve"

    graph = StateGraph(AgentState)

    graph.add_node("router",     router_node)
    graph.add_node("retrieve",   retrieve_node)
    graph.add_node("grade",      grade_node)
    graph.add_node("rewrite",    rewrite_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate",   generate_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges("router", route_after_router, {
        "retrieve":  "retrieve",
        "web_search": "web_search",
    })

    graph.add_edge("retrieve",   "grade")
    graph.add_edge("web_search", "generate")

    graph.add_conditional_edges("grade", route_after_grade, {
        "generate": "generate",
        "rewrite":  "rewrite",
    })

    graph.add_edge("rewrite",  "retrieve")
    graph.add_edge("generate", END)

    return graph.compile()


def run(query: str, compiled_graph) -> dict:
    initial_state = {
        "query":            query,
        "original_query":   query,
        "retrieved_chunks": [],
        "web_results":      "",
        "relevance_score":  0.0,
        "retry_count":      0,
        "final_answer":     "",
        "needs_web_search": False,
    }

    final_state = compiled_graph.invoke(initial_state)

    return {
        "answer":  final_state["final_answer"],
        "sources": final_state.get("retrieved_chunks", []),
    }
