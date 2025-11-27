"""RAG workflow utility nodes."""

from __future__ import annotations

from pprint import pprint
from typing import Any, Dict, List

from langchain_core.documents import Document
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """Tracks the state of the workflow."""

    question: str
    generation: str
    documents: Any


class RagGraphNodes:
    """Stateful wrappers for the graph nodes."""

    def __init__(
        self,
        retriever: Any,
        rag_chain: Any,
        question_router: Any,
        question_rewriter: Any,
        retrieval_grader: Any,
        web_search_tool: Any,
        hallucination_grader: Any,
        answer_grader: Any,
    ) -> None:
        self.retriever = retriever
        self.rag_chain = rag_chain
        self.question_router = question_router
        self.question_rewriter = question_rewriter
        self.retrieval_grader = retrieval_grader
        self.web_search_tool = web_search_tool
        self.hallucination_grader = hallucination_grader
        self.answer_grader = answer_grader

    def retrieve(self, state: GraphState) -> Dict[str, Any]:
        """Retrieve documents from the vectorstore."""

        print("---RETRIEVE---")
        question = state["question"]
        documents = self.retriever.invoke(question)
        return {"documents": documents, "question": question}

    def generate(self, state: GraphState) -> Dict[str, Any]:
        """Generate an answer using the retrieved documents."""

        print("---GENERATE---")
        question = state["question"]

        generation = self.rag_chain.invoke(
            {"documents": state["documents"], "question": question}
        )
        return {
            "documents": state["documents"],
            "question": question,
            "generation": generation,
        }

    def grade_documents(self, state: GraphState) -> Dict[str, Any]:
        """Filter documents that are relevant to the question."""

        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        filtered_docs: List[Document] = []
        for document in state["documents"]:

            score = self.retrieval_grader.invoke(
                {"question": question, "documents": document.page_content}
            )
            if score["score"] == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(document)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
        return {"documents": filtered_docs, "question": question}

    def transform_query(self, state: GraphState) -> Dict[str, Any]:
        """Re-write the question after filtering out irrelevant documents."""

        print("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]
        better_question = self.question_rewriter.invoke({"question": question})
        return {"documents": documents, "question": better_question}

    def web_search(self, state: GraphState) -> Dict[str, Any]:
        """Fetch web search results for the transformed question."""

        print("---WEB SEARCH---")
        question = state["question"]
        docs = self.web_search_tool.invoke({"query": question})

        results = []
        if isinstance(docs, dict):
            results = docs.get("results", [])
        elif isinstance(docs, list):
            results = docs

        web_results_list = [
            item["content"] for item in results if isinstance(item, dict)
        ]
        web_results_text = "\n\n".join(web_results_list)
        return {
            "documents": Document(page_content=web_results_text),
            "question": question,
        }

    def route_question(self, state: GraphState) -> str:
        """Decide whether to answer via the vectorstore or a web search."""

        print("---ROUTE QUESTION---")
        question = state["question"]
        source = self.question_router.invoke({"question": question})
        print(source)

        if source.get("datasource") == "web_search":
            print("---ROUTE QUESTION TO WEB SEARCH---")
            return "web_search"
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"

    def decide_to_generate(self, state: GraphState) -> str:
        """Determine whether the filtered documents were relevant enough."""

        print("---ASSESS GRADED DOCUMENTS---")
        if not state["documents"]:
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )
            return "transform_query"
        print("---DECISION: GENERATE---")
        return "generate"

    def grade_generation_v_documents_and_question(self, state: GraphState) -> str:
        """Check whether the generation is grounded and useful."""

        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader.invoke(
            {"documents": documents, "generation": generation}
        )
        if score["score"] != "yes":
            pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"

        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = self.answer_grader.invoke(
            {"question": question, "generation": generation}
        )
        if score["score"] == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
        return "not useful"
