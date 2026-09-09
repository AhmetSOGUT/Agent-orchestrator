# 🧠 AI Research Orchestrator

[![CI](https://github.com/AhmetSOGUT/Agent-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmetSOGUT/Agent-orchestrator/actions/workflows/ci.yml)


A multi-agent AI system that autonomously researches a topic by breaking it down,
researching sub-topics in parallel, and synthesizing the findings into a coherent report —
exposed as an async REST API.

Built to explore **agent orchestration patterns**: task decomposition, parallel execution,
and result synthesis using LLM-powered agents that each own a single responsibility —
with the configuration management, logging, testing, and abstraction layers you'd expect
in a real backend service, not just a prototype script.

## Table of Contents

- [How it Works](#how-it-works)
- [Architecture](#architecture)
- [Engineering Highlights](#engineering-highlights)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [API Usage](#api-usage)
- [Design Decisions](#design-decisions)
- [Roadmap](#roadmap)

## How it Works

Give the API a topic, and three specialized agents collaborate to produce a report:

1. **Planner Agent** — breaks the topic into 3–4 independently researchable sub-topics
2. **Researcher Agents** — investigate all sub-topics **concurrently** (`asyncio.gather`),
   not sequentially — cutting total latency roughly by the number of sub-topics
3. **Writer Agent** — synthesizes the raw findings into a single, well-structured
   Markdown report

```
Topic → Planner → [Sub-task 1, Sub-task 2, Sub-task 3]
                        ↓ (parallel)
              Researcher × N  →  findings
                        ↓
                   Writer Agent
                        ↓
                  Final Report
```

Every agent is a class inheriting from a shared `BaseAgent`, giving each one its own
system prompt, its own logger, and a consistent interface (`run()`) — see
[Engineering Highlights](#engineering-highlights) below.

## Architecture

The API doesn't block while a report is being generated (this can take 10–30s).
Instead it follows a **job-based async pattern**, common in production systems
handling long-running tasks:

1. `POST /research` — kicks off a background job, returns a `job_id` immediately
2. `GET /research/{job_id}` — poll for status (`pending` → `running` → `done`/`failed`)
   and retrieve the result once ready
3. `GET /health` — standard health check endpoint for deployment/monitoring

This avoids long-held HTTP connections and mirrors how real-world systems
(video rendering, large report generation, batch processing) are typically designed.

Each LLM call goes through a shared `call_agent()` function wrapped with
**exponential backoff retry** logic (via `tenacity`), so transient rate limits
or network errors don't crash the pipeline — retries are automatically logged
as warnings so failures are visible, not silent.

## Engineering Highlights

Beyond the core orchestration logic, this project applies a few patterns you'd
expect in a real backend codebase rather than a notebook-style script:

- **Object-oriented agents** — `PlannerAgent`, `ResearcherAgent`, and `WriterAgent`
  all inherit from an abstract `BaseAgent`, which owns the shared LLM-calling logic
  and per-agent logger setup. Adding a new agent means writing a system prompt and
  a `run()` method, nothing else.
- **Centralized, validated configuration** — all settings (API keys, model name,
  retry limits, log level) are loaded through a single `pydantic-settings` class.
  A missing or malformed `.env` value fails immediately at startup instead of
  causing an obscure runtime error mid-request.
- **Structured logging** — every module logs through a shared configuration
  (timestamped, leveled, tagged by module name) instead of scattered `print()`
  statements, making it possible to trace exactly what each agent did and when.
- **Abstracted job storage** — the API depends on a `JobStore` interface, not a
  concrete dictionary. The current implementation (`InMemoryJobStore`) can be
  swapped for a Redis- or Postgres-backed store without touching any endpoint code —
  a direct application of the dependency inversion principle.
- **Automated tests with mocking** — `pytest` + `pytest-mock` cover the planner's
  JSON-parsing logic (including malformed-response fallback) and the job store's
  behavior, without making real API calls during test runs.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| LLM Provider | Google Gemini API (`google-genai`) | Generous free tier for prototyping |
| Web Framework | FastAPI | Native async support, auto-generated docs |
| Concurrency | Python `asyncio` | True parallel I/O-bound agent calls |
| Configuration | `pydantic-settings` | Type-safe, validated environment config |
| Resilience | `tenacity` | Automatic retry with exponential backoff on rate limits |
| Testing | `pytest`, `pytest-asyncio`, `pytest-mock` | Async-aware unit tests without real API calls |
| Containerization | Docker | Reproducible, portable deployment |

## Project Structure

```
agent-orchestrator/
├── agents/
│   ├── agent.py           # BaseAgent abstract class (shared logic for all agents)
│   ├── base.py             # Low-level LLM call wrapper (client, retry logic)
│   ├── planner.py           # PlannerAgent - breaks a topic into sub-tasks
│   ├── researcher.py         # ResearcherAgent - researches sub-tasks in parallel
│   └── writer.py             # WriterAgent - synthesizes findings into a report
├── app/
│   └── main.py                # FastAPI app, endpoints, background job execution
├── tests/
│   ├── test_planner.py         # Planner JSON-parsing behavior (mocked LLM calls)
│   └── test_job_store.py        # InMemoryJobStore behavior
├── examples/
│   ├── test.py                  # End-to-end pipeline run (planner -> researcher -> writer)
│   └── async_demo.py             # Sync vs async performance demonstration
├── orchestrator.py               # Wires the three agents into a single pipeline
├── job_store.py                   # JobStore interface + InMemoryJobStore implementation
├── config.py                       # Centralized, validated settings (pydantic-settings)
├── logging_config.py                # Shared logging setup
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Getting Started

### Prerequisites
- Python 3.11+
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- (Optional) Docker Desktop

### Local Setup

```bash
# Clone the repo
git clone https://github.com/AhmetSOGUT/Agent-orchestrator.git
cd agent-orchestrator

# Create environment (conda example)
conda create -n agent-orchestrator python=3.11 -y
conda activate agent-orchestrator

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# then edit .env and add: GOOGLE_API_KEY=your-key-here

# Run the API
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

### Run with Docker

```bash
docker compose up --build
```

### Running Examples

```bash
python -m examples.test          # Full pipeline run, saves output to rapor.md
python -m examples.async_demo    # Sync vs async performance demo
```

## Running Tests

Tests mock all LLM calls — no API key or network access needed to run them:

```bash
pytest -v
```

With coverage:

```bash
pip install pytest-cov
pytest --cov=. --cov-report=term-missing
```

## API Usage

**Start a research job:**

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "The state of electric vehicle adoption in Turkey"}'
```

Response:
```json
{ "job_id": "3d2bcc5b-c898-41d3-bc71-761d52550aae", "status": "pending" }
```

**Poll for the result:**

```bash
curl http://127.0.0.1:8000/research/3d2bcc5b-c898-41d3-bc71-761d52550aae
```

Response (once done):
```json
{
  "status": "done",
  "result": {
    "topic": "...",
    "subtasks": ["...", "...", "..."],
    "findings": { "...": "..." },
    "report": "# Full markdown report here"
  }
}
```

**Health check:**

```bash
curl http://127.0.0.1:8000/health
```

## Design Decisions

- **Why object-oriented agents instead of plain functions?**
  Each agent owns its own prompt, its own logger, and a consistent `run()` interface
  through a shared `BaseAgent`. This makes it straightforward to add new agents,
  give an agent a different model or config, or mock an agent entirely in tests —
  all things that get awkward with loose functions.

- **Why an in-memory job store instead of Redis/a database?**
  The `JobStore` abstract interface means the storage backend is a swappable
  implementation detail, not something baked into the API layer. `InMemoryJobStore`
  is intentionally simple for this project's scope; moving to Redis or Postgres
  for persistence across restarts and multi-instance deployments is a matter of
  writing one new class, not rewriting the API.

- **Why `asyncio.gather` instead of sequential loops for research?**
  Each researcher call is I/O-bound (waiting on an LLM API response). Running
  them concurrently means total research time ≈ the slowest single call,
  not the sum of all calls.

- **Why retry with exponential backoff?**
  LLM APIs are rate-limited and occasionally flaky. Retrying with increasing
  delays (2s → 4s → 8s...) handles transient failures gracefully instead of
  crashing the whole pipeline over a single dropped request — and every retry
  is logged, so failures are visible rather than silent.

- **Why validate configuration with pydantic-settings instead of raw `os.getenv`?**
  A missing or malformed environment variable fails loudly at startup, with a
  clear validation error, instead of surfacing as an obscure `AttributeError`
  or `None`-related bug deep inside a request handler.

## Roadmap

- [ ] Add real web search grounding for researcher agents (currently relies on model knowledge)
- [ ] Move job store to Redis for persistence across restarts
- [ ] Add streaming responses (SSE) instead of polling
- [ ] Simple frontend to visualize the pipeline in real time
- [ ] GitHub Actions CI to run tests and validate the Docker build on every push
- [ ] LLM tracing/observability (e.g. Langfuse) for per-call cost and latency visibility

## License

MIT
