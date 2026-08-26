# FlyRank LLM API — W7 Assignment

A FastAPI endpoint that routes support tickets to a local Ollama LLM (gemma3:1b) and returns a structured JSON classification.

## Folder structure

```
llm/
├── main.py               # FastAPI app — mounts /triage
├── requirements.txt
├── .env.example          # Key names with placeholder values (safe to commit)
├── JOB-CARD.md           # Assignment brief
├── src/
│   ├── llm/
│   │   ├── client.py     # OpenAI-compatible Ollama client (30 s timeout)
│   │   ├── schema.py     # Pydantic models: TriageInput, TriageOutput
│   │   └── hello.py      # One-shot Ollama connectivity check
│   └── routes/
│       └── triage.py     # POST /triage — full pipeline
├── prompts/
│   └── triage-v1.md      # Versioned system prompt
├── evals/
│   ├── cases.json        # 8 labelled test cases
│   └── run_eval.py       # Eval runner (hits live server)
└── logs/
    ├── .gitkeep
    ├── quarantine.jsonl  # Created at runtime — bad LLM outputs
    └── cost.jsonl        # Created at runtime — per-call cost log
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- Model pulled: `ollama pull gemma3:1b`

## Setup

```bash
cd llm
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env
```

`.env` values (defaults already set in `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| LLM_BASE_URL | http://localhost:11434/v1/ | Ollama URL |
| LLM_API_KEY | ollama | Required by SDK, ignored by Ollama |
| LLM_MODEL | gemma3:1b | Model name |
| LLM_STUB | 0 | `1` = skip model, return hardcoded response |
| LLM_ENABLED | true | `false` = return 503 immediately |
| PORT | 8001 | Server port |

## Verify Ollama is running

```bash
python src/llm/hello.py
# Ollama says: ready
```

## Run the server

```bash
uvicorn main:app --reload --port 8001
```

Swagger UI: `http://localhost:8001/docs`

## API

### POST /triage

**Request body:**
```json
{ "text": "Login button is broken for all users.", "source": "email" }
```

`source` must be one of: `email`, `slack`, `form`

**Response 200:**
```json
{
  "category": "bug",
  "priority": "high",
  "summary": "Login button is broken for all users.",
  "confidence": 0.95
}
```

| Field | Values |
|-------|--------|
| category | `bug` · `feature` · `question` · `other` |
| priority | `low` · `medium` · `high` |
| summary | one sentence, max 20 words |
| confidence | 0.0 – 1.0 |

**Response 503:** LLM disabled (`LLM_ENABLED=false`)  
**Response 502:** LLM returned unparseable output after repair  
**Response 422:** Invalid request body

## Pipeline

```
Request → Pydantic validation
       → Kill switch check (LLM_ENABLED)
       → Stub check (LLM_STUB)
       → Load versioned prompt (prompts/triage-v1.md)
       → Call Ollama (30 s timeout, up to 3 retries with backoff on timeout/429/5xx)
       → Strip markdown fences
       → json.loads → TriageOutput validation
       → On failure: one repair attempt
       → On repair failure: quarantine to logs/quarantine.jsonl
       → Log cost to logs/cost.jsonl
       → Return TriageOutput
```

## Retry policy

| Attempt | Delay |
|---------|-------|
| 1st retry | 1 s + jitter |
| 2nd retry | 2 s + jitter |
| 3rd retry | 4 s + jitter |

Retries only on: `APITimeoutError`, `RateLimitError`, HTTP 5xx.  
No retry on: 400, 401, 422 (deterministic failures).

## Running evals

Start the server first, then:

```bash
python evals/run_eval.py
```

Runs all 8 labelled cases and prints pass/fail per case + overall accuracy.

## Logs

`logs/cost.jsonl` — one JSON line per successful LLM call:
```json
{"ts": "...", "prompt_version": "triage-v1", "model": "gemma3:1b", "input_tokens": 312, "output_tokens": 58, "duration_ms": 1240, "needed_repair": false}
```

`logs/quarantine.jsonl` — one JSON line per output that could not be parsed even after repair.
