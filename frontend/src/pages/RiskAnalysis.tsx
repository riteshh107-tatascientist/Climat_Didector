import { RiskAnalysisForm } from "@/components/risk/RiskAnalysisForm";

export default function RiskAnalysis() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Risk Analysis</h1>
        <p className="text-sm text-ink-faint">
          Enter environmental parameters for a location to get a real-time, explainable risk score.
        </p>
      </div>
      <RiskAnalysisForm />
    </div>
  );
}
