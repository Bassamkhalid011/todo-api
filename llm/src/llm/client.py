import os
from openai import OpenAI

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/"),
            api_key=os.getenv("LLM_API_KEY", "ollama"),
            timeout=30.0,
        )
    return _client
