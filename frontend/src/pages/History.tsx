import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";
import type { HistoryResponse, PredictionDetail } from "@/types/api";
import { Card, CardContent, Select, Badge, riskBadgeVariant, Skeleton, EmptyState, Button } from "@/components/ui/primitives";
import { FactorContributionChart, RecommendationCard } from "@/components/risk/RiskComponents";
import { formatDateTime } from "@/lib/utils";
import { X } from "lucide-react";

export default function History() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [module, setModule] = useState("");
  const [page, setPage] = useState(1);
  const openId = searchParams.get("open");

  const history = useQuery({
    queryKey: ["history", module, page],
    queryFn: () =>
      api.get<HistoryResponse>(
        `/predictions/history?page=${page}&page_size=10${module ? `&module=${module}` : ""}`
      ),
  });

  const detail = useQuery({
    queryKey: ["prediction-detail", openId],
    queryFn: () => api.get<PredictionDetail>(`/predictions/${openId}`),
    enabled: !!openId,
  });

  const totalPages = history.data ? Math.ceil(history.data.total / history.data.page_size) : 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-xl font-semibold text-ink">History</h1>
          <p className="text-sm text-ink-faint">Every past risk assessment, fully traceable back to its inputs and model version.</p>
        </div>
        <Select value={module} onChange={(e) => { setModule(e.target.value); setPage(1); }} className="w-44">
          <option value="">All modules</option>
          <option value="flood">Flood</option>
          <option value="water">Water</option>
          <option value="agriculture">Agriculture</option>
        </Select>
      </div>

      <Card>
        <CardContent className="pt-4">
          {history.isLoading ? (
            <div className="space-y-2"><Skeleton className="h-12" /><Skeleton className="h-12" /><Skeleton className="h-12" /></div>
          ) : history.data && history.data.results.length > 0 ? (
            <>
              {/* Desktop table */}
              <div className="hidden overflow-x-auto md:block">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-ink/8 text-left text-xs uppercase tracking-wide text-ink-faint">
                      <th className="py-2 pr-4">Date</th>
                      <th className="py-2 pr-4">Location</th>
                      <th className="py-2 pr-4">Module</th>
                      <th className="py-2 pr-4">Score</th>
                      <th className="py-2 pr-4">Level</th>
                      <th className="py-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.data.results.map((r) => (
                      <tr key={r.prediction_id} className="border-b border-ink/5">
                        <td className="py-2.5 pr-4 text-ink-muted">{formatDateTime(r.predicted_at)}</td>
                        <td className="py-2.5 pr-4 text-ink">{r.region}, {r.state}</td>
                        <td className="py-2.5 pr-4 capitalize text-ink-muted">{r.module}</td>
                        <td className="py-2.5 pr-4 font-medium tabular-nums text-ink">{r.risk_score.toFixed(0)}</td>
                        <td className="py-2.5 pr-4"><Badge variant={riskBadgeVariant(r.risk_level)}>{r.risk_level}</Badge></td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => setSearchParams({ open: String(r.prediction_id) })}
                            className="text-xs font-medium text-brand-700 hover:underline"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Mobile cards */}
              <div className="space-y-2 md:hidden">
                {history.data.results.map((r) => (
                  <button
                    key={r.prediction_id}
                    onClick={() => setSearchParams({ open: String(r.prediction_id) })}
                    className="flex w-full items-center justify-between rounded-lg border border-ink/8 px-3 py-3 text-left"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-ink">{r.region}, {r.state}</p>
                      <p className="text-xs text-ink-faint">{r.module} · {formatDateTime(r.predicted_at)}</p>
                    </div>
                    <Badge variant={riskBadgeVariant(r.risk_level)}>{r.risk_level}</Badge>
                  </button>
                ))}
              </div>

              <div className="mt-4 flex items-center justify-between text-sm">
                <span className="text-ink-faint">
                  Page {history.data.page} of {totalPages || 1} · {history.data.total} total
                </span>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</Button>
                  <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</Button>
                </div>
              </div>
            </>
          ) : (
            <EmptyState title="No history yet" description="Assessments you run will appear here." />
          )}
        </CardContent>
      </Card>

      {openId && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center" onClick={() => setSearchParams({})}>
          <div
            className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-t-2xl bg-surface p-6 sm:rounded-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-ink">Assessment Detail</h2>
              <button onClick={() => setSearchParams({})} aria-label="Close" className="rounded-md p-1.5 hover:bg-surface-muted">
                <X className="h-4 w-4" />
              </button>
            </div>
            {detail.isLoading && <Skeleton className="h-64" />}
            {detail.data && (
              <div className="space-y-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-ink">{detail.data.region}, {detail.data.state}</p>
                    <p className="text-xs text-ink-faint">{formatDateTime(detail.data.predicted_at)}</p>
                  </div>
                  <Badge variant={riskBadgeVariant(detail.data.risk_level)}>
                    {detail.data.risk_level} · {detail.data.risk_score.toFixed(0)}
                  </Badge>
                </div>
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-ink">Contributing Factors</h3>
                  <FactorContributionChart factors={detail.data.key_factors} />
                </div>
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-ink">Recommendations</h3>
                  <div className="space-y-3">
                    {detail.data.recommendations.map((rec, i) => <RecommendationCard key={i} rec={rec} />)}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
