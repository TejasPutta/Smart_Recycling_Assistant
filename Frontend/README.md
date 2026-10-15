# Smart Recycling Assistant: frontend

React + Vite frontend for the Smart Recycling Assistant. Point a camera at an item, see what it is and how to recycle it, confirm the disposal, and earn water droplets that grow a tree.

## Run it

Start the backend first (from the `Backend/` folder):

```bash
uvicorn app.main:app --reload
```

Then, in a second terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The camera only works on `localhost` or `https`.

## Settings (`frontend/.env`)

| Variable | Default | What it does |
|----------|---------|--------------|
| `VITE_API_URL` | `http://127.0.0.1:8000/api/v1` | Where the backend lives |
| `VITE_USER_ID` | `user-1` | The single user that earns droplets (there is no login) |

Restart `npm run dev` after changing `.env`. The backend must allow the frontend address in its own `CORS_ORIGINS`.

## Screens

- **Scan** (`/`): live camera or image upload, a tracking frame that turns green (recyclable) or red (hazardous), recycling steps, and Confirm disposal.
- **Digital Twin** (`/twin`): virtual bins, statistics and scan history.
- **Tree Game** (`/tree`): your tree, level, droplet balance and droplet history.

## How a scan works

1. The camera image is cropped to the area inside the tracking frame and sent to `POST /classify`.
2. The frame locks on only when confidence is at least 35%. Hazardous categories (`battery`, `chemical`, `hazardous`) give a red frame, unknown gives amber, everything else gives green.
3. For a confident result, `POST /guidance` fetches recycling steps. The badge says whether they came from Gemini or the built-in fallback.
4. **Confirm disposal** saves the scan (`POST /history`) and then awards droplets (`POST /rewards/award`). Nothing is saved without that click.

Rules from the API contract that the UI follows: the answer source is always visible, demo results (model not loaded) can't be saved or rewarded, bins are labelled virtual, and scans are never auto-saved.

## 60-second demo script

1. Open the app. Point out that the status banner is hidden, which means the AI model is live.
2. Start the camera, hold up a plastic bottle, and let the frame lock green. Show the recycling steps and the source badge.
3. Press Confirm disposal. Droplets fall and the balance updates.
4. Open Digital Twin: the plastic bin has risen and the scan is in the history.
5. Open Tree Game: the tree and droplet history have updated.
6. Hold up something hazardous (a lampshade) and show the red frame.

The backend uses a general ImageNet model with keyword matching, not a model trained on waste. Rehearse your demo items before presenting. Items that tend to map cleanly: water bottle, plastic bag, newspaper, envelope, banana, lampshade. A phone may be labelled as a battery.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Red banner: can't reach the backend | Start the backend, check `VITE_API_URL`, press Retry |
| Red banner: took too long | The first request makes the backend load the model. Wait a few seconds and press Retry |
| Amber banner: AI model offline | The model failed to load. Scans return a placeholder and can't be saved. Check the backend terminal |
| Camera won't start | Allow camera access in the browser. Use `localhost` or `https`. Close other apps using the camera. Use Upload image as a backup |
| Request blocked by CORS | Add the frontend address (for example `http://localhost:5173`) to `CORS_ORIGINS` in `Backend/.env` and restart the backend |
| Upload rejected | Use JPEG, PNG or WebP under 8 MB |

## Tuning

| What | Where |
|------|-------|
| How confident a scan must be to lock on | `CONFIDENCE_LOCK_THRESHOLD` in `src/utils/categories.js` |
| Which categories count as hazardous | `HAZARD_CATEGORIES` in `src/utils/categories.js` |
| How often live scan sends a frame | `LIVE_INTERVAL_MS` in `src/components/ImageCapture.jsx` |
| Colours and glow | the tokens at the top of `src/index.css` |
| Strength of the screen scanlines | the `rgba(0, 0, 0, 0.16)` value in `body::before` in `src/index.css` |

## Project layout

```
frontend/
├── index.html
├── vite.config.js
├── .env
└── src/
    ├── main.jsx           entry point, loads fonts and theme
    ├── App.jsx            routes, page titles, error boundary
    ├── index.css          the neon theme
    ├── api/client.js      every backend call
    ├── utils/             category and colour rules, async helper
    ├── components/        reusable UI pieces
    └── pages/             Scan, Digital Twin, Tree Game
```

Build for production with `npm run build` (output goes to `dist/`).
