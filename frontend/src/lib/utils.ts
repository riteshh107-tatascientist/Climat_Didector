import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export const RISK_LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"] as const;
export type RiskLevel = (typeof RISK_LEVELS)[number];

export const riskColor: Record<RiskLevel, string> = {
  LOW: "#2f9e5c",
  MODERATE: "#d99a1f",
  HIGH: "#e2711d",
  CRITICAL: "#d1352b",
};

export const riskTextClass: Record<RiskLevel, string> = {
  LOW: "text-risk-low",
  MODERATE: "text-risk-moderate",
  HIGH: "text-risk-high",
  CRITICAL: "text-risk-critical",
};

export const riskBgClass: Record<RiskLevel, string> = {
  LOW: "bg-risk-low/10",
  MODERATE: "bg-risk-moderate/10",
  HIGH: "bg-risk-high/10",
  CRITICAL: "bg-risk-critical/10",
};
