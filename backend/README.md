# Backend — Smart Recycling Assistant API

FastAPI backend for the Smart Recycling Assistant hackathon project.

## Tech stack

- **Framework:** FastAPI 0.115 + Uvicorn
- **Config:** Pydantic Settings (`.env`-driven)
- **Database:** SQLite via SQLAlchemy (Stage 5)
- **AI classification:** real vision model (Stage 2)
- **Generative guidance:** Google Gemini (Stage 4)
- **Testing:** pytest + HTTPX TestClient

## Local setup (Windows PowerShell)

```powershell
cd F:\Smart_Recycling_Assistant\backend

# Use Python 3.10 (fast wheel installs, no Rust needed)
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Copy-Item .env.example .env
```

## Run the API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

| URL | What |
|-----|------|
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |
| http://127.0.0.1:8000/api/v1/health | Health check |
| http://127.0.0.1:8000/ | Root info |

## Run the tests

```powershell
python -m pytest -v
```

## Folder layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── core/config.py          # Settings (env-based)
│   ├── api/routes/             # HTTP routers
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic (AI, guidance, rewards)
│   ├── database/               # SQLAlchemy engine/session
│   ├── models/                 # ORM models
│   ├── repositories/           # DB access layer
│   └── utils/                  # Helpers (image validation)
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
├── storage/                    # Runtime uploads (git-ignored)
├── requirements.txt
└── .env.example
```

## Status

- [x] **Stage 1** — Foundation (app, health endpoint, tests)
- [ ] Stage 2 — AI waste classification
- [ ] Stage 3 — Multi-object scanning
- [ ] Stage 4 — Gemini guidance
- [ ] Stage 5 — Database, bins, history, statistics
- [ ] Stage 6 — Rewards & virtual tree
- [ ] Stage 7 — Docs, CORS finalization, demo prep