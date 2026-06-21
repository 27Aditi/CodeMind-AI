

import logging
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, GROQ_MODEL, MIN_RELEVANCE_SCORE

logger = logging.getLogger(__name__)

GRADE_PROMPT = """You are a relevance grader for a code search system.

Question: {query}

Code chunk:
{chunk}

Is this code chunk relevant to answering the question?
Answer with a single word only: yes or no."""

REWRITE_PROMPT = """You are a query rewriter for a code search system.

The following search query did not return relevant results:
Original query: {query}

Rewrite this query using different words, synonyms, or a more specific/general phrasing.
Return ONLY the rewritten query, nothing else."""


class RelevanceGrader:

    def __init__(self):
        
        self.llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0,
        )

    def grade(self, query: str, chunks: list[dict]) -> float:
        
        if not chunks:
            return 0.0

        yes_count = 0
        for chunk in chunks:
            prompt   = GRADE_PROMPT.format(
                query=query,
                chunk=chunk["content"][:500],   
            )
            response = self.llm.invoke(prompt).content.strip().lower()
            if response == "yes":
                yes_count += 1

        score = yes_count / len(chunks)
        logger.info(f"Relevance score: {score:.2f} ({yes_count}/{len(chunks)} chunks relevant)")
        return score

    def rewrite_query(self, original_query: str) -> str:
        
        prompt   = REWRITE_PROMPT.format(query=original_query)
        response = self.llm.invoke(prompt).content.strip()
        logger.info(f"Query rewritten: '{original_query}' → '{response}'")
        return response
