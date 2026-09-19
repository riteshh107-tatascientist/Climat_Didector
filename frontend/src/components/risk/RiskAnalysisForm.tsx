import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import type { RiskResponse, Module } from "@/types/api";
import { Button, Card, CardContent, CardHeader, CardTitle, Select, Input, Badge, riskBadgeVariant, ErrorState } from "@/components/ui/primitives";
import { FactorContributionChart, RecommendationCard, RiskScoreDial } from "@/components/risk/RiskComponents";

const MODULE_LABELS: Record<Module, string> = {
  flood: "Flood Risk",
  water: "Water Stress",
  agriculture: "Agriculture Stress",
};

interface FormState {
  module: Module;
  region: string;
  rainfall_mm: string;
  temperature_c: string;
  humidity_pct: string;
  soil_saturation_pct: string;
  drainage_index: string;
  elevation_m: string;
  pop_density_per_km2: string;
  water_storage_pct: string;
  flood_prone_base: string;
  drought_prone_base: string;
  month: string;
  is_monsoon: string;
}

const DEFAULTS: FormState = {
  module: "flood",
  region: "Mumbai",
  rainfall_mm: "180", temperature_c: "28", humidity_pct: "88",
  soil_saturation_pct: "85", drainage_index: "35", elevation_m: "12",
  pop_density_per_km2: "9000", water_storage_pct: "45",
  flood_prone_base: "1", drought_prone_base: "0", month: "7", is_monsoon: "1",
};

