# Deployment Guide — One Render Blueprint

**Recommended method: Render Blueprints.** One file (`render.yaml` at the repo root) defines
all three pieces — backend, frontend, and database — and Render creates and wires them
together automatically from a single "New Blueprint" action. This is the simplest reliable
path for this stack (FastAPI + ML/SHAP + PostgreSQL + a static React build) without writing
a Dockerfile, without a separate frontend host, and without manually copy-pasting connection
strings between dashboards.

No secrets are hardcoded anywhere — `render.yaml` uses Render's `generateValue` for the JWT
secret and `fromDatabase` for the DB connection string.

## What gets created

| Resource | Name | What it is |
|---|---|---|
| Database | `climateguard-ai-db` | Managed PostgreSQL |
| Backend | `climateguard-ai-api` | FastAPI + ML models + SHAP, `pip install`-based |
| Frontend | `climateguard-ai-web` | React static build, served from CDN |

All three come from the one `render.yaml` in this repo — nothing else to configure.

## Exact steps

1. Push this repository to GitHub (a plain `git push` to a new repo — Render deploys from
   a Git remote, it doesn't accept a raw zip upload).
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint**.
3. Connect the GitHub repo. Render detects `render.yaml` automatically and shows a preview
   of the 3 resources above.
4. Click **Apply**.

That's it — three manual actions after the repo exists on GitHub. Render then:
- provisions the Postgres database,
- builds and starts the FastAPI backend (`pip install -r backend/requirements.txt`, then
  `uvicorn app.main:app`), including generating and running the three trained models —
  they're already committed under `ml/models/`, so no training step runs at deploy time,
  the API just loads the existing `.joblib` files,
  the database tables auto-create on first backend startup (`init_db()`),
- builds the frontend (`npm ci --include=dev && npm run build`) and serves the static output.

Your live URLs (visible in the Render dashboard once each service finishes deploying):
```
Frontend:  https://climateguard-ai-web.onrender.com
Backend:   https://climateguard-ai-api.onrender.com
API docs:  https://climateguard-ai-api.onrender.com/docs
```

## If a service name is already taken

Render service URLs are `<name>.onrender.com`, and names must be unique platform-wide. If
`climateguard-ai-web` or `climateguard-ai-api` happens to already be taken by someone else,
Render will suffix the name for you (e.g. `climateguard-ai-web-x7k2`) — the deploy still
succeeds, but the two services won't automatically know each other's real URL, since
`render.yaml` has the URLs written in directly (the simplest reliable way to wire a static
site to a backend — see the note in `render.yaml` for why). If that happens:

1. Open each service's page in the Render dashboard and copy its actual `.onrender.com` URL.
2. On `climateguard-ai-api` → Environment → edit `CORS_ORIGINS` → paste the frontend's actual URL.
3. On `climateguard-ai-web` → Environment → edit `VITE_API_BASE_URL` → paste the backend's
   actual URL + `/api/v1`.
4. Click **Manual Deploy** on the frontend (env var changes need a rebuild to take effect
   for a static site; the backend picks up its env var change on its own restart).

This is a one-time fix and only needed on the (uncommon) name collision case.

## Post-deploy checklist

- [ ] `https://<backend>/api/v1/health` returns `{"status": "ok"}`
- [ ] `https://<backend>/api/v1/models/status` shows all three modules `loaded: true`
- [ ] Frontend loads and `/demo` returns a real prediction
- [ ] Signup → login → risk analysis → history flow works end-to-end

## Free-tier behavior (worth knowing, not a blocker)

- The free Postgres database expires 30 days after creation (Render's own limit, not ours) —
  fine for a demo/competition deployment; upgrade its plan in the dashboard for anything
  longer-lived, no code or config changes needed.
- The free backend service spins down after ~15 minutes idle and takes up to ~60 seconds to
  wake on the next request — the very first request after idle will be slow, subsequent ones
  are normal speed.
- Both are one-line `plan:` changes in `render.yaml` (e.g. `plan: starter`) if you want to
  remove either limitation — no other changes needed.

## Updating the live site later

Push to the branch Render is tracking (`main` by default) — Render redeploys the affected
service(s) automatically. No manual redeploy step needed for ordinary code changes.
