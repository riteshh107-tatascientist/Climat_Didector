import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, PieChart, Pie, Legend,
} from "recharts";
import { riskColor, formatDate, type RiskLevel } from "@/lib/utils";

export function EnvironmentalTrendChart({
  data,
}: {
  data: { observed_at: string; rainfall_mm: number; temperature_c: number }[];
}) {
  const chartData = data.map((d) => ({
    date: formatDate(d.observed_at),
    Rainfall: d.rainfall_mm,
    Temperature: d.temperature_c,
  }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eef1ef" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#7c8b83" }} />
        <YAxis tick={{ fontSize: 11, fill: "#7c8b83" }} />
        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #eef1ef" }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="monotone" dataKey="Rainfall" stroke="#1e7f82" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Temperature" stroke="#e2711d" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function RiskTrendChart({ data }: { data: { predicted_at: string; risk_score: number }[] }) {
  const chartData = [...data].reverse().map((d) => ({
    date: formatDate(d.predicted_at),
    "Risk score": d.risk_score,
  }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={chartData} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eef1ef" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#7c8b83" }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#7c8b83" }} />
        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #eef1ef" }} />
        <Line type="monotone" dataKey="Risk score" stroke="#277355" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function RiskDistributionChart({ distribution }: { distribution: Record<RiskLevel, number> }) {
  const data = (Object.entries(distribution) as [RiskLevel, number][]).map(([level, count]) => ({
    name: level, value: count,
  }));
  const allZero = data.every((d) => d.value === 0);
  if (allZero) {
    return <p className="text-sm text-ink-faint">No assessments yet.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={riskColor[entry.name]} />
          ))}
        </Pie>
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #eef1ef" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function TopFactorsChart({ factors }: { factors: { factor: string; occurrences: number }[] }) {
  if (factors.length === 0) {
    return <p className="text-sm text-ink-faint">Not enough data yet to identify recurring factors.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(160, factors.length * 36)}>
      <BarChart data={factors} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
        <XAxis type="number" tick={{ fontSize: 11, fill: "#7c8b83" }} />
        <YAxis type="category" dataKey="factor" width={140} tick={{ fontSize: 11, fill: "#4b5a53" }} />
        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #eef1ef" }} />
        <Bar dataKey="occurrences" fill="#e2711d" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
