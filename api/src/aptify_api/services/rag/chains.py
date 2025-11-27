"""Chains that wire prompts with LLMs for the RAG workflow."""

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from aptify_api.services.rag.prompts import (
    answer_prompt,
    generation_prompt,
    hallucination_prompt,
    question_rewriter_prompt,
    retrieval_grader_prompt,
    routing_prompt,
)


def build_question_router(llm):
    """Combine the routing prompt with the primary LLM."""

    return routing_prompt | llm | JsonOutputParser()


def build_retrieval_grader(llm_checker):
    """Return the retrieval grader chain."""

    return retrieval_grader_prompt | llm_checker | JsonOutputParser()


def build_rag_chain(llm):
    """Answer questions using the retrieved context."""

    return generation_prompt | llm | StrOutputParser()


def build_hallucination_grader(llm_checker):
    """Check whether the generation is grounded in the provided facts."""

    return hallucination_prompt | llm_checker | JsonOutputParser()


def build_answer_grader(llm_checker):
    """Assess whether a generation effectively answers the question."""

    return answer_prompt | llm_checker | JsonOutputParser()


def build_question_rewriter(llm_checker):
    """Produce an improved question optimised for retrieval."""

    return question_rewriter_prompt | llm_checker | StrOutputParser()
