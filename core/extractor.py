"""
core/extractor.py — Extract action items, decisions, and open questions.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from config import LLM_TEMPERATURE_EXTRACT
from core.llm import get_llm


def _build_chain(system_prompt: str):
    llm = get_llm(temperature=LLM_TEMPERATURE_EXTRACT)
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    chain = _build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found, say 'No action items found.'"
    )
    return chain.invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    chain = _build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found, say 'No key decisions found.'"
    )
    return chain.invoke(transcript)


def extract_questions(transcript: str) -> str:
    chain = _build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found, say 'No open questions found.'"
    )
    return chain.invoke(transcript)
