"""
core/llm.py — Single LLM factory. Import from here everywhere.
Eliminates the get_llm() duplication across extractor/summarizer/rag_engine.
"""

import os
from functools import lru_cache

from langchain_mistralai import ChatMistralAI

from config import MISTRAL_API_KEY, MISTRAL_MODEL


@lru_cache(maxsize=4)
def get_llm(temperature: float = 0.3) -> ChatMistralAI:
    """Return a cached Mistral LLM instance for a given temperature."""
    if not MISTRAL_API_KEY:
        raise EnvironmentError(
            "MISTRAL_API_KEY is not set. Add it to your .env file."
        )
    return ChatMistralAI(
        model=MISTRAL_MODEL,
        mistral_api_key=MISTRAL_API_KEY,
        temperature=temperature,
    )
