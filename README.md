# ClimateGuard AI

**AI-powered climate risk, sustainability & resilience intelligence for India.**

Built for the **SANKALP by Satin Finserv — Climate Edition Student Track**.

---

## The problem

Climate risk data in India — rainfall, soil, water storage, crop-stress indicators — is
fragmented across meteorological, agricultural, and municipal sources. Local decision-makers
often learn about flood, water, or crop-stress risk only after damage has already occurred,
not while there's still time to act.

## The solution

ClimateGuard AI is a single platform that turns environmental readings into:

```
DATA → ANALYSIS → ML PREDICTION → RISK SCORE → EXPLANATION → RECOMMENDATION → IMPACT
```

Three genuine, trained ML models (flood, water, agriculture) share one risk engine, one
explainability layer, and one recommendation engine — so every score is transparent and
every recommendation is tied to the specific factors that produced it, not generic advice.

---

## Features

- **Flood, water, and agriculture risk models** — real scikit-learn models, compared
  head-to-head and evaluated with standard metrics (not "100% accurate" marketing claims).
- **Explainable AI** — every prediction returns ranked, signed factor contributions
  (SHAP where available, with an automatic model-consistent fallback otherwise).
- **Unified risk engine** — transparent 0–100 scoring → LOW / MODERATE / HIGH / CRITICAL.
- **Actionable recommendations** — problem / reason / action / expected benefit, generated
  from the actual factors driving each prediction, not boilerplate text.
- **Full prediction traceability** — every prediction is stored with its inputs, model
  version, score, explanation, and recommendations.
- **JWT authentication** — signup/login/logout, secure password hashing, protected routes.
- **Dashboard, location intelligence, history, and impact APIs** — all backed by real
  database queries, no hardcoded numbers.
- **React frontend** — dashboard, risk analysis, location intelligence, history, and impact
  pages, plus a public, no-login demo for judges/evaluators.
- **Public demo mode** — the ML endpoints work anonymously so anyone can try the real model
  without creating an account.

---

## Architecture

```
frontend (React + Vite + TS + Tailwind)
        │  fetch / TanStack Query
        ▼
FastAPI backend  ──────────────────────────────┐
  ├── auth (JWT, PBKDF2 password hashing)       │
  ├── climate routes (flood/water/agriculture)  │
  ├── dashboard routes (aggregation queries)     │
  ├── locations routes                           │
  └── models routes (version/performance)        │
        │                                        │
        ▼                                        │
Prediction service (app/ml/predictors.py)        │
  ├── loads joblib model + scaler + encoders     │
  ├── risk engine  (app/core/risk_engine.py)     │
  ├── explainability (app/ml/explain.py)         │
  └── recommendation engine                       │
        │                                        │
        ▼                                        ▼
SQLAlchemy ORM ───────────────────────► PostgreSQL / SQLite
  users · locations · environmental_observations
  predictions · risk_assessments · recommendations · model_versions

ml/ (offline, one-time)
  data/generate_datasets.py → data/datasets/*.csv
  training/train_*.py       → ml/models/*.joblib + *_metrics.json
```

---

## Technology stack

| Layer | Technology |
|---|---|
| ML | scikit-learn (Random Forest, Gradient Boosting, Logistic/Linear Regression), pandas, numpy, SHAP (with fallback explainer) |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0, PyJWT, PBKDF2-HMAC password hashing |
| Database | PostgreSQL (production) / SQLite (local dev) |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, React Router, TanStack Query, Recharts |

---

## ML models & datasets

### Datasets

`ml/data/generate_datasets.py` is the single ingestion boundary for all raw data (see its
docstring for the full explanation). **Environment limitation, stated plainly:** the sandbox
this project was built in has no outbound network access, so live IMD/NASA/data.gov.in APIs
could not be called. The `SyntheticProvider` generates data statistically anchored to
publicly documented Indian climate facts (IMD long-period rainfall averages by region, CPCB
municipal solid waste composition benchmarks, CEA grid emission factors) across 30 real
Indian districts, 2 years of daily data (21,900 rows per module). The `DataProvider`
interface is designed so a `LiveAPIProvider` can be dropped in with zero downstream changes
to preprocessing, training, or serving code.

| Dataset | Rows | Target |
|---|---|---|
| `flood_risk.csv` | 21,900 | `flood_event` (binary) |
| `water_stress.csv` | 21,900 | `water_stress_event` (binary) |
| `agriculture_stress.csv` | 21,900 | `crop_stress_index` (0–100 regression) |
| `waste_circular_economy.csv` | 30 | rules-based, no ML target |
| `energy_carbon.csv` | 720 | `energy_demand_mwh` / `carbon_emissions_tco2` (regression) |

### Model evaluation (actual results, not illustrative)

Each training script compares Logistic/Linear Regression, Random Forest, and Gradient
Boosting head-to-head and saves the best performer by validation metric.

| Module | Selected model | Key metrics (test set) |
|---|---|---|
| Flood risk | Logistic Regression | Accuracy 0.746 · Precision 0.585 · Recall 0.762 · F1 0.662 · **ROC-AUC 0.822** |
| Water stress | Logistic Regression | Accuracy 0.734 · Precision 0.876 · Recall 0.720 · F1 0.790 · **ROC-AUC 0.809** |
| Agriculture stress | Gradient Boosting | MAE 4.01 · RMSE 5.00 · **R² 0.259** |

The agriculture R² is intentionally reported as-is (0.26) — crop stress is a noisier signal
than binary flood/water events in this dataset, and we're not going to pretend otherwise.
Full metrics, confusion matrices, and feature importances are in `ml/models/*_metrics.json`.

