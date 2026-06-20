# Onboarding Health Dashboard

A FastAPI + vanilla JS dashboard that scores SaaS account health and surfaces AI-generated CSM recommendations.

---

## What it does

**Dashboard** — A single-page frontend that fetches all accounts from the API and renders them as cards with color-coded risk levels (Healthy / At Risk / Critical) and a summary bar showing portfolio-level counts.

**Health scoring engine** — Each account receives a 0–100 score computed from four weighted signals derived from raw account data. No ML — deterministic, inspectable math. See [Health scoring model](#health-scoring-model) below.

**AI recommendations** — When you open a single account (`GET /api/v1/accounts/{id}`), the API calls Claude (`claude-sonnet-4-6`) via the Anthropic API and returns a 2–3 sentence, account-specific CSM action recommendation alongside the health score. The recommendation is generated from the account's company name, industry, score, risk level, and individual signals.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| ORM / DB | SQLAlchemy 2.0 (DeclarativeBase), SQLite |
| Validation | Pydantic v2 |
| AI | Anthropic Claude API (`claude-sonnet-4-6`), httpx |
| Frontend | Vanilla HTML + CSS + JavaScript (no framework) |
| Tests | pytest, FastAPI TestClient |

---

## Architecture

```
backend/
  main.py              # App factory: mounts router, serves frontend as StaticFiles
  database.py          # Engine, SessionLocal, get_db dependency
  models.py            # SQLAlchemy ORM — Account table
  schemas.py           # Pydantic schemas: AccountCreate, AccountRead, AccountReadWithScore
  routers/
    accounts.py        # Route handlers for /api/v1/accounts
  services/
    health_score.py    # Pure function: compute_health_score(account) → dict
    ai_recommendations.py  # Async: generate_recommendation(account, health) → str | None
frontend/
  index.html           # Dashboard shell
  static/css/style.css
  static/js/app.js     # Fetches API, renders cards, updates summary bar
tests/
  test_accounts.py     # API endpoint tests (in-memory SQLite, dependency override)
  test_health_score.py # Unit tests for the scoring engine
```

**Key design decisions:**
- Services (`health_score`, `ai_recommendations`) are pure functions / async functions with no FastAPI or ORM imports — easy to test in isolation.
- Schemas are split: `AccountCreate` (input, no server fields) vs. `AccountRead` (output, includes `id` and `created_at`) vs. `AccountReadWithScore` (extends `AccountRead` with `health` and `recommendation`).
- The AI recommendation is only fetched on the single-account endpoint, not the list — avoids fanning out N API calls on the index page.

---

## Health scoring model

Each account is scored 0–100 from four components. Each component scores 100% (full), 50% (partial), or 0% (low) on its tier, then weights are applied. If NPS is absent, its 15% weight is redistributed proportionally across the other three components so the final score stays on a 0–100 scale.

| Component | Weight | Full (100%) | Partial (50%) | Low (0%) |
|---|---|---|---|---|
| Seat adoption | 35% | ≥ 80% of seats active | 50–79% | < 50% |
| Login engagement | 30% | ≥ 3.0 logins / active seat / 30d | 1.0–2.9 | < 1.0 |
| Support ticket load | 20% | < 0.10 tickets / active seat | 0.10–0.30 | > 0.30 |
| NPS score | 15% | ≥ 8 / 10 | 5–7 | < 5 |

**Risk thresholds:** 70–100 → Healthy · 40–69 → At Risk · 0–39 → Critical

---

## How to run locally

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd onboarding-health-dashboard

# 2. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv httpx pytest

# 4. Configure environment
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY to your Anthropic API key
# DATABASE_URL defaults to sqlite:///./onboarding.db

# 5. Start the server
uvicorn backend.main:app --reload
```

The dashboard is served at [http://localhost:8000](http://localhost:8000).  
The API is available at [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/).

> AI recommendations require a valid `ANTHROPIC_API_KEY`. Without one, the `recommendation` field returns `null` and everything else works normally.

---

## Running tests

```bash
pytest tests/
```

Tests use an in-memory SQLite database with `StaticPool` for connection isolation and override the `get_db` FastAPI dependency — no `.env` required.

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/accounts` | Create an account. Body: `AccountCreate` JSON. Returns `AccountRead` (201). |
| `GET` | `/api/v1/accounts` | List all accounts with health scores. Returns `list[AccountReadWithScore]`. No AI call. |
| `GET` | `/api/v1/accounts/{id}` | Get one account with health score and AI recommendation. Returns `AccountReadWithScore` including `recommendation`. 404 if not found. |
