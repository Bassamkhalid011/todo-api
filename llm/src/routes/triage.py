import json
import os
import time
import random
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from openai import APITimeoutError, RateLimitError, APIStatusError

from src.llm.client import get_client
from src.llm.schema import TriageInput, TriageOutput

router = APIRouter()

PROMPT_VERSION = "triage-v1"
_prompt_cache: str | None = None

QUARANTINE_FILE = Path("logs/quarantine.jsonl")
COST_LOG_FILE = Path("logs/cost.jsonl")

logger = logging.getLogger(__name__)


def _load_prompt() -> str:
    global _prompt_cache
    if _prompt_cache is None:
        p = Path("prompts/triage-v1.md")
        _prompt_cache = p.read_text(encoding="utf-8")
    return _prompt_cache


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        # drop first and last fence lines
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        raw = "\n".join(inner).strip()
    return raw


def _parse_output(raw: str) -> TriageOutput:
    cleaned = _strip_fences(raw)
    data = json.loads(cleaned)
    return TriageOutput(**data)


def _quarantine(text: str, source: str, raw: str, error: str) -> None:
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "text_snippet": text[:200],
        "raw_response": raw,
        "error": error,
    }
    with QUARANTINE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _log_cost(
    prompt_version: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
    needed_repair: bool,
) -> None:
    COST_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "prompt_version": prompt_version,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "duration_ms": duration_ms,
        "needed_repair": needed_repair,
    }
    with COST_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _call_model(system_prompt: str, user_content: str) -> tuple[str, int, int]:
    """Call LLM with exponential backoff. Returns (raw_text, input_tokens, output_tokens)."""
    client = get_client()
    model = os.getenv("LLM_MODEL", "gemma3:1b")
    delays = [1, 2, 4]

    for attempt, delay in enumerate(delays + [None]):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_content)},
                ],
                max_tokens=300,
            )
            raw = resp.choices[0].message.content or ""
            usage = resp.usage
            in_tok = usage.prompt_tokens if usage else 0
            out_tok = usage.completion_tokens if usage else 0
            return raw, in_tok, out_tok

        except (APITimeoutError, RateLimitError) as e:
            if delay is None:
                raise
            jitter = random.uniform(0, 0.3 * delay)
            time.sleep(delay + jitter)

        except APIStatusError as e:
            if e.status_code in (500, 502, 503, 504):
                if delay is None:
                    raise
                jitter = random.uniform(0, 0.3 * delay)
                time.sleep(delay + jitter)
            else:
                raise

    raise RuntimeError("All retries exhausted")


@router.post("/triage", response_model=TriageOutput)
def triage(body: TriageInput):
    # Kill switch
    if os.getenv("LLM_ENABLED", "true").lower() == "false":
        raise HTTPException(status_code=503, detail="LLM is currently disabled")

    # Stub mode — skip model entirely
    if os.getenv("LLM_STUB", "0") == "1":
        return TriageOutput(
            category="question",
            priority="low",
            summary="Stub mode active — no model was called.",
            confidence=1.0,
        )

    system_prompt = _load_prompt()
    start = time.monotonic()

    raw, in_tok, out_tok = _call_model(system_prompt, body.text)

    duration_ms = int((time.monotonic() - start) * 1000)
    model = os.getenv("LLM_MODEL", "gemma3:1b")
    needed_repair = False

    # Parse → validate → one repair attempt → quarantine
    result: TriageOutput | None = None
    try:
        result = _parse_output(raw)
    except Exception as first_err:
        # Repair: ask model to fix its own output
        needed_repair = True
        repair_prompt = (
            "Your previous response was not valid JSON. "
            "Return ONLY the JSON object, no fences, no explanation:\n\n"
            + raw
        )
        try:
            repair_raw, r_in, r_out = _call_model(system_prompt, repair_prompt)
            in_tok += r_in
            out_tok += r_out
            result = _parse_output(repair_raw)
            raw = repair_raw
        except Exception as repair_err:
            _quarantine(body.text, body.source, raw, str(repair_err))
            raise HTTPException(
                status_code=502,
                detail="LLM returned unparseable output after repair attempt",
            )

    _log_cost(PROMPT_VERSION, model, in_tok, out_tok, duration_ms, needed_repair)
    return result