### Explainable AI

`backend/app/ml/explain.py` uses SHAP (`TreeExplainer`/`LinearExplainer`) when installed,
and automatically falls back to a documented, model-consistent contribution heuristic
(feature importance × z-score from the training distribution, signed by known risk
direction) when SHAP isn't available. Both paths return the same shape, so the API and
frontend never need to know which one ran.

---

## API endpoints

All under `/api/v1`. Full interactive docs at `/docs` (Swagger) once the backend is running.

**Auth**
- `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`

**Climate intelligence**
- `POST /predict` — unified endpoint, dispatches by `module`
- `POST /flood/predict`, `POST /water/predict`, `POST /agriculture/predict`
- `POST /waste/recommend`, `POST /energy/recommend` (rules-based, no ML in Phase 1)
- `GET /predictions/history`, `GET /predictions/{id}`

**Dashboard**
- `GET /dashboard/overview`, `/risk-distribution`, `/recent`, `/top-risk-factors`,
  `/environmental-trends`, `/location-comparison`

**Locations**
- `GET /locations`, `GET /locations/{region}/intelligence`

**Models**
- `GET /models`, `GET /models/{module}/performance`

**System**
- `GET /health`, `GET /models/status`

Prediction endpoints work **anonymously** (for judge/demo use) and attribute the prediction
to the logged-in user when a valid bearer token is present.

---

## Local setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example ../.env   # edit SECRET_KEY, DATABASE_URL
uvicorn app.main:app --reload
```

The three ML models must exist under `ml/models/` before the API starts (it fails fast at
startup otherwise). Generate them once:

```bash
python ml/data/generate_datasets.py
python ml/training/train_flood_model.py
python ml/training/train_water_model.py
python ml/training/train_agriculture_model.py
```

Run tests:
```bash
pytest backend/tests          # full suite (needs fastapi/sqlalchemy/httpx)
python -m unittest discover -s backend/tests   # logic-only tests, zero extra deps
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## Environment variables

See `.env.example` (backend/root) and `frontend/.env.example`. Never committed. At minimum,
set a real `SECRET_KEY` in production:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Deployment

One `render.yaml` Blueprint deploys the backend, frontend, and PostgreSQL database together
in a single action. See [`docs/deployment.md`](docs/deployment.md) for the exact steps.

---

## Testing status (honestly reported)

The authoring environment had **no outbound network access** — `pip install` and
`npm install` both fail there (confirmed, not assumed). This shaped what could be executed
directly versus what is written correctly but needs your environment to run:

**Actually executed and passing in the sandbox (27/27 tests, stdlib + scikit-learn + PyJWT
only, zero network-dependent installs):**
- Password hashing & JWT round-trip (`test_security.py`)
- Risk engine scoring/confidence logic (`test_risk_engine.py`)
- Recommendation engine rule dispatch (`test_recommendation_engine.py`)
- Feature engineering / encoders (`test_preprocessing.py`)
- Full ML prediction pipeline, model loading, explanation, recommendations end-to-end
  (`test_predictors.py`)
- `ml/data/generate_datasets.py`, all three `ml/training/train_*.py` scripts — actually run,
  produced the metrics quoted above
- `backend/app/models/schema.sql` — validated by executing it against real SQLite

**Written correctly, requires `pip install -r backend/requirements-dev.txt` to execute
(FastAPI/SQLAlchemy/httpx aren't installable in the sandbox — no network):**
- `test_auth_api.py`, `test_climate_api.py` (full HTTP-level integration tests via
  `fastapi.testclient.TestClient` + an isolated temp SQLite DB, see `conftest.py`)
- The FastAPI app itself (`uvicorn app.main:app`) — every file passes `py_compile`, imports
  are structurally correct, but the ASGI app was never actually started in this sandbox

**Frontend**: written by hand (no `npm install`/`vite build` possible without network); every
`.tsx`/`.ts` file passes a manual bracket-balance check and a best-effort `tsc` structural
pass with stub type declarations for packages that couldn't be installed. It has **not** been
run in a browser. Run `npm install && npm run build` in a normal environment before treating
it as verified.

---

## Impact methodology

The Impact page reports two categories, clearly separated:
- **Measured**: assessment counts, high-risk counts — direct database counts, always real.
- **Illustrative estimates** (water saved, emissions avoided): computed from a disclosed,
  fixed assumption per acted-upon alert (see `frontend/src/pages/Impact.tsx`). These are
  order-of-magnitude projections for demo purposes, explicitly labeled as estimates, and are
  never presented as measured outcomes.

---

## Limitations

- No live network access during development — synthetic-but-documented data instead of live
  IMD/NASA feeds (see "ML models & datasets" above); the ingestion interface is built for a
  live provider to be swapped in later.
- Agriculture model R² (0.26) reflects genuine noise in the crop-stress signal — reported
  honestly rather than hidden or inflated.
- JWT logout uses an in-memory revocation set — fine for a single-process demo deployment,
  needs Redis (or similar shared store) behind multiple workers in production.
- Waste and energy modules are rules-based in this phase, not ML-backed.
- Rate limiting is architected for (stateless routes, documented insertion point in
  `app/main.py`) but not enabled by default.

## Future roadmap

- Swap `SyntheticProvider` for live IMD/NASA/data.gov.in feeds via the existing
  `DataProvider` interface.
- ML models for waste and energy modules.
- Redis-backed token revocation and rate limiting for multi-worker deployment.
- Mobile app / SMS alerts for high-risk notifications.
- Multi-language support (Hindi + regional languages).

## Team

Built by Ritesh Kumar Singh for the SANKALP by Satin Finserv Climate Edition Student Track.
