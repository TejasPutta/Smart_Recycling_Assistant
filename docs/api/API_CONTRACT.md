# Smart Recycling Assistant — API Contract

Backend base URL (local): `http://127.0.0.1:8000`
All endpoints are prefixed with `/api/v1`.

Interactive docs: `http://127.0.0.1:8000/docs`

---

## Health

### `GET /api/v1/health`

Returns the service health. Safe for monitoring.

**Response 200**
```json
{
  "status": "ok",
  "service": "Smart Recycling Assistant API",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-10-15T06:30:00+00:00"
}
```

---

## Root

### `GET /`

Metadata about the API. Useful for quick discovery.

**Response 200**
```json
{
  "service": "Smart Recycling Assistant API",
  "version": "0.1.0",
  "environment": "development",
  "docs": "/docs",
  "redoc": "/redoc",
  "openapi": "/openapi.json",
  "health": "/api/v1/health"
}
```

---

## Classification

### `POST /api/v1/classify`

Upload an image → get waste classification.

**Request** — `multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | file | yes | JPEG / PNG / WebP, max 8 MB |

**Response 200**
```json
{
  "source": "model",
  "model_name": "mobilenet_v3_large_imagenet",
  "predictions": [
    {
      "label": "water bottle",
      "category": "plastic",
      "confidence": 0.87,
      "category_info": {
        "category": "plastic",
        "display_name": "Plastic",
        "recyclability": "conditional",
        "short_advice": "Rinse and remove caps..."
      }
    }
  ],
  "note": null
}
```

**Error responses**

| Status | Meaning |
|--------|---------|
| 400 | Invalid image, empty upload, or unreadable |
| 413 | Image exceeds max size |
| 415 | Unsupported MIME type |

### `GET /api/v1/classify/status`

Reports whether the real ML model is loaded. Use this to show an "AI offline — demo mode" banner.

**Response 200**
```json
{ "model_available": true }
```

---

## Guidance

### `POST /api/v1/guidance`

Generate recycling guidance for a scanned item. Uses Google Gemini when configured; falls back to local guidance on any failure.

**Request body**
```json
{
  "label": "water bottle",
  "category": "plastic",
  "confidence": 0.87
}
```

**Response 200**
```json
{
  "source": "gemini",
  "label": "water bottle",
  "category": "plastic",
  "recyclability": "conditional",
  "guidance": "### Preparation\n1. Empty and rinse...",
  "note": null
}
```

**Important:** When `source == "fallback"`, Gemini was unreachable or not configured. The `note` field explains why. Never treat fallback as a Gemini success.

---

## History

### `POST /api/v1/history`

Save a confirmed scan. **Only call this after the user explicitly confirms.**

**Request body**
```json
{
  "label": "water bottle",
  "category": "plastic",
  "confidence": 0.87,
  "source": "model",
  "predictions": [ /* same shape as /classify */ ]
}
```

**Response 201**
```json
{
  "id": 12,
  "created_at": "2026-10-15T06:31:00+00:00"
}
```

### `GET /api/v1/history`

Paginated list of scans, newest first.

**Query params**

| Name | Type | Default | Notes |
|------|------|---------|-------|
| `limit` | int | 20 | 1–100 |
| `offset` | int | 0 | ≥ 0 |
| `category` | str | — | Filter by waste category |

**Response 200**
```json
{
  "total": 3,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": 3,
      "label": "water bottle",
      "category": "plastic",
      "confidence": 0.87,
      "source": "model",
      "created_at": "2026-10-15T06:31:00+00:00"
    }
  ]
}
```

### `GET /api/v1/history/{id}`

Returns full detail including all predictions. `404` if not found.

---

## Statistics

### `GET /api/v1/statistics`

Dashboard stats computed entirely from real scan records.

**Response 200**
```json
{
  "total_scans": 42,
  "categories": [
    { "category": "plastic", "count": 18, "percentage": 42.86 },
    { "category": "paper",   "count": 12, "percentage": 28.57 }
  ],
  "recent": [
    {
      "id": 42,
      "label": "water bottle",
      "category": "plastic",
      "confidence": 0.87,
      "created_at": "2026-10-15T06:31:00+00:00"
    }
  ],
  "first_scan_at": "2026-10-10T10:00:00+00:00",
  "last_scan_at": "2026-10-15T06:31:00+00:00"
}
```

---

## Bins (Digital Twin)

### `GET /api/v1/bins`

Virtual bin fill levels. **These bins are VIRTUAL — they are computed from confirmed scans, not physical sensors.**

**Response 200**
```json
{
  "bins": [
    {
      "category": "plastic",
      "fill_percentage": 72.0,
      "estimated_items": 18,
      "status": "filling"
    }
  ],
  "total_items": 42,
  "note": "Bins are virtual — values are derived from confirmed scans, not from physical sensors."
}
```

`status` values: `empty | normal | filling | full`.

---

## Rewards

### `GET /api/v1/rewards/balance?user_id=<id>`

Current droplet balance and derived tree level.

**Response 200**
```json
{
  "user_id": "user-1",
  "droplets": 50,
  "tree_level": 1,
  "tree_progress_pct": 0.0
}
```

### `POST /api/v1/rewards/award`

Award droplets for a **confirmed** disposal. Idempotent — repeat calls with the same `(user_id, scan_id)` return `awarded: false`.

**Request body**
```json
{
  "user_id": "user-1",
  "scan_id": 42,
  "reason": "confirmed disposal"
}
```

**Response 200**
```json
{
  "awarded": true,
  "amount": 5,
  "balance": {
    "user_id": "user-1",
    "droplets": 55,
    "tree_level": 1,
    "tree_progress_pct": 10.0
  },
  "note": null
}
```

### `GET /api/v1/rewards/history?user_id=<id>`

Paginated reward transactions.

---

## Error format

All errors return:
```json
{ "detail": "Human-readable message" }
```

## CORS

The backend allows the frontend origins configured in `backend/.env` (`CORS_ORIGINS`). For local development: `http://localhost:5173`, `http://localhost:3000`, and their `127.0.0.1` equivalents.

## Notes for the frontend

- All timestamps are ISO-8601 UTC.
- `source` in classification and guidance responses tells you where the answer came from. **Never hide `source`** — it protects the demo from looking fake.
- `/classify` returns top-N predictions. The first entry is the "top" prediction, but always display confidence.
- History save is user-initiated. Do **not** auto-save scans without confirmation.