import type { KeyFactor, Recommendation } from "@/types/api";
import { Card, CardContent } from "@/components/ui/primitives";
import { ArrowUpRight, ArrowDownRight, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

/** Horizontal contribution bars, e.g.
 *  Heavy rainfall      +24
 *  Poor drainage        +18
 * Bar length is proportional to |contribution| within this factor set. */
export function FactorContributionChart({ factors }: { factors: KeyFactor[] }) {
  if (factors.length === 0) {
    return <p className="text-sm text-ink-faint">No dominant factors were identified for this prediction.</p>;
  }
  const max = Math.max(...factors.map((f) => Math.abs(f.contribution)), 0.0001);

  return (
    <div className="space-y-3">
      {factors.map((f) => {
        const pct = Math.max(4, (Math.abs(f.contribution) / max) * 100);
        const increases = f.direction === "increases_risk";
        return (
          <div key={f.feature} className="flex items-center gap-3">
            <div className="w-36 shrink-0 truncate text-sm text-ink-muted" title={f.human_label}>
              {f.human_label}
            </div>
            <div className="relative h-6 flex-1 overflow-hidden rounded-md bg-surface-muted">
              <div
                className={cn(
                  "h-full rounded-md transition-all",
                  increases ? "bg-risk-high" : "bg-risk-low"
                )}
                style={{ width: `${pct}%` }}
              />
            </div>
            <div className={cn(
              "flex w-16 shrink-0 items-center justify-end gap-1 text-sm font-semibold tabular-nums",
              increases ? "text-risk-high" : "text-risk-low"
            )}>
              {increases ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
              {Math.abs(f.contribution).toFixed(2)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-700">
            <Lightbulb className="h-4 w-4" />
          </div>
          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-sm font-semibold text-ink">{rec.problem}</p>
            <p className="text-sm text-ink-muted">{rec.reason}</p>
            <div className="rounded-lg bg-surface-subtle p-3">
              <p className="text-xs font-medium uppercase tracking-wide text-ink-faint">Recommended action</p>
              <p className="mt-1 text-sm text-ink">{rec.action}</p>
            </div>
            <p className="text-xs text-brand-700">
              <span className="font-medium">Expected benefit:</span> {rec.expected_benefit}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function RiskScoreDial({ score, level }: { score: number; level: string }) {
  const color = {
    LOW: "#2f9e5c", MODERATE: "#d99a1f", HIGH: "#e2711d", CRITICAL: "#d1352b",
  }[level] ?? "#4b5a53";
  const circumference = 2 * Math.PI * 54;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative flex h-40 w-40 items-center justify-center">
      <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
        <circle cx="60" cy="60" r="54" fill="none" stroke="#eef1ef" strokeWidth="10" />
        <circle
          cx="60" cy="60" r="54" fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-ink">{score.toFixed(0)}</span>
        <span className="text-xs font-medium uppercase tracking-wide" style={{ color }}>
          {level}
        </span>
      </div>
    </div>
  );
}
