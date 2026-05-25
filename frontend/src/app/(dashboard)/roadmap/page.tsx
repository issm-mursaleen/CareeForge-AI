"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { resumeService } from "@/services/resume";
import { roadmapService } from "@/services/roadmap";
import type { ResumeListItem, RoadmapPlan, RoadmapMilestone, RoadmapResource } from "@/types/api";

const TYPE_STYLE: Record<string, string> = {
  course:   "bg-brand-500/15 text-brand-700 ring-brand-500/25",
  book:     "bg-purple-500/15 text-purple-700 ring-purple-500/25",
  article:  "bg-emerald-500/15 text-emerald-700 ring-emerald-500/25",
  video:    "bg-rose-500/15 text-rose-700 ring-rose-500/25",
  practice: "bg-amber-500/15 text-amber-700 ring-amber-500/25",
};
function ResourceBadge({ type }: { type: string }) {
  const cls = TYPE_STYLE[type?.toLowerCase()] ?? TYPE_STYLE.article;
  return (
    <span className={`rounded-md px-2 py-0.5 text-xs font-medium ring-1 ${cls}`}>
      {type ?? "link"}
    </span>
  );
}

/* ─── setup panel ───────────────────────────────────────── */
function SetupPanel({ onGenerated }: { onGenerated: (plan: RoadmapPlan) => void }) {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    resumeService.list().then((list) => {
      setResumes(list);
      if (list.length) setResumeId(list[0].id);
    }).catch(() => {});
  }, []);

  async function generate() {
    if (!resumeId) return toast.error("Upload a resume first (Resume Analyzer page).");
    if (!targetRole.trim()) return toast.error("Enter a target role.");
    setLoading(true);
    try {
      const plan = await roadmapService.create(resumeId, targetRole.trim());
      onGenerated(plan);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail ?? "Failed to generate roadmap.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="max-w-xl">
      <CardTitle className="mb-1">Generate your career roadmap</CardTitle>
      <CardDescription className="mb-6">
        We&apos;ll analyse your resume, identify skill gaps, and build a personalised 12-week plan.
      </CardDescription>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm text-on-surface">Resume</label>
          {resumes.length === 0 ? (
            <p className="rounded-xl border border-dashed border-outline-variant bg-surface-container p-4 text-sm text-on-surface-variant">
              No resumes found. Go to <strong className="text-brand-400">Resume Analyzer</strong> first.
            </p>
          ) : (
            <select
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="w-full rounded-xl border border-outline-variant bg-surface-container px-4 py-2.5 text-sm text-on-surface outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.file_name}{r.ats_score != null ? ` — ATS ${r.ats_score.toFixed(0)}` : ""}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="mb-1.5 block text-sm text-on-surface">Target role</label>
          <Input
            placeholder="e.g. Machine Learning Engineer"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && generate()}
          />
        </div>

        <Button onClick={generate} loading={loading} size="lg" className="w-full mt-2">
          {loading ? "Building roadmap…" : "Generate Roadmap"}
        </Button>
      </div>
    </Card>
  );
}

/* ─── milestone timeline ─────────────────────────────────── */
function Timeline({ milestones }: { milestones: RoadmapMilestone[] }) {
  return (
    <div className="relative">
      {/* vertical line */}
      <div className="absolute left-5 top-0 bottom-0 w-px bg-outline-variant" />
      <div className="space-y-4">
        {milestones.map((m, i) => (
          <div key={i} className="relative flex gap-5">
            {/* dot */}
            <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-500/20 ring-2 ring-brand-500/40">
              <span className="text-xs font-bold text-brand-400">{m.week ?? i + 1}</span>
            </div>
            <Card className="flex-1 py-4 px-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-on-surface">{m.title}</p>
                  <p className="mt-1 text-sm text-on-surface-variant leading-relaxed">{m.description}</p>
                </div>
                <span className="shrink-0 text-xs text-on-surface-variant whitespace-nowrap">Week {m.week ?? i + 1}</span>
              </div>
              {m.skills?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {m.skills.map((s) => (
                    <span key={s} className="rounded-md bg-surface-container-high px-2 py-0.5 text-xs text-on-surface-variant ring-1 ring-outline-variant">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── resources grid ─────────────────────────────────────── */
function ResourcesGrid({ resources }: { resources: RoadmapResource[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {resources.map((r, i) => (
        <a
          key={i}
          href={r.url}
          target="_blank"
          rel="noopener noreferrer"
          className="group block rounded-2xl border border-outline-variant bg-surface-container p-4 transition-all hover:border-brand-500/40 hover:bg-surface-container-high"
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <ResourceBadge type={r.type} />
            <span className="text-on-surface-variant transition-colors group-hover:text-brand-400 text-xs">↗</span>
          </div>
          <p className="text-sm font-medium text-on-surface group-hover:text-primary transition-colors line-clamp-2">
            {r.title}
          </p>
        </a>
      ))}
    </div>
  );
}

/* ─── result view ────────────────────────────────────────── */
function PlanView({ plan, onReset }: { plan: RoadmapPlan; onReset: () => void }) {
  return (
    <div className="space-y-8">
      {/* header card */}
      <Card className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">Target Role</p>
          <p className="text-2xl font-bold gradient-text">{plan.target_role}</p>
        </div>
        <Button variant="outline" size="sm" onClick={onReset}>
          ↺ New Roadmap
        </Button>
      </Card>

      {/* skill gaps */}
      {plan.skill_gaps.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-on-surface">Skill Gaps</h2>
          <div className="flex flex-wrap gap-2">
            {plan.skill_gaps.map((g) => (
              <span key={g} className="rounded-md bg-red-500/10 px-3 py-1 text-sm text-red-300 ring-1 ring-red-500/25">
                {g}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* milestones */}
      {plan.milestones.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-on-surface">12-Week Milestones</h2>
          <Timeline milestones={plan.milestones} />
        </section>
      )}

      {/* resources */}
      {plan.resources.length > 0 && (
        <section>
          <h2 className="mb-4 text-lg font-semibold text-on-surface">Recommended Resources</h2>
          <ResourcesGrid resources={plan.resources} />
        </section>
      )}
    </div>
  );
}

/* ─── main page ──────────────────────────────────────────── */
export default function RoadmapPage() {
  const [plan, setPlan] = useState<RoadmapPlan | null>(null);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Career Roadmap</h1>
        <p className="text-on-surface-variant">12-week personalised plan based on your resume and target role.</p>
      </header>

      {!plan ? (
        <SetupPanel onGenerated={setPlan} />
      ) : (
        <PlanView plan={plan} onReset={() => setPlan(null)} />
      )}
    </div>
  );
}
