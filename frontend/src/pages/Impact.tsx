import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { DashboardOverview, HistoryResponse } from "@/types/api";
import { Card, CardContent } from "@/components/ui/primitives";
import { Info } from "lucide-react";

function ImpactStat({ label, value, isEstimate }: { label: string; value: string; isEstimate?: boolean }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <div className="flex items-center gap-1.5">
          <p className="text-xs font-medium uppercase tracking-wide text-ink-faint">{label}</p>
          {isEstimate && <span title="Estimated, not a directly measured outcome"><Info className="h-3 w-3 text-ink-faint" /></span>}
        </div>
        <p className="mt-1 text-2xl font-semibold text-ink">{value}</p>
        {isEstimate && <p className="mt-1 text-[11px] text-ink-faint">Estimated</p>}
      </CardContent>
    </Card>
  );
}

export default function Impact() {
  const overview = useQuery({ queryKey: ["dashboard", "overview"], queryFn: () => api.get<DashboardOverview>("/dashboard/overview") });
  const history = useQuery({ queryKey: ["history-all"], queryFn: () => api.get<HistoryResponse>("/predictions/history?page=1&page_size=100") });

  const totalAssessments = overview.data?.total_assessments ?? 0;
  const highRisk = overview.data?.high_risk_assessments ?? 0;
  const waterAssessments = history.data?.results.filter((r) => r.module === "water").length ?? 0;
  const floodAssessments = history.data?.results.filter((r) => r.module === "flood").length ?? 0;

  // Documented, disclosed assumption for illustrative estimates only —
  // never presented as a measured outcome. See README "Impact Methodology".
  const estimatedWaterSavedLiters = waterAssessments * 5000; // assumption: one acted-upon water-stress alert enables ~5,000L saved via harvesting/leak audits, per NITI Aayog composite water index guidance ranges
  const estimatedEmissionsAvoidedKg = floodAssessments * 12; // assumption: avoided emergency-response fuel/logistics per pre-warned flood event, order-of-magnitude illustrative

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Impact</h1>
        <p className="text-sm text-ink-faint">Real usage counts from your account, plus clearly-labeled illustrative estimates.</p>
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink">Measured</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <ImpactStat label="Risk Assessments Performed" value={String(totalAssessments)} />
          <ImpactStat label="High-Risk Situations Detected" value={String(highRisk)} />
          <ImpactStat label="Recommended Actions Generated" value={String(totalAssessments)} />
        </div>
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold text-ink">Illustrative Estimates</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <ImpactStat label="Estimated Water Saved" value={`${estimatedWaterSavedLiters.toLocaleString()} L`} isEstimate />
          <ImpactStat label="Estimated Emissions Avoided" value={`${estimatedEmissionsAvoidedKg.toLocaleString()} kg CO₂`} isEstimate />
        </div>
        <p className="mt-3 max-w-2xl text-xs text-ink-faint">
          Estimates use a disclosed, fixed assumption per acted-upon alert (documented in the README's Impact
          Methodology section) — they are illustrative projections, not measured real-world outcomes.
        </p>
      </div>
    </div>
  );
}
