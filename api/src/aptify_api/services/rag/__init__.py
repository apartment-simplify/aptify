import os
from langgraph.graph import END, StateGraph, START
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

from aptify_api.services.rag.chains import (
    build_answer_grader,
    build_hallucination_grader,
    build_question_rewriter,
    build_question_router,
    build_rag_chain,
    build_retrieval_grader,
)
from aptify_api.utils.init_vector_db import initialize_vectorstore
from aptify_api.utils.rag import GraphState, RagGraphNodes

# from aptify_api.app import retriever
retriever = initialize_vectorstore()

# from utils.init_vector_db import initialize_vectorstore

load_dotenv()
# from langchain_openai import ChatOpenAI

### Router
# local_llm = 'mistral'
# LLM
model_name = os.getenv("MODEL", "llama3.1")
llm = OllamaLLM(model=model_name, format="json", temperature=0)
llm_checker = ChatOllama(
    model="llama3.1", temperature=0  # Make sure to run `ollama pull llama3.1` first
)
# llm_checker = ChatOpenAI(model="gpt-4o-mini")

question_router = build_question_router(llm)
retrieval_grader = build_retrieval_grader(llm_checker)
rag_chain = build_rag_chain(llm)
hallucination_grader = build_hallucination_grader(llm_checker)
answer_grader = build_answer_grader(llm_checker)
question_rewriter = build_question_rewriter(llm_checker)

### Search
web_search_tool = TavilySearch(k=3)

rag_nodes = RagGraphNodes(
    retriever=retriever,
    rag_chain=rag_chain,
    question_router=question_router,
    question_rewriter=question_rewriter,
    retrieval_grader=retrieval_grader,
    web_search_tool=web_search_tool,
    hallucination_grader=hallucination_grader,
    answer_grader=answer_grader,
)


workflow = StateGraph(GraphState)

# Define the nodes via the reusable handlers
workflow.add_node("web_search", rag_nodes.web_search)
workflow.add_node("retrieve", rag_nodes.retrieve)
workflow.add_node("grade_documents", rag_nodes.grade_documents)
workflow.add_node("generate", rag_nodes.generate)
workflow.add_node("transform_query", rag_nodes.transform_query)

# Build graph
workflow.add_conditional_edges(
    START,
    rag_nodes.route_question,
    {
        "web_search": "web_search",
        "vectorstore": "retrieve",
    },
)
workflow.add_edge("web_search", "generate")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    rag_nodes.decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "retrieve")
workflow.add_conditional_edges(
    "generate",
    rag_nodes.grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

# Compile
app = workflow.compile()
if __name__ == "__main__":
    initial_state: GraphState = {
        "question": "Who pays stamp duty on tenancy agreement?",
        "generation": "",
    }
    final_state = app.invoke(initial_state)
    print("Final generation:")
    print(final_state)
