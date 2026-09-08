# 🧠 AI Research Orchestrator

A multi-agent AI system that autonomously researches a topic by breaking it down,
researching sub-topics in parallel, and synthesizing the findings into a coherent report —
exposed as an async REST API.

Built to explore **agent orchestration patterns**: task decomposition, parallel execution,
and result synthesis using LLM-powered agents that each own a single responsibility.

## Table of Contents

- [How it Works](#how-it-works)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
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

## Architecture

The API doesn't block while a report is being generated (this can take 10–30s).
Instead it follows a **job-based async pattern**, common in production systems
handling long-running tasks:

1. `POST /research` — kicks off a background job, returns a `job_id` immediately
2. `GET /research/{job_id}` — poll for status (`pending` → `running` → `done`/`failed`)
   and retrieve the result once ready

This avoids long-held HTTP connections and mirrors how real-world systems
(video rendering, large report generation, batch processing) are typically designed.

Each LLM call goes through a shared `call_agent()` function wrapped with
**exponential backoff retry** logic (via `tenacity`), so transient rate limits
or network errors don't crash the pipeline.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| LLM Provider | Google Gemini API (`google-genai`) | Generous free tier for prototyping |
| Web Framework | FastAPI | Native async support, auto-generated docs |
| Concurrency | Python `asyncio` | True parallel I/O-bound agent calls |
| Resilience | `tenacity` | Automatic retry with exponential backoff on rate limits |
| Containerization | Docker | Reproducible, portable deployment |

## Project Structure

```
agent-orchestrator/
├── agents/
│   ├── base.py          # Shared LLM call wrapper (retry logic, client setup)
│   ├── planner.py        # Breaks a topic into sub-tasks
│   ├── researcher.py      # Researches sub-tasks, runs them in parallel
│   └── writer.py          # Synthesizes findings into a final report
├── app/
│   └── main.py            # FastAPI app, job queue, endpoints
├── orchestrator.py        # Wires the three agents into a single pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
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
git clone https://github.com/YOUR_USERNAME/agent-orchestrator.git
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

## Design Decisions

- **Why an in-memory job store instead of Redis/a database?**
  Kept intentionally simple for this project's scope. In a production system,
  this would move to Redis or Postgres so job state survives restarts and
  scales across multiple API instances.

- **Why `asyncio.gather` instead of sequential loops for research?**
  Each researcher call is I/O-bound (waiting on an LLM API response). Running
  them concurrently means total research time ≈ the slowest single call,
  not the sum of all calls.

- **Why retry with exponential backoff?**
  LLM APIs are rate-limited and occasionally flaky. Retrying with increasing
  delays (2s → 4s → 8s...) handles transient failures gracefully instead of
  crashing the whole pipeline over a single dropped request.

## Roadmap

- [ ] Add real web search grounding for researcher agents (currently relies on model knowledge)
- [ ] Move job store to Redis for persistence across restarts
- [ ] Add streaming responses (SSE) instead of polling
- [ ] Simple frontend to visualize the pipeline in real time
- [ ] GitHub Actions CI to validate the Docker build on every push

## License

MIT
