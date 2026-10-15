# Backend — Smart Recycling Assistant API

FastAPI backend for the Smart Recycling Assistant hackathon project.

## Tech stack

- **Framework:** FastAPI 0.115 + Uvicorn
- **Config:** Pydantic Settings (`.env`-driven)
- **Database:** SQLite via SQLAlchemy 2.0
- **AI classification:** MobileNetV3-Large (torchvision, CPU inference)
- **Generative guidance:** `google-genai` SDK (Google Gemini, optional)
- **Testing:** pytest + HTTPX TestClient

## Local setup (Windows PowerShell)

```powershell
cd F:\Smart_Recycling_Assistant\backend

# Python 3.10 recommended (best wheel coverage for torch)
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# CPU-only PyTorch (smaller install, no CUDA needed)
python -m pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu

Copy-Item .env.example .env
```

## Run the API

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

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

Tests do **not** require a Gemini key. Gemini fallback path is exercised by
default.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Service health |
| POST | `/api/v1/classify` | Classify a waste image |
| GET | `/api/v1/classify/status` | Model availability |
| POST | `/api/v1/guidance` | Recycling guidance (Gemini + fallback) |
| POST | `/api/v1/history` | Save a confirmed scan |
| GET | `/api/v1/history` | Paginated scan history |
| GET | `/api/v1/history/{id}` | Single scan detail |
| GET | `/api/v1/statistics` | Dashboard statistics |
| GET | `/api/v1/bins` | Virtual bin fill levels |
| GET | `/api/v1/rewards/balance` | Droplet balance |
| POST | `/api/v1/rewards/award` | Award droplets (idempotent) |
| GET | `/api/v1/rewards/history` | Reward transactions |

## Folder layout

```
backend/
├── app/
│   ├── main.py                       # FastAPI app entrypoint
│   ├── core/config.py                # Settings (env-based)
│   ├── api/routes/
│   │   ├── health.py
│   │   ├── classification.py
│   │   ├── guidance.py
│   │   ├── history.py
│   │   ├── statistics.py
│   │   ├── bins.py
│   │   └── rewards.py
│   ├── schemas/                      # Pydantic request/response models
│   ├── services/
│   │   ├── classification/           # Classifier + category mapper
│   │   ├── guidance/                 # Gemini service with fallback
│   │   ├── rewards/                  # Reward ledger + tree growth
│   │   └── statistics_service.py     # Dashboard stats
│   ├── database/
│   │   ├── base.py                   # Declarative base
│   │   └── connection.py             # Engine + session factory
│   ├── models/
│   │   ├── scan.py                   # Scan ORM model
│   │   └── reward.py                 # Reward transaction ORM model
│   ├── repositories/                 # (reserved for Stage-next repos)
│   └── utils/
│       └── image_validation.py       # Upload validation
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_category_mapper.py
│   │   └── test_rewards.py
│   └── integration/
│       ├── test_health.py
│       ├── test_classification_api.py
│       ├── test_statistics_api.py
│       └── test_guidance_api.py
├── scripts/
├── storage/                          # Runtime uploads (git-ignored)
├── requirements.txt
├── pytest.ini
└── .env.example
```

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `APP_NAME` | Smart Recycling Assistant API | |
| `APP_VERSION` | 0.1.0 | |
| `APP_ENV` | development | |
| `API_V1_PREFIX` | /api/v1 | |
| `CORS_ORIGINS` | localhost:5173,3000 | Comma-separated |
| `DATABASE_URL` | sqlite:///./smart_recycling.db | |
| `GEMINI_API_KEY` | *(empty)* | Optional — leave blank for fallback |
| `GEMINI_MODEL` | gemini-2.0-flash | |
| `MAX_UPLOAD_SIZE_MB` | 8 | |
| `ALLOWED_IMAGE_TYPES` | image/jpeg,image/png,image/webp | |

## Status

- [x] **Stage 1** — Foundation (app, health, tests)
- [x] **Stage 2** — AI waste classification
- [x] **Stage 3** — SQLite persistence + history endpoints
- [x] **Stage 4** — Gemini guidance + fallback
- [x] **Stage 5** — Dashboard statistics + virtual bins
- [x] **Stage 6** — Rewards ledger + tree growth
- [x] **Stage 7** — API contract + docs

## Honest limitations

- Bins are **virtual** — derived from scans, not physical sensors.
- Gemini is **optional** — no key means local fallback, clearly labeled.
- Classification uses **ImageNet classes** mapped via keyword table, not a
  purpose-trained waste model. Do not claim bounding-box detection; the
  service performs image classification only.
- **No authentication.** Single-user demo API.

## Troubleshooting

- **`pip install torch` hangs on "Preparing metadata"** → you're on Python 3.13/3.14. Use Python 3.10 (as documented above).
- **`ModuleNotFoundError: No module named 'app'`** → you ran Python from the repo root. Always `cd backend` first.
- **`sqlite3.OperationalError: no such table`** → run the server once so `init_db()` creates tables, or check that `DATABASE_URL` points to a writable path.
- **Gemini always returns fallback** → set `GEMINI_API_KEY` in `backend/.env`. The response `note` field explains why fallback was used.