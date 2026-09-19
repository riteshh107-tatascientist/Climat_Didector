import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import type { DashboardOverview, RecentAssessment } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle, Skeleton, Badge, riskBadgeVariant, EmptyState, Button } from "@/components/ui/primitives";
import { RiskDistributionChart, TopFactorsChart } from "@/components/charts/Charts";
import { formatDateTime, type RiskLevel } from "@/lib/utils";

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-faint">{label}</p>
        <p className="mt-1 text-2xl font-semibold text-ink">{value}</p>
        {hint && <p className="mt-1 text-xs text-ink-faint">{hint}</p>}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const overview = useQuery({ queryKey: ["dashboard", "overview"], queryFn: () => api.get<DashboardOverview>("/dashboard/overview") });
  const distribution = useQuery({
    queryKey: ["dashboard", "risk-distribution"],
    queryFn: () => api.get<Record<string, number>>("/dashboard/risk-distribution"),
  });
  const recent = useQuery({
    queryKey: ["dashboard", "recent"],
    queryFn: () => api.get<RecentAssessment[]>("/dashboard/recent?limit=6"),
  });
  const topFactors = useQuery({
    queryKey: ["dashboard", "top-factors"],
    queryFn: () => api.get<{ factor: string; occurrences: number }[]>("/dashboard/top-risk-factors"),
  });

  const noData = overview.data?.total_assessments === 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Overview</h1>
        <p className="text-sm text-ink-faint">What's happening across your climate risk assessments.</p>
      </div>

      {noData && (
        <EmptyState
          title="No assessments yet"
          description="Run your first risk analysis to start populating your dashboard with real data."
          action={<Link to="/app/risk-analysis"><Button size="sm">Run a Risk Analysis</Button></Link>}
        />
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        {overview.isLoading ? (
          <>
            <Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" />
          </>
        ) : (
          <>
            <StatCard label="Total Assessments" value={String(overview.data?.total_assessments ?? 0)} />
            <StatCard
              label="High-Risk Assessments"
              value={String(overview.data?.high_risk_assessments ?? 0)}
              hint="HIGH or CRITICAL level"
            />
            <StatCard
              label="Average Risk Score"
              value={overview.data?.average_risk_score != null ? overview.data.average_risk_score.toFixed(1) : "—"}
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Risk Distribution</CardTitle></CardHeader>
          <CardContent>
            {distribution.isLoading ? <Skeleton className="h-52" /> : <RiskDistributionChart distribution={(distribution.data ?? {}) as Record<RiskLevel, number>} />}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top Contributing Factors</CardTitle></CardHeader>
          <CardContent>
            {topFactors.isLoading ? <Skeleton className="h-40" /> : <TopFactorsChart factors={topFactors.data ?? []} />}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Assessments</CardTitle>
          <Link to="/app/history" className="text-xs font-medium text-brand-700 hover:underline">View all</Link>
        </CardHeader>
        <CardContent>
          {recent.isLoading ? (
            <div className="space-y-2"><Skeleton className="h-10" /><Skeleton className="h-10" /></div>
          ) : recent.data && recent.data.length > 0 ? (
            <div className="divide-y divide-ink/8">
              {recent.data.map((a) => (
                <Link
                  key={a.prediction_id}
                  to={`/app/history?open=${a.prediction_id}`}
                  className="flex items-center justify-between gap-3 py-3 hover:bg-surface-subtle"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-ink">{a.region}, {a.state}</p>
                    <p className="text-xs text-ink-faint">{a.module} · {formatDateTime(a.predicted_at)}</p>
                  </div>
                  <Badge variant={riskBadgeVariant(a.risk_level)}>{a.risk_level}</Badge>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink-faint">No assessments yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
