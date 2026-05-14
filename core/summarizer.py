"""
core/summarizer.py — Map-reduce summarization and title generation.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    LLM_TEMPERATURE_SUMMARIZE,
    SUMMARIZE_CHUNK_SIZE,
    SUMMARIZE_CHUNK_OVERLAP,
)
from core.llm import get_llm


def _split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=SUMMARIZE_CHUNK_SIZE,
        chunk_overlap=SUMMARIZE_CHUNK_OVERLAP,
    )
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    """Map-reduce summarize a full transcript."""
    llm = get_llm(temperature=LLM_TEMPERATURE_SUMMARIZE)

    # Map: summarise each chunk
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}"),
    ])
    map_chain = map_prompt | llm | StrOutputParser()

    chunks = _split_transcript(transcript)
    chunk_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)

    # Reduce: merge chunk summaries into final
    reduce_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert meeting summarizer. Combine these partial summaries "
            "into one final professional meeting summary in bullet points.",
        ),
        ("human", "{text}"),
    ])
    reduce_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | reduce_prompt
        | llm
        | StrOutputParser()
    )
    return reduce_chain.invoke(combined)


def generate_title(transcript: str) -> str:
    """Generate a short professional meeting title (≤8 words)."""
    llm = get_llm(temperature=LLM_TEMPERATURE_SUMMARIZE)
    title_chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )
    return title_chain.invoke(transcript[:2000])
