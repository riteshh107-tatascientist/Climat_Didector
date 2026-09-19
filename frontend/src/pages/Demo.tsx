import { Link } from "react-router-dom";
import { RiskAnalysisForm } from "@/components/risk/RiskAnalysisForm";
import { Button } from "@/components/ui/primitives";

export default function Demo() {
  return (
    <div className="min-h-screen bg-surface-subtle">
      <header className="border-b border-ink/8 bg-surface px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">CG</div>
            <span className="text-[15px] font-semibold text-ink">ClimateGuard</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link to="/login"><Button variant="ghost" size="sm">Log in</Button></Link>
            <Link to="/signup"><Button size="sm">Sign up</Button></Link>
          </div>
        </div>
      </header>
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="mb-6 rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 text-sm text-brand-800">
          <span className="font-semibold">Live demo</span> — this runs the same trained ML models and risk
          engine as the full product. Predictions here aren't saved to an account.{" "}
          <Link to="/signup" className="font-medium underline">Sign up</Link> to build a saved history.
        </div>
        <h1 className="mb-1 text-xl font-semibold text-ink">Try ClimateGuard AI</h1>
        <p className="mb-6 text-sm text-ink-faint">
          Adjust the environmental inputs below (defaults reflect real monsoon-season Mumbai conditions) and run an analysis.
        </p>
        <RiskAnalysisForm demoMode />
      </div>
    </div>
  );
}
