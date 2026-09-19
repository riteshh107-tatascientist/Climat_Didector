-- ClimateGuard AI — Database Schema
-- Dialect: written portable (SQLite for local dev; PostgreSQL for prod —
-- see app/models/orm.py SQLAlchemy models, which target both via the same
-- declarative classes). This .sql file is the canonical schema reference
-- and is validated against SQLite as part of the test suite.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    organization TEXT,
    role TEXT DEFAULT 'viewer',              -- viewer | analyst | admin
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,
    state TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    elevation_m REAL,
    pop_density_per_km2 REAL,
    flood_prone_base INTEGER DEFAULT 0,
    drought_prone_base INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region, state)
);

CREATE TABLE IF NOT EXISTS environmental_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL REFERENCES locations(id),
    observed_at TIMESTAMP NOT NULL,
    rainfall_mm REAL,
    temperature_c REAL,
    humidity_pct REAL,
    soil_saturation_pct REAL,
    drainage_index REAL,
    water_storage_pct REAL,
    source TEXT DEFAULT 'synthetic_v1',       -- provenance: which DataProvider produced this row
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,                     -- flood | water | agriculture | ...
    version_label TEXT NOT NULL,              -- e.g. flood_v1_logistic_regression
    algorithm TEXT NOT NULL,
    metrics_json TEXT NOT NULL,               -- serialized metrics blob
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    UNIQUE(module, version_label)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    location_id INTEGER REFERENCES locations(id),
    module TEXT NOT NULL,
    model_version_id INTEGER REFERENCES model_versions(id),
    input_features_json TEXT NOT NULL,
    raw_output REAL NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER NOT NULL REFERENCES predictions(id),
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,                 -- LOW | MODERATE | HIGH | CRITICAL
    confidence REAL NOT NULL,
    key_factors_json TEXT NOT NULL,
    estimated_impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_assessment_id INTEGER NOT NULL REFERENCES risk_assessments(id),
    problem TEXT NOT NULL,
    reason TEXT NOT NULL,
    action TEXT NOT NULL,
    expected_benefit TEXT NOT NULL,
    driven_by_factor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_module ON predictions(module);
CREATE INDEX IF NOT EXISTS idx_predictions_location ON predictions(location_id);
CREATE INDEX IF NOT EXISTS idx_obs_location_time ON environmental_observations(location_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_prediction ON risk_assessments(prediction_id);
