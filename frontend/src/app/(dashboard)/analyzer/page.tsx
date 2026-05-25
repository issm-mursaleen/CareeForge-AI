"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { resumeService } from "@/services/resume";
import type { ResumeAnalysis } from "@/types/api";
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
} from "recharts";

export default function AnalyzerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jd, setJd] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<ResumeAnalysis | null>(null);

  async function submit() {
    if (!file) return toast.error("Pick a resume file first");
    setSubmitting(true);
    try {
      const r = await resumeService.analyze(file, jd || undefined);
      setResult(r);
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Analysis failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-lg max-w-7xl mx-auto">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Resume Analyzer</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Upload your resume and get an instant ATS compatibility report.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-xs px-md py-xs bg-secondary-container/30 rounded-full border border-secondary/20">
          <span className="material-symbols-outlined text-secondary" style={{ fontSize: 16 }}>auto_awesome</span>
          <span className="font-label-sm text-label-sm text-on-secondary-container">AI-Powered Analysis</span>
        </div>
      </div>

      {/* Upload card */}
      <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
        <div className="flex items-center gap-sm mb-md">
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
            <span className="material-symbols-outlined text-primary">upload_file</span>
          </div>
          <div>
            <h2 className="font-headline-md text-headline-md text-on-surface">Upload Resume</h2>
            <p className="font-label-sm text-label-sm text-on-surface-variant">PDF, DOCX, or TXT · max 5 MB</p>
          </div>
        </div>

        {/* Drop zone */}
        <label className="block cursor-pointer">
          <div className="rounded-xl border-2 border-dashed border-outline-variant bg-surface-container p-lg text-center hover:border-primary hover:bg-primary/5 transition-all">
            <span className="material-symbols-outlined text-on-surface-variant block mx-auto mb-sm" style={{ fontSize: 40 }}>
              cloud_upload
            </span>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {file ? (
                <span className="text-primary font-bold">{file.name}</span>
              ) : (
                <>Drag & drop or <span className="text-primary font-bold">browse files</span></>
              )}
            </p>
          </div>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="sr-only"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>

        {/* Job description */}
        <div className="mt-md">
          <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">
            Target Job Description <span className="text-outline">(optional)</span>
          </label>
          <Textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the job description to enable role-fit scoring…"
            className="bg-surface-container border-outline-variant text-on-surface placeholder:text-outline focus:border-primary focus:ring-primary/20 rounded-lg"
            rows={4}
          />
        </div>

        <div className="mt-md flex gap-sm">
          <Button onClick={submit} loading={submitting} size="lg">
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>analytics</span>
            Analyze Resume
          </Button>
          {file && (
            <Button variant="outline" onClick={() => { setFile(null); setResult(null); }}>
              Clear
            </Button>
          )}
        </div>
      </div>

      {result && <ResultView result={result} />}
    </div>
  );
}

function ResultView({ result }: { result: ResumeAnalysis }) {
  const radarData = [
    { axis: "Sections", value: result.ats.section_completeness * 4 },
    { axis: "Contact", value: result.ats.contact_info * 10 },
    { axis: "Length", value: result.ats.length * 6.66 },
    { axis: "Skills", value: result.ats.skill_density * 4 },
    { axis: "JD match", value: result.ats.jd_match * 4 },
  ];

  const score = result.ats.score;
  const circumference = 2 * Math.PI * 60;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="space-y-gutter">
      <div className="flex items-center gap-sm">
        <div className="w-2 h-2 rounded-full bg-secondary" />
        <h2 className="font-headline-md text-headline-md text-on-surface">Analysis Complete</h2>
        <span className="px-sm py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-sm text-label-sm ml-auto">
          {result.file_name}
        </span>
      </div>

      <div className="grid gap-gutter lg:grid-cols-2">
        {/* ATS Score */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <p className="font-label-md text-label-md text-on-surface-variant mb-md">ATS Compatibility Score</p>
          <div className="flex items-center gap-lg">
            {/* Circular gauge */}
            <div className="relative w-32 h-32 shrink-0">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 132 132">
                <circle cx="66" cy="66" r="60" fill="transparent" stroke="#e6f0ea" strokeWidth="10" />
                <circle
                  cx="66" cy="66" r="60" fill="transparent"
                  stroke={score >= 70 ? "#266956" : score >= 40 ? "#aa324b" : "#ba1a1a"}
                  strokeWidth="10"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-headline-lg text-headline-lg text-on-surface">{score.toFixed(0)}</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">/ 100</span>
              </div>
            </div>

            {/* Radar chart */}
            <div className="flex-1 h-48">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#b9cbc2" />
                  <PolarAngleAxis dataKey="axis" stroke="#6a7b73" fontSize={11} />
                  <PolarRadiusAxis stroke="#b9cbc2" tick={false} domain={[0, 100]} />
                  <Radar dataKey="value" stroke="#006b54" fill="#006b54" fillOpacity={0.2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Skills detected */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <p className="font-label-md text-label-md text-on-surface-variant mb-md">Skills Detected</p>
          <div className="flex flex-wrap gap-2 mb-md">
            {result.skills.length === 0 ? (
              <span className="font-body-md text-body-md text-on-surface-variant">No skills detected.</span>
            ) : (
              result.skills.map((s) => (
                <span
                  key={s}
                  className="rounded-lg bg-secondary-container/50 px-2 py-1 font-label-sm text-label-sm text-on-secondary-container border border-secondary/20"
                >
                  {s}
                </span>
              ))
            )}
          </div>

          {result.missing_skills.length > 0 && (
            <>
              <p className="font-label-md text-label-md text-on-surface-variant mt-md mb-xs">Missing from JD</p>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills.map((s) => (
                  <span
                    key={s}
                    className="rounded-lg bg-error-container/50 px-2 py-1 font-label-sm text-label-sm text-on-error-container border border-error/20"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm">
          <div className="flex items-center gap-sm mb-md">
            <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: 18 }}>lightbulb</span>
            </div>
            <p className="font-label-md text-label-md text-on-surface-variant">Improvement Suggestions</p>
          </div>
          <ul className="space-y-sm">
            {result.suggestions.map((s, i) => (
              <li key={i} className="flex items-start gap-sm">
                <span
                  className="material-symbols-outlined text-secondary mt-0.5 shrink-0"
                  style={{ fontSize: 16, fontVariationSettings: "'FILL' 1" }}
                >
                  check_circle
                </span>
                <span className="font-body-md text-body-md text-on-surface">{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
