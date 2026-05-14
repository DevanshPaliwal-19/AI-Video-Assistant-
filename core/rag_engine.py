"""
core/rag_engine.py — RAG chain for Q&A over the meeting transcript.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from config import LLM_TEMPERATURE_RAG, RAG_TOP_K
from core.llm import get_llm
from core.vector_store import build_vector_store, load_vector_store, get_retriever

_RAG_SYSTEM_PROMPT = """\
You are an expert meeting assistant. Answer the user's question \
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say:
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention their name clearly.

Context from meeting transcript:
{context}"""


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _build_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", _RAG_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])


def build_rag_chain(transcript: str):
    """Build a fresh RAG chain from a transcript string."""
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=RAG_TOP_K)
    llm = get_llm(temperature=LLM_TEMPERATURE_RAG)

    rag_chain = (
        {
            "context": retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
        }
        | _build_prompt()
        | llm
        | StrOutputParser()
    )
    return rag_chain


def load_rag_chain():
    """Load RAG chain from persisted vector store (no transcript needed)."""
    vector_store = load_vector_store()
    retriever = get_retriever(vector_store, k=RAG_TOP_K)
    llm = get_llm(temperature=LLM_TEMPERATURE_RAG)

    rag_chain = (
        {
            "context": retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
        }
        | _build_prompt()
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    """Invoke the RAG chain and return the answer string."""
    return rag_chain.invoke(question)
