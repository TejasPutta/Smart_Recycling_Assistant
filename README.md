# Smart Recycling Assistant

AI-powered waste classification and recycling guidance with camera detection, generative AI, scan history, and a digital-twin dashboard.

## Repository layout

```
Smart_Recycling_Assistant/
├── backend/      # FastAPI service (Python) — TejasPutta
├── frontend/     # Web UI — Mayank-Raj9339
└── docs/         # API contract & architecture notes
```

## Team

| Member | Responsibility |
|--------|----------------|
| TejasPutta | Backend, AI integration, database, APIs, integration |
| Mayank-Raj9339 | Frontend |

## Quick start (backend)

```powershell
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open:
- Swagger UI: http://127.0.0.1:8000/docs
- Health:     http://127.0.0.1:8000/api/v1/health

Full setup details: see [`backend/README.md`](backend/README.md).

## Project stages

- [x] **Stage 1** — Backend foundation (FastAPI + health endpoint + tests)
- [ ] Stage 2 — AI waste classification
- [ ] Stage 3 — Multi-object scanning
- [ ] Stage 4 — Gemini recycling guidance
- [ ] Stage 5 — Database, bins, history, statistics
- [ ] Stage 6 — Rewards & virtual tree
- [ ] Stage 7 — Integration & docs finalization