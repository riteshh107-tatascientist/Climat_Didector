# ClimateGuard AI — Pitch Outline (10 slides)

Evidence-based throughout — every claim below is backed by something actually built and
measurable in this repo (see README for exact metrics/sources).

---

### 1. Title
**ClimateGuard AI**
AI-Powered Climate Risk, Sustainability & Resilience Intelligence Platform
SANKALP by Satin Finserv — Climate Edition Student Track

### 2. Problem
- Climate risk data in India is fragmented across meteorological, agricultural, and
  municipal sources.
- Communities and local decision-makers typically learn about flood, water, or crop-stress
  risk only after damage has occurred.
- Existing tools show raw data (rainfall charts, satellite maps) but rarely translate it into
  "what should I do, and why."

### 3. Why now
- India's climate variability is increasing measurably year over year (monsoon volatility,
  heat extremes).
- ML models for tabular risk prediction are mature, cheap to train, and don't require
  massive infrastructure — accessible to a student-built platform running real models today.
- Explainable AI (SHAP and equivalents) is now standard practice, not exotic — risk scores no
  longer need to be black boxes.

### 4. Solution
One platform, one risk engine, one explanation layer, one recommendation engine — shared
across flood, water, and agriculture risk modules, rather than five disconnected tools.

### 5. How it works
```
Environmental inputs → ML model → Risk Engine (0–100, LOW→CRITICAL)
→ Explainability (ranked contributing factors) → Recommendation Engine
→ Stored, traceable prediction → Dashboard / History / Location Intelligence
```

### 6. AI/ML
- Three trained models: flood risk (Logistic Regression, ROC-AUC 0.82), water stress
  (Logistic Regression, ROC-AUC 0.81), agriculture stress (Gradient Boosting, R² 0.26 —
  reported as-is).
- Each was chosen by comparing Logistic/Linear Regression, Random Forest, and Gradient
  Boosting head-to-head, not picked arbitrarily.
- Every prediction ships with ranked, signed factor contributions (SHAP or a documented,
  model-consistent fallback) — never a bare number.

### 7. Demo
Live, on the actual trained models: pick a location → environmental inputs → risk score →
"why" → recommended action. (See `docs/pitch/3-minute-script.md` for the exact demo beats.)

### 8. Impact
- Every assessment is traceable: input → model version → score → explanation →
  recommendation, stored in the database.
- Dashboard and Impact pages report real counts from the database; any projected/estimated
  figures (e.g. water saved) are explicitly labeled as estimates, never presented as
  measured outcomes.

### 9. Scalability / business potential
- Modular architecture: new risk modules (e.g. heatwave, air quality) plug into the same
  risk engine and recommendation engine without rearchitecting.
- Data ingestion is provider-based (`DataProvider` interface) — swapping in live IMD/NASA
  feeds requires no change to models, API, or frontend.
- Natural customers: municipal disaster-management cells, agricultural extension services,
  insurance/microfinance risk assessment (fits a Satin Finserv-style fintech context).

### 10. Vision
A shared, explainable climate risk layer that any Indian institution — government,
agricultural, financial — can build on, instead of every organization re-deriving its own
opaque risk score from scratch.
