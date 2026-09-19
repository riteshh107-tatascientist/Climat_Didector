import { Link } from "react-router-dom";
import { Button } from "@/components/ui/primitives";
import {
  CloudRain, Droplets, Sprout, ArrowRight, CheckCircle2, Database,
  Brain, ShieldCheck, LineChart,
} from "lucide-react";

const MODULES = [
  { icon: CloudRain, title: "Flood Risk", desc: "Rainfall, drainage, and soil-saturation signals combine into an explainable flood risk score." },
  { icon: Droplets, title: "Water Stress", desc: "Storage levels, rainfall deficits, and temperature trends flag emerging water stress early." },
  { icon: Sprout, title: "Agriculture Stress", desc: "Heat and water-deficit indicators estimate crop stress before yield impact shows up." },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Enter conditions", desc: "Location and environmental readings — rainfall, temperature, humidity, soil, and more." },
  { step: "02", title: "ML risk models", desc: "Trained scikit-learn models (Random Forest, Gradient Boosting, Logistic Regression) score the risk." },
  { step: "03", title: "Explainable output", desc: "Feature-contribution analysis shows exactly which factors are driving the score, and by how much." },
  { step: "04", title: "Act on it", desc: "Every score comes with specific, input-driven recommendations — not generic advice." },
];

function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-ink/8 bg-surface/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">CG</div>
          <span className="text-[15px] font-semibold text-ink">ClimateGuard</span>
        </div>
        <nav className="hidden items-center gap-6 text-sm text-ink-muted md:flex">
          <a href="#modules" className="hover:text-ink">Modules</a>
          <a href="#how-it-works" className="hover:text-ink">How it works</a>
          <a href="#technology" className="hover:text-ink">Technology</a>
        </nav>
        <div className="flex items-center gap-2">
          <Link to="/login"><Button variant="ghost" size="sm">Log in</Button></Link>
          <Link to="/signup"><Button size="sm">Sign up</Button></Link>
        </div>
      </div>
    </header>
  );
}

export default function Landing() {
  return (
    <div className="bg-surface">
      <Header />

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-800">
            Built for the SANKALP Climate Edition Student Track
          </span>
          <h1 className="mt-5 text-3xl font-bold leading-tight text-ink sm:text-5xl">
            Understand Climate Risk.<br />Act Before It Escalates.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-ink-muted sm:text-lg">
            ClimateGuard AI turns environmental data into explainable risk scores and actionable
            recommendations for flood, water, and agriculture risk across India — backed by real,
            trained machine learning models.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/demo">
              <Button size="lg">
                Explore Climate Intelligence <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="secondary" size="lg">See How It Works</Button>
            </a>
          </div>
        </div>

        {/* Product preview */}
        <div className="mx-auto mt-14 max-w-4xl rounded-2xl border border-ink/10 bg-surface-subtle p-2 shadow-card sm:p-4">
          <div className="rounded-xl border border-ink/8 bg-surface p-4 sm:p-6">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm font-semibold text-ink">Mumbai — Flood Risk</p>
              <span className="rounded-full bg-risk-high/10 px-2.5 py-1 text-xs font-medium text-risk-high">HIGH · 78</span>
            </div>
            <div className="space-y-2">
              {[
                { label: "Heavy rainfall", value: 82 },
                { label: "Poor drainage capacity", value: 61 },
                { label: "Soil saturation", value: 48 },
              ].map((f) => (
                <div key={f.label} className="flex items-center gap-3">
                  <span className="w-40 shrink-0 text-xs text-ink-muted">{f.label}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted">
                    <div className="h-full rounded-full bg-risk-high" style={{ width: `${f.value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Problem / Solution */}
      <section className="border-t border-ink/8 bg-surface-subtle py-16">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 sm:px-6 md:grid-cols-2">
          <div>
            <h2 className="text-lg font-semibold text-ink">The problem</h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-muted">
              Climate risk data in India is fragmented across meteorological, agricultural, and
              municipal sources. Communities and local decision-makers often learn about flood,
              water, or crop-stress risk only after it has already caused damage — not while there's
              still time to act.
            </p>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-ink">Our solution</h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-muted">
              A unified platform that converts environmental readings into a calibrated risk score,
              explains exactly which factors are driving it, and recommends a specific, actionable
              response — all through one shared risk engine across modules.
            </p>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-lg font-semibold text-ink">How it works</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {HOW_IT_WORKS.map((s) => (
            <div key={s.step}>
              <p className="text-2xl font-bold text-brand-200">{s.step}</p>
              <h3 className="mt-2 text-sm font-semibold text-ink">{s.title}</h3>
              <p className="mt-1 text-sm text-ink-faint">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Modules */}
      <section id="modules" className="border-t border-ink/8 bg-surface-subtle py-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <h2 className="text-lg font-semibold text-ink">Climate modules</h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {MODULES.map((m) => (
              <div key={m.title} className="rounded-xl border border-ink/8 bg-surface p-5">
                <m.icon className="h-6 w-6 text-brand-700" />
                <h3 className="mt-3 text-sm font-semibold text-ink">{m.title}</h3>
                <p className="mt-1 text-sm text-ink-faint">{m.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="technology" className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-lg font-semibold text-ink">Technology</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Database, title: "Real, documented data", desc: "Data pipeline anchored to public IMD/CPCB/CEA reference ranges." },
            { icon: Brain, title: "Genuine ML models", desc: "Random Forest, Gradient Boosting & Logistic Regression, evaluated head-to-head." },
            { icon: LineChart, title: "Explainable AI", desc: "Every score ships with ranked, signed factor contributions — not a black box." },
            { icon: ShieldCheck, title: "Production architecture", desc: "FastAPI, PostgreSQL, JWT auth — built to scale beyond a prototype." },
          ].map((t) => (
            <div key={t.title}>
              <t.icon className="h-5 w-5 text-brand-700" />
              <h3 className="mt-2 text-sm font-semibold text-ink">{t.title}</h3>
              <p className="mt-1 text-sm text-ink-faint">{t.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-ink/8 bg-brand-900 py-16 text-center">
        <h2 className="text-2xl font-semibold text-white">See it work on real conditions</h2>
        <p className="mx-auto mt-2 max-w-md text-sm text-brand-100">
          Try the live model with sample or your own environmental inputs — no account required.
        </p>
        <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link to="/demo">
            <Button size="lg" className="bg-white text-brand-900 hover:bg-brand-50">
              <CheckCircle2 className="h-4 w-4" /> Try the Live Demo
            </Button>
          </Link>
        </div>
      </section>

      <footer className="border-t border-ink/8 py-8 text-center text-xs text-ink-faint">
        ClimateGuard AI — built for the SANKALP by Satin Finserv Climate Edition Student Track.
      </footer>
    </div>
  );
}
