import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import type { LocationSummary, KeyFactor } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle, Input, Badge, riskBadgeVariant, EmptyState, Skeleton } from "@/components/ui/primitives";
import { FactorContributionChart } from "@/components/risk/RiskComponents";
import { Search, MapPin } from "lucide-react";

interface LocationIntelligence {
  region: string;
  state: string;
  flood_prone: boolean;
  drought_prone: boolean;
  modules: Record<string, {
    risk_score: number; risk_level: string; confidence: number;
    key_factors: KeyFactor[]; predicted_at: string;
  }>;
}

export default function Locations() {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>(null);

  const list = useQuery({
    queryKey: ["locations", query],
    queryFn: () => api.get<LocationSummary[]>(`/locations${query ? `?q=${encodeURIComponent(query)}` : ""}`),
  });

  const intelligence = useQuery({
    queryKey: ["location-intelligence", selected],
    queryFn: () => api.get<LocationIntelligence>(`/locations/${encodeURIComponent(selected!)}/intelligence`),
    enabled: !!selected,
    retry: false,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Locations</h1>
        <p className="text-sm text-ink-faint">Search a region to see its latest risk snapshot across all modules.</p>
      </div>

      <div className="relative max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
        <Input
          placeholder="Search region or state (e.g. Mumbai, Kerala)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <Card>
          <CardContent className="max-h-[480px] space-y-1 overflow-y-auto pt-4">
            {list.isLoading ? (
              <><Skeleton className="h-9" /><Skeleton className="h-9" /></>
            ) : list.data && list.data.length > 0 ? (
              list.data.map((loc) => (
                <button
                  key={loc.id}
                  onClick={() => setSelected(loc.region)}
                  className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-subtle ${
                    selected === loc.region ? "bg-brand-50 text-brand-800" : "text-ink"
                  }`}
                >
                  <MapPin className="h-3.5 w-3.5 shrink-0" />
                  <span className="min-w-0 flex-1 truncate">{loc.region}, {loc.state}</span>
                </button>
              ))
            ) : (
              <p className="px-1 py-4 text-sm text-ink-faint">
                No locations recorded yet — run a prediction for a region to add it here.
              </p>
            )}
          </CardContent>
        </Card>

        <div>
          {!selected && (
            <EmptyState title="Select a location" description="Choose a region from the list to see its risk snapshot." />
          )}
          {selected && intelligence.isLoading && <Skeleton className="h-64" />}
          {selected && intelligence.isError && (
            <EmptyState
              title="No data for this location yet"
              description={intelligence.error instanceof ApiError ? String(intelligence.error.detail) : undefined}
            />
          )}
          {selected && intelligence.data && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-ink">{intelligence.data.region}, {intelligence.data.state}</h2>
                {intelligence.data.flood_prone && <Badge variant="high">Flood-prone</Badge>}
                {intelligence.data.drought_prone && <Badge variant="moderate">Drought-prone</Badge>}
              </div>
              {Object.keys(intelligence.data.modules).length === 0 ? (
                <EmptyState title="No assessments for this location yet" />
              ) : (
                Object.entries(intelligence.data.modules).map(([module, snap]) => (
                  <Card key={module}>
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle className="capitalize">{module} risk</CardTitle>
                      <Badge variant={riskBadgeVariant(snap.risk_level)}>{snap.risk_level} · {snap.risk_score.toFixed(0)}</Badge>
                    </CardHeader>
                    <CardContent>
                      <FactorContributionChart factors={snap.key_factors} />
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
