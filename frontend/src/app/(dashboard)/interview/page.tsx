"use client";

import { useState, useEffect, useRef } from "react";
import { toast } from "sonner";
import { Card, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { resumeService } from "@/services/resume";
import { interviewService } from "@/services/interview";
import type { ResumeListItem, InterviewSession, InterviewQuestion, AnswerResult } from "@/types/api";

/* ─── tiny helpers ──────────────────────────────────────── */
const BADGE: Record<string, string> = {
  technical:     "bg-brand-500/15 text-brand-300 ring-brand-500/30",
  behavioral:    "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  system_design: "bg-purple-500/15 text-purple-300 ring-purple-500/30",
};

function CategoryBadge({ category }: { category: string }) {
  const cls = BADGE[category?.toLowerCase()] ?? BADGE.technical;
  return (
    <span className={`rounded-md px-2 py-0.5 text-xs font-medium ring-1 ${cls}`}>
      {category ?? "technical"}
    </span>
  );
}

function ScoreRing({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score));
  const color = pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444";
  const r = 28;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width="72" height="72" viewBox="0 0 72 72" className="shrink-0">
      <circle cx="36" cy="36" r={r} fill="none" stroke="#1e293b" strokeWidth="6" />
      <circle
        cx="36" cy="36" r={r} fill="none"
        stroke={color} strokeWidth="6"
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        transform="rotate(-90 36 36)"
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
      <text x="36" y="41" textAnchor="middle" fontSize="16" fontWeight="700" fill={color}>
        {pct.toFixed(0)}
      </text>
    </svg>
  );
}

/* ─── step 1: setup form ─────────────────────────────────── */
function SetupPanel({
  onStart,
}: {
  onStart: (session: InterviewSession) => void;
}) {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [role, setRole] = useState("");
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    resumeService.list().then((list) => {
      setResumes(list);
      if (list.length) setResumeId(list[0].id);
    }).catch(() => {});
  }, []);

  async function start() {
    if (!resumeId) return toast.error("Upload a resume first (Resume Analyzer page).");
    if (!role.trim()) return toast.error("Enter a target role.");
    setLoading(true);
    try {
      const session = await interviewService.generate(resumeId, role.trim(), count);
      onStart(session);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail ?? "Failed to generate questions.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="max-w-xl">
      <CardTitle className="mb-1">Configure your session</CardTitle>
      <CardDescription className="mb-6">
        Pick a resume, set your target role, and choose how many questions to generate.
      </CardDescription>

      <div className="space-y-4">
        {/* Resume picker */}
        <div>
          <label className="mb-1.5 block text-sm text-slate-300">Resume</label>
          {resumes.length === 0 ? (
            <p className="rounded-xl border border-dashed border-white/10 bg-white/[0.02] p-4 text-sm text-slate-500">
              No resumes found. Go to <strong className="text-brand-400">Resume Analyzer</strong> and upload one first.
            </p>
          ) : (
            <select
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.file_name}
                  {r.ats_score != null ? ` — ATS ${r.ats_score.toFixed(0)}` : ""}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Role */}
        <div>
          <label className="mb-1.5 block text-sm text-slate-300">Target role</label>
          <Input
            placeholder="e.g. Senior Frontend Engineer"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && start()}
          />
        </div>

        {/* Count */}
        <div>
          <label className="mb-1.5 block text-sm text-slate-300">
            Number of questions — <span className="text-brand-400">{count}</span>
          </label>
          <input
            type="range" min={1} max={15} value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-full accent-brand-500"
          />
          <div className="mt-1 flex justify-between text-xs text-slate-500">
            <span>1</span><span>15</span>
          </div>
        </div>

        <Button onClick={start} loading={loading} size="lg" className="w-full mt-2">
          {loading ? "Generating questions…" : "Start Interview"}
        </Button>
      </div>
    </Card>
  );
}

