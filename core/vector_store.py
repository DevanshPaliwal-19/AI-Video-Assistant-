"""
core/vector_store.py — ChromaDB vector store with HuggingFace embeddings.
"""

import torch
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    RAG_TOP_K,
    VECTOR_DB_DIR,
    VECTOR_CHUNK_SIZE,
    VECTOR_CHUNK_OVERLAP,
)


def _get_embeddings() -> HuggingFaceEmbeddings:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": device},
    )


def build_vector_store(transcript: str) -> Chroma:
    """Chunk transcript and build a persistent Chroma vector store."""
    print("Building vector store…")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=VECTOR_CHUNK_SIZE,
        chunk_overlap=VECTOR_CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(transcript)
    docs = [
        Document(page_content=chunk, metadata={"chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]
    embeddings = _get_embeddings()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION,
        persist_directory=str(VECTOR_DB_DIR),
    )
    print(f"Vector store built — {len(docs)} chunks indexed.")
    return vector_store


def load_vector_store() -> Chroma:
    """Load an existing Chroma vector store from disk."""
    embeddings = _get_embeddings()
    return Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
    )


def get_retriever(vector_store: Chroma, k: int = RAG_TOP_K):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
