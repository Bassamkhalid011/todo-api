"""Run this once to confirm Ollama is reachable before wiring it to the API."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)

response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL", "gemma3:1b"),
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
    max_tokens=10,
)

print("Ollama says:", response.choices[0].message.content.strip())