export function RiskAnalysisForm({ demoMode = false }: { demoMode?: boolean }) {
  const [form, setForm] = useState<FormState>(DEFAULTS);

  const mutation = useMutation<RiskResponse, ApiError, void>({
    mutationFn: async () => {
      const base = {
        region: form.region,
        rainfall_mm: Number(form.rainfall_mm),
        temperature_c: Number(form.temperature_c),
        humidity_pct: Number(form.humidity_pct),
        month: Number(form.month),
        is_monsoon: Number(form.is_monsoon) as 0 | 1,
      };
      if (form.module === "flood") {
        return api.post<RiskResponse>("/flood/predict", {
          ...base,
          soil_saturation_pct: Number(form.soil_saturation_pct),
          drainage_index: Number(form.drainage_index),
          elevation_m: Number(form.elevation_m),
          pop_density_per_km2: Number(form.pop_density_per_km2),
          flood_prone_base: Number(form.flood_prone_base) as 0 | 1,
        });
      }
      if (form.module === "water") {
        return api.post<RiskResponse>("/water/predict", {
          ...base,
          water_storage_pct: Number(form.water_storage_pct),
          pop_density_per_km2: Number(form.pop_density_per_km2),
          drought_prone_base: Number(form.drought_prone_base) as 0 | 1,
        });
      }
      return api.post<RiskResponse>("/agriculture/predict", {
        ...base,
        soil_saturation_pct: Number(form.soil_saturation_pct),
        drought_prone_base: Number(form.drought_prone_base) as 0 | 1,
      });
    },
  });

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Environmental Inputs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {demoMode && (
            <Badge variant="brand">Demo mode — sample inputs, real model</Badge>
          )}
          <Select label="Module" value={form.module} onChange={(e) => update("module", e.target.value as Module)}>
            <option value="flood">Flood Risk</option>
            <option value="water">Water Stress</option>
            <option value="agriculture">Agriculture Stress</option>
          </Select>
          <Input label="Region" value={form.region} onChange={(e) => update("region", e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Rainfall (mm)" type="number" value={form.rainfall_mm} onChange={(e) => update("rainfall_mm", e.target.value)} />
            <Input label="Temperature (°C)" type="number" value={form.temperature_c} onChange={(e) => update("temperature_c", e.target.value)} />
            <Input label="Humidity (%)" type="number" value={form.humidity_pct} onChange={(e) => update("humidity_pct", e.target.value)} />
            <Input label="Month (1-12)" type="number" min={1} max={12} value={form.month} onChange={(e) => update("month", e.target.value)} />
          </div>

          {(form.module === "flood" || form.module === "agriculture") && (
            <div className="grid grid-cols-2 gap-3">
              <Input label="Soil saturation (%)" type="number" value={form.soil_saturation_pct} onChange={(e) => update("soil_saturation_pct", e.target.value)} />
              {form.module === "flood" && (
                <>
                  <Input label="Drainage index (0-100)" type="number" value={form.drainage_index} onChange={(e) => update("drainage_index", e.target.value)} />
                  <Input label="Elevation (m)" type="number" value={form.elevation_m} onChange={(e) => update("elevation_m", e.target.value)} />
                  <Input label="Pop. density (/km²)" type="number" value={form.pop_density_per_km2} onChange={(e) => update("pop_density_per_km2", e.target.value)} />
                </>
              )}
            </div>
          )}

          {form.module === "water" && (
            <div className="grid grid-cols-2 gap-3">
              <Input label="Water storage (%)" type="number" value={form.water_storage_pct} onChange={(e) => update("water_storage_pct", e.target.value)} />
              <Input label="Pop. density (/km²)" type="number" value={form.pop_density_per_km2} onChange={(e) => update("pop_density_per_km2", e.target.value)} />
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            {form.module === "flood" && (
              <Select label="Known flood-prone area?" value={form.flood_prone_base} onChange={(e) => update("flood_prone_base", e.target.value)}>
                <option value="0">No</option>
                <option value="1">Yes</option>
              </Select>
            )}
            {(form.module === "water" || form.module === "agriculture") && (
              <Select label="Known drought-prone area?" value={form.drought_prone_base} onChange={(e) => update("drought_prone_base", e.target.value)}>
                <option value="0">No</option>
                <option value="1">Yes</option>
              </Select>
            )}
            <Select label="Monsoon season?" value={form.is_monsoon} onChange={(e) => update("is_monsoon", e.target.value)}>
              <option value="0">No</option>
              <option value="1">Yes</option>
            </Select>
          </div>

          <Button className="w-full" onClick={() => mutation.mutate()} isLoading={mutation.isPending}>
            Analyze Risk
          </Button>
        </CardContent>
      </Card>

      <div className="space-y-6">
        {mutation.isError && (
          <ErrorState
            message={mutation.error instanceof ApiError ? String(mutation.error.detail) : "Analysis failed."}
            onRetry={() => mutation.mutate()}
          />
        )}

        {!mutation.data && !mutation.isError && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center gap-2 py-16 text-center">
              <p className="text-sm font-medium text-ink">No analysis yet</p>
              <p className="max-w-xs text-sm text-ink-faint">
                Fill in the environmental inputs and run an analysis to see the risk score, explanation, and recommendations.
              </p>
            </CardContent>
          </Card>
        )}

        {mutation.data && (
          <>
            <Card>
              <CardContent className="flex flex-col items-center gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-6">
                  <RiskScoreDial score={mutation.data.risk_score} level={mutation.data.risk_level} />
                  <div className="space-y-1.5">
                    <Badge variant={riskBadgeVariant(mutation.data.risk_level)}>
                      {MODULE_LABELS[mutation.data.module]}
                    </Badge>
                    <p className="text-sm text-ink-muted">
                      Confidence: <span className="font-medium text-ink">{mutation.data.confidence.toFixed(0)}%</span>
                    </p>
                    <p className="text-xs text-ink-faint">Model: {mutation.data.model_version}</p>
                    {mutation.data.estimated_impact && (
                      <p className="text-sm text-ink-muted">{mutation.data.estimated_impact}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Why this score?</CardTitle></CardHeader>
              <CardContent>
                <FactorContributionChart factors={mutation.data.key_factors} />
              </CardContent>
            </Card>

            <div>
              <h3 className="mb-3 text-sm font-semibold text-ink">Recommended Actions</h3>
              <div className="space-y-3">
                {mutation.data.recommendations.map((rec, i) => (
                  <RecommendationCard key={i} rec={rec} />
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
