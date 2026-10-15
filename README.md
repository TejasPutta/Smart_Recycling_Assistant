# Smart Recycling Assistant

AI-powered waste classification and recycling guidance with camera detection, generative AI, scan history, and a digital-twin dashboard.

## Repository layout

```
Smart_Recycling_Assistant/
├── backend/      # FastAPI service (Python)
├── frontend/     # Web UI (separate app)
└── docs/         # API contract & architecture notes
```

## Team

| Member | Responsibility |
|--------|----------------|
| TejasPutta | Backend, AI integration, database, APIs, integration |
| Mayank-Raj9339 | Frontend |

## Tech stack

- **Backend:** Python 3.10, FastAPI, SQLAlchemy, SQLite
- **AI classification:** MobileNetV3-Large (ImageNet pretrained, CPU inference)
- **Generative guidance:** Google Gemini (`google-genai` SDK, optional)
- **Testing:** pytest + FastAPI TestClient

## Quick start (backend)

```powershell
cd backend
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Health:** http://127.0.0.1:8000/api/v1/health

## Environment variables

Copy `backend/.env.example` to `backend/.env` and edit:

| Variable | Default | Notes |
|----------|---------|-------|
| `APP_NAME` | Smart Recycling Assistant API | Shown in Swagger |
| `APP_VERSION` | 0.1.0 | |
| `APP_ENV` | development | development / staging / production |
| `API_V1_PREFIX` | /api/v1 | |
| `CORS_ORIGINS` | localhost:5173,3000 | Comma-separated |
| `DATABASE_URL` | sqlite:///./smart_recycling.db | |
| `GEMINI_API_KEY` | *(empty)* | **Optional.** Leave blank to use local guidance |
| `GEMINI_MODEL` | gemini-2.0-flash | |
| `MAX_UPLOAD_SIZE_MB` | 8 | |
| `ALLOWED_IMAGE_TYPES` | image/jpeg,image/png,image/webp | |

**Never commit `.env`.** It is git-ignored.

## API endpoints (summary)

Full contract: [`docs/api/API_CONTRACT.md`](docs/api/API_CONTRACT.md)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Service health |
| POST | `/api/v1/classify` | Classify a waste image |
| GET | `/api/v1/classify/status` | Is the ML model loaded? |
| POST | `/api/v1/guidance` | Recycling guidance (Gemini + fallback) |
| POST | `/api/v1/history` | Save a confirmed scan |
| GET | `/api/v1/history` | Paginated scan history |
| GET | `/api/v1/history/{id}` | Single scan detail |
| GET | `/api/v1/statistics` | Dashboard statistics (real data) |
| GET | `/api/v1/bins` | Virtual bin fill levels |
| GET | `/api/v1/rewards/balance` | Droplet balance + tree level |
| POST | `/api/v1/rewards/award` | Award droplets (idempotent) |
| GET | `/api/v1/rewards/history` | Reward transactions |

## Running tests

```powershell
cd backend
python -m pytest -v
```

Expected: all tests pass. The suite uses an in-memory SQLite for rewards tests and never calls Gemini.

## Project stages

- [x] **Stage 1** — Backend foundation (FastAPI, health endpoint, config, tests)
- [x] **Stage 2** — AI waste classification (MobileNetV3 + mapper)
- [x] **Stage 3** — Scan persistence (SQLite, history endpoints)
- [x] **Stage 4** — Gemini guidance + local fallback
- [x] **Stage 5** — Dashboard statistics + virtual bins
- [x] **Stage 6** — Rewards ledger + tree growth
- [x] **Stage 7** — API contract + docs

## Honest limitations

- **Bins are virtual.** They are derived from confirmed scans, not from physical sensors or IoT hardware.
- **Gemini is optional.** Without an API key, `/api/v1/guidance` returns locally-generated guidance clearly labeled `source: "fallback"`.
- **Classification uses ImageNet classes.** MobileNetV3 predicts generic object classes (e.g. "water bottle", "newspaper"). Labels are mapped to our 8 normalized waste categories via a deterministic keyword table. This is not a purpose-trained waste model.
- **No authentication.** All endpoints are public and designed for a single-user demo.