/* ─── step 2: question card ──────────────────────────────── */
interface QuestionCardProps {
  index: number;
  total: number;
  question: InterviewQuestion;
  onAnswered: (answer: string) => void;
  isLast: boolean;
}

function QuestionCard({ index, total, question, onAnswered, isLast }: QuestionCardProps) {
  const [answer, setAnswer] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    textareaRef.current?.focus();
    setAnswer("");
  }, [index]);

  function submit() {
    if (!answer.trim()) return toast.error("Write an answer first.");
    onAnswered(answer.trim());
  }

  return (
    <div className="space-y-4 max-w-2xl">
      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-400 transition-all duration-500"
            style={{ width: `${((index) / total) * 100}%` }}
          />
        </div>
        <span className="shrink-0 text-xs text-slate-500">{index + 1} / {total}</span>
      </div>

      <Card>
        <div className="mb-3 flex items-start justify-between gap-4">
          <CardTitle className="text-base leading-snug">{question.question}</CardTitle>
          <CategoryBadge category={question.category} />
        </div>

        {question.expected_topics?.length > 0 && (
          <div className="mb-4 rounded-xl bg-white/[0.03] p-3">
            <p className="mb-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">Key topics to cover</p>
            <ul className="space-y-1">
              {question.expected_topics.map((pt, i) => (
                <li key={i} className="text-xs text-slate-400 flex gap-2">
                  <span className="text-brand-400 shrink-0">·</span>{pt}
                </li>
              ))}
            </ul>
          </div>
        )}

        <Textarea
          ref={textareaRef}
          placeholder="Type your answer here…"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          className="min-h-[140px] resize-none"
        />

        <div className="mt-4 flex gap-3">
          <Button onClick={submit} size="lg">
            {isLast ? "Submit & Grade Interview" : "Next Question →"}
          </Button>
          <Button
            variant="ghost"
            size="lg"
            onClick={() => onAnswered("")}
          >
            Skip
          </Button>
        </div>
      </Card>
    </div>
  );
}

