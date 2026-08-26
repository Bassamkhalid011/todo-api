# JOB-CARD — W7: Put an LLM Behind Your API

## Assignment
Add a POST /triage endpoint that routes incoming text to a local Ollama model (gemma3:1b) and returns a structured JSON classification.

## Provider
- Runtime: Ollama (local)
- Base URL: http://localhost:11434/v1/
- API key: "ollama" (placeholder — Ollama ignores it)
- Model: gemma3:1b

## Endpoint contract
```
POST /triage
Body:  { "text": "...", "source": "email|slack|form" }
Response 200: { "category": "bug|feature|question|other", "priority": "low|medium|high", "summary": "...", "confidence": 0.0–1.0 }
Response 503: LLM disabled (LLM_ENABLED=false)
Response 422: Validation error on input
```

## Stages
| # | Deliverable |
|---|-------------|
| 0 | This job card + `src/llm/hello.py` proving Ollama responds |
| 1 | POST /triage with Pydantic validation + LLM_STUB=1 mode |
| 2 | `prompts/triage-v1.md` versioned prompt, wired to endpoint |
| 3 | Parse → validate → repair → quarantine pipeline |
| 4 | 30 s timeout, exponential backoff, structured cost log, kill switch |
| 5 | `evals/cases.json` (8 cases), `evals/run_eval.py`, README update |

## Environment variables
| Variable | Default | Purpose |
|----------|---------|---------|
| LLM_BASE_URL | http://localhost:11434/v1/ | Ollama base URL |
| LLM_API_KEY | ollama | Ignored by Ollama but required by SDK |
| LLM_MODEL | gemma3:1b | Model name |
| LLM_STUB | 0 | Set to 1 to skip model entirely |
| LLM_ENABLED | true | Set to false to return 503 |
