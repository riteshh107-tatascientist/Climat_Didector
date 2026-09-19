export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type Module = "flood" | "water" | "agriculture";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  organization: string | null;
  role: string;
}

export interface KeyFactor {
  feature: string;
  human_label: string;
  contribution: number;
  direction: "increases_risk" | "decreases_risk";
  value: number | null;
  method: string;
}

export interface Recommendation {
  problem: string;
  reason: string;
  action: string;
  expected_benefit: string;
  driven_by_factor: string | null;
}

export interface RiskResponse {
  module: Module;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  key_factors: KeyFactor[];
  raw_model_output: number;
  model_version: string;
  estimated_impact: string | null;
  recommendations: Recommendation[];
}

export interface FloodRiskInput {
  region: string;
  rainfall_mm: number;
  temperature_c: number;
  humidity_pct: number;
  soil_saturation_pct: number;
  drainage_index: number;
  elevation_m: number;
  pop_density_per_km2: number;
  flood_prone_base: 0 | 1;
  month: number;
  is_monsoon: 0 | 1;
}

export interface WaterRiskInput {
  region: string;
  rainfall_mm: number;
  temperature_c: number;
  humidity_pct: number;
  water_storage_pct: number;
  pop_density_per_km2: number;
  drought_prone_base: 0 | 1;
  month: number;
  is_monsoon: 0 | 1;
}

export interface AgricultureInput {
  region: string;
  rainfall_mm: number;
  temperature_c: number;
  humidity_pct: number;
  soil_saturation_pct: number;
  drought_prone_base: 0 | 1;
  month: number;
  is_monsoon: 0 | 1;
}

export interface DashboardOverview {
  total_assessments: number;
  high_risk_assessments: number;
  average_risk_score: number | null;
  modules_covered: Module[];
  note?: string;
}

export interface RecentAssessment {
  prediction_id: number;
  module: Module;
  region: string;
  state: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  predicted_at: string;
}

export interface HistoryResponse {
  total: number;
  page: number;
  page_size: number;
  results: RecentAssessment[];
}

export interface PredictionDetail {
  prediction_id: number;
  module: Module;
  region: string;
  state: string;
  input_features: Record<string, unknown>;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  key_factors: KeyFactor[];
  estimated_impact: string | null;
  recommendations: Recommendation[];
  predicted_at: string;
}

export interface LocationSummary {
  id: number;
  region: string;
  state: string;
  flood_prone: boolean;
  drought_prone: boolean;
}

export interface ModelInfo {
  module: Module;
  version: string;
  algorithm: string;
}
