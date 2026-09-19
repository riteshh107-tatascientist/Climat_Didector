import { useState } from "react";
import { useQuery, useQueries, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { RecentAssessment, PredictionDetail } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle, Badge, riskBadgeVariant, Skeleton, EmptyState, Input, Button } from "@/components/ui/primitives";
import { RecommendationCard } from "@/components/risk/RiskComponents";

interface RuleRecommendation {
  problem: string; reason: string; action: string; expected_benefit: string; driven_by_factor: string | null;
}

function WasteTool() {
  const [organic, setOrganic] = useState("55");
  const [recyclable, setRecyclable] = useState("20");
  const [efficiency, setEfficiency] = useState("60");
  const mutation = useMutation({
    mutationFn: () =>
      api.post<{ recommendations: RuleRecommendation[] }>("/waste/recommend", {
        region: "Custom", organic_pct: Number(organic), recyclable_pct: Number(recyclable),
        collection_efficiency_pct: Number(efficiency),
      }),
  });
  return (
    <Card>
      <CardHeader><CardTitle>Waste & Circular Economy</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-2">
          <Input label="Organic %" type="number" value={organic} onChange={(e) => setOrganic(e.target.value)} />
          <Input label="Recyclable %" type="number" value={recyclable} onChange={(e) => setRecyclable(e.target.value)} />
          <Input label="Collection eff. %" type="number" value={efficiency} onChange={(e) => setEfficiency(e.target.value)} />
        </div>
        <Button size="sm" onClick={() => mutation.mutate()} isLoading={mutation.isPending}>Get recommendations</Button>
        {mutation.data && (
          <div className="space-y-2 pt-2">
            {mutation.data.recommendations.map((r, i) => <RecommendationCard key={i} rec={r} />)}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function EnergyTool() {
  const [demand, setDemand] = useState("100");
  const [emissions, setEmissions] = useState("70");
  const [temp, setTemp] = useState("33");
  const mutation = useMutation({
    mutationFn: () =>
      api.post<{ recommendations: RuleRecommendation[] }>("/energy/recommend", {
        region: "Custom", energy_demand_mwh: Number(demand), carbon_emissions_tco2: Number(emissions),
        avg_temp_c: Number(temp),
      }),
  });
  return (
    <Card>
      <CardHeader><CardTitle>Energy & Carbon</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-2">
          <Input label="Demand (MWh)" type="number" value={demand} onChange={(e) => setDemand(e.target.value)} />
          <Input label="Emissions (tCO2)" type="number" value={emissions} onChange={(e) => setEmissions(e.target.value)} />
          <Input label="Avg temp (°C)" type="number" value={temp} onChange={(e) => setTemp(e.target.value)} />
        </div>
        <Button size="sm" onClick={() => mutation.mutate()} isLoading={mutation.isPending}>Get recommendations</Button>
        {mutation.data && (
          <div className="space-y-2 pt-2">
            {mutation.data.recommendations.map((r, i) => <RecommendationCard key={i} rec={r} />)}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Recommendations() {
  const recent = useQuery({
    queryKey: ["dashboard", "recent-for-recs"],
    queryFn: () => api.get<RecentAssessment[]>("/dashboard/recent?limit=5"),
  });

  const detailQueries = useQueries({
    queries: (recent.data ?? []).map((a) => ({
      queryKey: ["prediction-detail", a.prediction_id],
      queryFn: () => api.get<PredictionDetail>(`/predictions/${a.prediction_id}`),
      enabled: !!recent.data,
    })),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-ink">Recommendations</h1>
        <p className="text-sm text-ink-faint">Actions generated from your most recent assessments, plus standalone tools.</p>
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink">From your recent assessments</h2>
        {recent.isLoading ? (
          <div className="space-y-2"><Skeleton className="h-20" /><Skeleton className="h-20" /></div>
        ) : recent.data && recent.data.length > 0 ? (
          <div className="space-y-6">
            {recent.data.map((a, idx) => {
              const detail = detailQueries[idx];
              return (
                <div key={a.prediction_id}>
                  <div className="mb-2 flex items-center gap-2">
                    <p className="text-sm font-medium text-ink">{a.region}, {a.state}</p>
                    <Badge variant={riskBadgeVariant(a.risk_level)}>{a.risk_level}</Badge>
                    <span className="text-xs capitalize text-ink-faint">{a.module}</span>
                  </div>
                  {detail?.isLoading ? (
                    <Skeleton className="h-16" />
                  ) : (
                    <div className="space-y-2">
                      {detail?.data?.recommendations.map((rec, i) => <RecommendationCard key={i} rec={rec} />)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState title="No recommendations yet" description="Run a risk analysis first." />
        )}
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink">Quick tools (rules-based)</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          <WasteTool />
          <EnergyTool />
        </div>
      </div>
    </div>
  );
}
