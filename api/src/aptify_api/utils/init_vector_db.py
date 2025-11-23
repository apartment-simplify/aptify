"""Embedding functions for vector storage and retrieval."""

import os
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# from langchain_openai import OpenAIEmbeddings

DIRECTORY_PATH = "../../../../documents"

# 2. Initialize the DirectoryLoader
# glob="**/*.pdf" ensures we get PDFs even in subfolders of api/documents
loader = DirectoryLoader(
    DIRECTORY_PATH,
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,  # Use PyPDFLoader (or PyMuPDFLoader) for parsing
    show_progress=True,  # Shows a progress bar (useful for many files)
    use_multithreading=True,  # Speeds up loading significantly
)

docs = loader.load()
print(f"Loaded {len(docs)} documents from PDFs.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Target size of chunk
    chunk_overlap=200,  # Overlap ensures context across boundaries
    separators=["\n\n", "\n", " ", ""],  # Priority order
)

doc_splits = text_splitter.split_documents(docs)


def initialize_vectorstore(doc_splits):
    persist_directory = "src/aptify_api/db/chroma"

    if not os.path.exists(persist_directory):
        print("Chroma DB does not exist. Creating a new database...")
        # Initialize Chroma from documents and save it to the directory
        vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name="rag-chroma",
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        vectorstore.persist()
    else:
        print("Chroma DB exists. Loading from the existing database...")
        # Load the existing Chroma database
        vectorstore = Chroma(persist_directory, embeddings)

    return vectorstore.as_retriever()


initialize_vectorstore(doc_splits)