/* ─── step 3: grading panel ──────────────────────────────── */
function GradingPanel({
  session,
  answers,
  onComplete,
}: {
  session: InterviewSession;
  answers: string[];
  onComplete: (results: AnswerResult[]) => void;
}) {
  useEffect(() => {
    async function gradeAll() {
      try {
        const promises = session.questions.map(async (q, i) => {
          if (!answers[i]) {
            return { score: 0, feedback: "Skipped", strengths: [], improvements: [] } as AnswerResult;
          }
          return interviewService.answer(session.interview_id, i, answers[i]);
        });
        const results = await Promise.all(promises);
        onComplete(results);
      } catch (e: any) {
        toast.error(e?.response?.data?.detail ?? "Scoring failed.");
        // Try to continue anyway with failed results if we can't score everything
        onComplete(answers.map(a => ({ score: 0, feedback: "Error grading this response", strengths: [], improvements: [] })));
      }
    }
    gradeAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Card className="flex max-w-2xl flex-col items-center justify-center py-20 text-center">
      <div className="mb-6 h-12 w-12 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      <CardTitle className="mb-2 text-xl">Grading your interview...</CardTitle>
      <p className="text-slate-400 max-w-sm">Our AI is analyzing your answers against the key topics and generating personalized feedback.</p>
    </Card>
  );
}


/* ─── step 4: summary ────────────────────────────────────── */
function SummaryPanel({
  session,
  results,
  onRestart,
}: {
  session: InterviewSession;
  results: AnswerResult[];
  onRestart: () => void;
}) {
  const avg = results.length
    ? results.reduce((a, r) => a + r.score, 0) / results.length
    : 0;
  const answered = results.filter((r) => r.score > 0).length;

  return (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <div className="flex items-center gap-6">
          <ScoreRing score={avg} />
          <div>
            <p className="text-2xl font-bold gradient-text">{avg.toFixed(1)} / 100</p>
            <p className="text-sm text-slate-400">{answered} of {session.questions.length} answered</p>
          </div>
        </div>
      </Card>

      <div className="space-y-4">
        {session.questions.map((q, i) => {
          const r = results[i];
          const isSkipped = !r || r.feedback === "Skipped" || r.score === 0;
          return (
            <Card key={i} className="p-5">
              <div className="flex items-start gap-5">
                {r && <ScoreRing score={r.score} />}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-slate-500">Q{i + 1}</span>
                    <CategoryBadge category={q.category} />
                  </div>
                  <p className="text-[15px] text-slate-200 font-medium leading-snug mb-3">{q.question}</p>
                  
                  {isSkipped ? (
                    <p className="text-sm text-slate-500 italic">Skipped</p>
                  ) : (
                    <div className="space-y-4 mt-4 pt-4 border-t border-white/5">
                      <p className="text-sm text-slate-400 leading-relaxed">{r.feedback}</p>
                      
                      <div className="grid gap-4 sm:grid-cols-2">
                        {r.strengths?.length > 0 && (
                          <div className="rounded-xl bg-emerald-500/5 p-4 ring-1 ring-emerald-500/15">
                            <p className="mb-2 text-[10px] font-bold text-emerald-500 uppercase tracking-wider">Strengths</p>
                            <ul className="space-y-1.5">
                              {r.strengths.map((s, idx) => (
                                <li key={idx} className="text-xs text-emerald-200/80 flex gap-2">
                                  <span className="shrink-0 text-emerald-500">✓</span>{s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {r.improvements?.length > 0 && (
                          <div className="rounded-xl bg-amber-500/5 p-4 ring-1 ring-amber-500/15">
                            <p className="mb-2 text-[10px] font-bold text-amber-500 uppercase tracking-wider">Areas to improve</p>
                            <ul className="space-y-1.5">
                              {r.improvements.map((s, idx) => (
                                <li key={idx} className="text-xs text-amber-200/80 flex gap-2">
                                  <span className="shrink-0 text-amber-500">→</span>{s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <Button onClick={onRestart} size="lg" variant="outline" className="w-full">
        ↺ Start New Session
      </Button>
    </div>
  );
}

/* ─── main page ──────────────────────────────────────────── */
type Phase = "setup" | "question" | "grading" | "summary";

export default function InterviewPage() {
  const [phase, setPhase] = useState<Phase>("setup");
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [results, setResults] = useState<AnswerResult[]>([]);

  function handleStart(s: InterviewSession) {
    setSession(s);
    setQIndex(0);
    setAnswers([]);
    setResults([]);
    setPhase("question");
  }

  function handleAnswered(answer: string) {
    if (!session) return;
    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);

    if (newAnswers.length >= session.questions.length) {
      setPhase("grading");
    } else {
      setQIndex((i) => i + 1);
    }
  }

  function handleGraded(gradedResults: AnswerResult[]) {
    setResults(gradedResults);
    setPhase("summary");
  }

  function restart() {
    setPhase("setup");
    setSession(null);
    setQIndex(0);
    setAnswers([]);
    setResults([]);
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Interview Prep</h1>
        <p className="text-slate-400">AI-generated questions tailored to your resume and target role.</p>
      </header>

      {phase === "setup" && <SetupPanel onStart={handleStart} />}

      {phase === "question" && session && (
        <QuestionCard
          key={qIndex}
          index={qIndex}
          total={session.questions.length}
          question={session.questions[qIndex]}
          onAnswered={handleAnswered}
          isLast={qIndex + 1 >= session.questions.length}
        />
      )}

      {phase === "grading" && session && (
        <GradingPanel
          session={session}
          answers={answers}
          onComplete={handleGraded}
        />
      )}

      {phase === "summary" && session && (
        <SummaryPanel session={session} results={results} onRestart={restart} />
      )}
    </div>
  );
}
