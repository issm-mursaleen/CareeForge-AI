"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "@/services/analytics";
import { roadmapService } from "@/services/roadmap";
import Link from "next/link";
import {
  Bar, BarChart, CartesianGrid, Cell,
  Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

const ML_METRIC_COLORS: Record<string, string> = {
  Accuracy: "#006b54",
  Precision: "#266956",
  Recall: "#aa324b",
  "F1-Score": "#00e0b2",
};

function formatRelative(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins || 1}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics-summary"],
    queryFn: () => analyticsService.summary(),
  });

  const { data: ml, isLoading: mlLoading, isError: mlError } = useQuery({
    queryKey: ["ml-performance"],
    queryFn: () => analyticsService.mlPerformance(),
    retry: false,
  });

  const { data: roadmaps } = useQuery({
    queryKey: ["roadmaps"],
    queryFn: () => roadmapService.list(),
    retry: false,
  });

  const score = Math.round(data?.average_ats ?? 0);
  const circumference = 2 * Math.PI * 88;
  const offset = circumference * (1 - score / 100);

  // Most recent roadmap's milestones (up to 3)
  const latestRoadmap = roadmaps && roadmaps.length > 0 ? roadmaps[roadmaps.length - 1] : null;
  const milestones = latestRoadmap?.milestones.slice(0, 3) ?? [];

  // Activity derived from ats_trend (most recent 3 resume events)
  const trendActivity = [...(data?.ats_trend ?? [])]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 3)
    .map((t) => ({
      color: "bg-secondary",
      title: "Resume scored",
      sub: `${formatRelative(t.date)} · ATS ${Math.round(t.score)}`,
    }));
  // If a roadmap exists, prepend a roadmap event
  const activityItems = latestRoadmap
    ? [
        { color: "bg-primary", title: "Career roadmap generated", sub: `Target: ${latestRoadmap.target_role}` },
        ...trendActivity,
      ].slice(0, 3)
    : trendActivity.length > 0
      ? trendActivity
      : [{ color: "bg-outline", title: "No activity yet", sub: "Upload a resume to get started" }];

  return (
    <div className="space-y-lg max-w-7xl mx-auto">
      {/* Header */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-md">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Welcome back.</h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Your career momentum dashboard.
          </p>
        </div>
        <div className="flex gap-sm">
          <div className="px-md py-xs bg-surface-container rounded-xl border border-outline-variant flex items-center gap-xs">
            <span
              className="material-symbols-outlined text-secondary"
              style={{ fontSize: 20, fontVariationSettings: "'FILL' 1" }}
            >
              trending_up
            </span>
            <span className="font-label-md text-label-md">
              {isLoading ? "…" : `${data?.total_resumes ?? 0} Resumes Analyzed`}
            </span>
          </div>
        </div>
      </section>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        {/* Resume Score Gauge */}
        <div className="md:col-span-4 bg-surface-container-lowest border border-outline-variant rounded-xl p-md flex flex-col items-center justify-center text-center shadow-sm">
          <p className="font-label-md text-label-md text-on-surface-variant mb-md self-start">Current Resume Score</p>
          <div className="relative w-48 h-48 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 192 192">
              <circle cx="96" cy="96" r="88" fill="transparent" stroke="#e6f0ea" strokeWidth="12" />
              <circle
                cx="96" cy="96" r="88" fill="transparent"
                stroke="#266956" strokeWidth="12"
                strokeDasharray={circumference}
                strokeDashoffset={isLoading ? circumference : offset}
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="font-display-lg text-display-lg text-on-surface">
                {isLoading ? "…" : score}
              </span>
              <span className="font-label-sm text-label-sm text-on-surface-variant">/ 100</span>
            </div>
          </div>
          <p className="mt-md font-body-md text-body-md text-on-surface-variant px-sm">
            {isLoading
              ? "Loading your resume score…"
              : score > 0
                ? `Outperforming ${Math.min(99, score - 1)}% of candidates.`
                : "Upload a resume to get your score."}
          </p>
          <Link href="/analyzer" className="mt-lg w-full">
            <button className="w-full py-xs border border-primary text-primary font-bold rounded-lg hover:bg-primary-container/10 transition-colors font-label-md text-label-md">
              View Detailed Audit
            </button>
          </Link>
        </div>

        {/* Career Roadmap */}
        <div className="md:col-span-8 bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <div className="flex justify-between items-center mb-md">
            <div>
              <p className="font-label-md text-label-md text-on-surface-variant">Career Roadmap</p>
              {latestRoadmap && (
                <p className="font-headline-md text-headline-md text-on-surface">{latestRoadmap.target_role}</p>
              )}
            </div>
            {latestRoadmap ? (
              <Link href="/roadmap">
                <span className="px-sm py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-sm text-label-sm cursor-pointer hover:opacity-80 transition-opacity">
                  View full plan
                </span>
              </Link>
            ) : null}
          </div>

          {!latestRoadmap ? (
            <div className="flex flex-col items-center justify-center py-lg gap-sm text-center">
              <span className="material-symbols-outlined text-outline" style={{ fontSize: 40 }}>route</span>
              <p className="font-body-md text-body-md text-on-surface-variant">No roadmap yet.</p>
              <Link href="/roadmap">
                <button className="mt-xs px-md py-xs bg-primary text-on-primary rounded-lg font-label-md text-label-md hover:opacity-90 transition-opacity">
                  Generate Roadmap
                </button>
              </Link>
            </div>
          ) : (
            <div className="space-y-sm">
              {milestones.map((m, i) => {
                const status = i === 0 ? "done" : i === 1 ? "active" : "locked";
                return (
                  <div key={m.week} className="flex items-start gap-md">
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          status === "done"
                            ? "bg-secondary text-on-secondary"
                            : status === "active"
                              ? "border-2 border-primary bg-primary-container text-primary"
                              : "border-2 border-outline-variant bg-surface-container text-on-surface-variant"
                        }`}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 18, fontVariationSettings: status === "done" ? "'FILL' 1" : "'FILL' 0" }}>
                          {status === "done" ? "check" : status === "active" ? "bolt" : "lock"}
                        </span>
                      </div>
                      {i < milestones.length - 1 && (
                        <div className={`w-px h-10 mt-1 ${status === "done" ? "bg-secondary opacity-30" : "bg-outline-variant"}`} />
                      )}
                    </div>
                    <div className="pt-1 flex-1">
                      <p className="font-label-sm text-label-sm text-on-surface-variant">Week {m.week}</p>
                      <h4 className={`font-label-md text-label-md text-on-surface ${status === "done" ? "line-through opacity-50" : "font-bold"}`}>
                        {m.title}
                      </h4>
                      <p className="font-body-md text-body-md text-on-surface-variant line-clamp-1">{m.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ATS trend chart */}
        <div className="md:col-span-7 bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <p className="font-label-md text-label-md text-on-surface-variant mb-xs">ATS Score Over Time</p>
          <h3 className="font-headline-md text-headline-md text-on-surface mb-md">Track your resume strength</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.ats_trend ?? []}>
                <XAxis dataKey="date" stroke="#6a7b73" fontSize={11} />
                <YAxis stroke="#6a7b73" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #b9cbc2", borderRadius: 8 }} />
                <Line type="monotone" dataKey="score" stroke="#006b54" strokeWidth={2} dot={{ r: 3, fill: "#006b54" }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="md:col-span-5 bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <p className="font-label-md text-label-md text-on-surface-variant mb-md">Recent Activity</p>
          <div className="space-y-md">
            {activityItems.map((a, i) => (
              <div key={i} className="flex gap-sm">
                <div className={`w-2 h-2 rounded-full ${a.color} mt-2 shrink-0`} />
                <div>
                  <p className="font-label-md text-label-md text-on-surface">{a.title}</p>
                  <p className="font-label-sm text-label-sm text-on-surface-variant">{a.sub}</p>
                </div>
              </div>
            ))}
          </div>
          <Link href="/analyzer">
            <button className="w-full mt-lg text-primary font-label-md text-label-md hover:underline text-left">
              See full log →
            </button>
          </Link>
        </div>

        {/* ML Performance */}
        <div className="md:col-span-12 bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <div className="flex items-start justify-between gap-4 mb-md">
            <div>
              <p className="font-label-md text-label-md text-on-surface-variant">ML Model Performance</p>
              <h3 className="font-headline-md text-headline-md text-on-surface">
                {ml
                  ? `${ml.algorithm} + ${ml.vectorizer}`
                  : "Latest classifier metrics"}
              </h3>
              {ml && (
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Trained on {ml.train_size.toLocaleString()} rows · {ml.num_classes} roles
                </p>
              )}
            </div>
            {ml && (
              <span className="rounded-full border border-outline-variant px-3 py-1 font-label-sm text-label-sm text-on-surface-variant">
                {new Date(ml.created_at).toLocaleString()}
              </span>
            )}
          </div>
          <div className="h-64">
            {mlLoading ? (
              <div className="flex h-full items-center justify-center text-on-surface-variant font-body-md">Loading…</div>
            ) : mlError || !ml ? (
              <div className="flex h-full items-center justify-center text-center font-body-md text-on-surface-variant">
                No metrics yet. Run{" "}
                <code className="mx-1 rounded bg-surface-container px-1.5 py-0.5 font-mono text-sm">
                  python backend/scripts/train_model.py
                </code>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ml.metrics} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                  <CartesianGrid stroke="#e6f0ea" vertical={false} />
                  <XAxis dataKey="metric" stroke="#6a7b73" fontSize={12} />
                  <YAxis stroke="#6a7b73" fontSize={12} domain={[0, 1]} tickFormatter={(v) => `${Math.round(v * 100)}%`} />
                  <Tooltip
                    contentStyle={{ background: "#ffffff", border: "1px solid #b9cbc2", borderRadius: 8 }}
                    formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
                  />
                  <Bar dataKey="value" name="Score" radius={[4, 4, 0, 0]}>
                    {ml.metrics.map((m: { metric: string }) => (
                      <Cell key={m.metric} fill={ML_METRIC_COLORS[m.metric] ?? "#006b54"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
