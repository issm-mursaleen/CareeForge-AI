"use client";

import { useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { rankingService } from "@/services/ranking";
import type { Algo, RankingResponse } from "@/types/api";

const ALGOS: Algo[] = ["bm25", "word2vec", "bert"];
const ALGO_LABELS: Record<Algo, string> = { bm25: "BM25", word2vec: "Word2Vec", bert: "BERT" };
const ALLOWED = [".pdf", ".docx", ".txt"];

export default function RankingPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [algos, setAlgos] = useState<Set<Algo>>(new Set(["bm25", "bert"]));
  const [jobTitle, setJobTitle] = useState("");
  const [jd, setJd] = useState("");
  const [dragging, setDragging] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<RankingResponse | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function addFiles(incoming: FileList | null) {
    if (!incoming) return;
    const valid: File[] = [];
    const rejected: string[] = [];
    Array.from(incoming).forEach((f) => {
      const ext = "." + f.name.split(".").pop()?.toLowerCase();
      if (ALLOWED.includes(ext)) {
        // deduplicate by name
        if (!files.some((existing) => existing.name === f.name)) valid.push(f);
      } else {
        rejected.push(f.name);
      }
    });
    if (rejected.length) toast.error(`Skipped unsupported file(s): ${rejected.join(", ")}`);
    if (valid.length) setFiles((prev) => [...prev, ...valid]);
  }

  function removeFile(name: string) {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  }

  function toggleAlgo(a: Algo) {
    setAlgos((prev) => {
      const next = new Set(prev);
      next.has(a) ? next.delete(a) : next.add(a);
      return next;
    });
  }

  async function run() {
    if (files.length === 0) return toast.error("Upload at least one resume");
    if (algos.size === 0) return toast.error("Select at least one algorithm");
    if (!jd.trim()) return toast.error("Paste a job description");
    setSubmitting(true);
    try {
      const r = await rankingService.rankFiles({
        files,
        job_title: jobTitle.trim() || "Untitled role",
        job_description: jd,
        algorithms: [...algos],
        explain_top_k: 3,
      });
      setResult(r);
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Ranking failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-lg max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-md">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Candidate Ranking</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Upload resumes directly and score them against a job description.
          </p>
        </div>
        <div className="flex items-center gap-xs px-md py-xs bg-secondary-container/30 rounded-full border border-secondary/20 w-fit">
          <span className="material-symbols-outlined text-secondary" style={{ fontSize: 16 }}>analytics</span>
          <span className="font-label-sm text-label-sm text-on-secondary-container">Multi-Algorithm Scoring</span>
        </div>
      </div>

      <div className="grid gap-gutter lg:grid-cols-2">
        {/* ── Left: Job details + algorithms ── */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm space-y-md">
          <div className="flex items-center gap-sm">
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
              <span className="material-symbols-outlined text-primary">work</span>
            </div>
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface">Job Details</h2>
              <p className="font-label-sm text-label-sm text-on-surface-variant">Role title and description to score against</p>
            </div>
          </div>

          <div>
            <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">Job Title</label>
            <Input
              placeholder="e.g. Senior Software Engineer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />
          </div>

          <div>
            <label className="block font-label-md text-label-md text-on-surface-variant mb-xs">
              Job Description <span className="text-error">*</span>
            </label>
            <Textarea
              placeholder="Paste the full job description here…"
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              rows={6}
            />
          </div>

          {/* Algorithm selector */}
          <div>
            <p className="font-label-md text-label-md text-on-surface-variant mb-xs">Algorithms</p>
            <div className="flex gap-sm flex-wrap">
              {ALGOS.map((a) => {
                const active = algos.has(a);
                return (
                  <button
                    key={a}
                    onClick={() => toggleAlgo(a)}
                    className={`inline-flex items-center gap-xs px-md py-xs rounded-lg font-label-md text-label-md transition-all border ${
                      active
                        ? "bg-primary text-on-primary border-primary"
                        : "bg-surface-container text-on-surface-variant border-outline-variant hover:bg-surface-container-high"
                    }`}
                  >
                    {active && (
                      <span className="material-symbols-outlined" style={{ fontSize: 14, fontVariationSettings: "'FILL' 1" }}>
                        check_circle
                      </span>
                    )}
                    {ALGO_LABELS[a]}
                  </button>
                );
              })}
            </div>
            {algos.size > 0 && (
              <p className="font-label-sm text-label-sm text-outline mt-xs">
                Composite = weighted blend of {[...algos].map((a) => ALGO_LABELS[a]).join(" + ")}
              </p>
            )}
          </div>

          <Button onClick={run} loading={submitting} size="lg" className="w-full">
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>leaderboard</span>
            Run Ranking
          </Button>
        </div>

        {/* ── Right: Multi-file upload ── */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm flex flex-col gap-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-sm">
              <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                <span className="material-symbols-outlined text-secondary">upload_file</span>
              </div>
              <div>
                <h2 className="font-headline-md text-headline-md text-on-surface">Upload Resumes</h2>
                <p className="font-label-sm text-label-sm text-on-surface-variant">PDF, DOCX, or TXT · multiple files</p>
              </div>
            </div>
            {files.length > 0 && (
              <span className="px-sm py-1 bg-primary-container text-on-primary-container rounded-full font-label-sm text-label-sm">
                {files.length} file{files.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>

          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }}
            onClick={() => inputRef.current?.click()}
            className={`rounded-xl border-2 border-dashed cursor-pointer transition-all p-lg flex flex-col items-center justify-center gap-sm text-center ${
              dragging
                ? "border-primary bg-primary/5"
                : "border-outline-variant bg-surface-container hover:border-primary hover:bg-primary/5"
            }`}
          >
            <span
              className={`material-symbols-outlined ${dragging ? "text-primary" : "text-outline"}`}
              style={{ fontSize: 40 }}
            >
              cloud_upload
            </span>
            <div>
              <p className="font-body-md text-body-md text-on-surface-variant">
                <span className="text-primary font-bold">Click to browse</span> or drag & drop
              </p>
              <p className="font-label-sm text-label-sm text-outline mt-1">PDF, DOCX, TXT · no limit</p>
            </div>
          </div>

          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            className="sr-only"
            onChange={(e) => addFiles(e.target.files)}
          />

          {/* File list */}
          {files.length > 0 && (
            <ul className="space-y-xs max-h-64 overflow-auto pr-1">
              {files.map((f, i) => (
                <li
                  key={f.name}
                  className="flex items-center gap-sm px-md py-xs bg-surface-container rounded-lg border border-outline-variant/40"
                >
                  {/* Rank badge — shows after submit */}
                  <span className="w-6 h-6 rounded-full bg-surface-container-high flex items-center justify-center font-label-sm text-label-sm text-on-surface-variant shrink-0">
                    {i + 1}
                  </span>
                  <span className="material-symbols-outlined text-on-surface-variant shrink-0" style={{ fontSize: 18 }}>
                    {f.name.endsWith(".pdf") ? "picture_as_pdf" : "description"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-label-md text-label-md text-on-surface truncate">{f.name}</p>
                    <p className="font-label-sm text-label-sm text-outline">{(f.size / 1024).toFixed(0)} KB</p>
                  </div>
                  <button
                    onClick={() => removeFile(f.name)}
                    className="text-on-surface-variant hover:text-error transition-colors shrink-0"
                    title="Remove"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>close</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {files.length > 1 && (
            <button
              onClick={() => setFiles([])}
              className="self-start font-label-sm text-label-sm text-on-surface-variant hover:text-error transition-colors"
            >
              Remove all
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      {result && <RankingResults result={result} />}
    </div>
  );
}

function RankingResults({ result }: { result: RankingResponse }) {
  const topScore = result.ranked[0]?.composite ?? 1;

  return (
    <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm space-y-md">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-md text-headline-md text-on-surface">
            Results · {result.job_title}
          </h2>
          <p className="font-label-sm text-label-sm text-on-surface-variant">
            Composite = weighted blend of {result.algorithms.join(", ")}
          </p>
        </div>
        <span className="px-sm py-1 bg-secondary-container text-on-secondary-container rounded-full font-label-sm text-label-sm">
          {result.ranked.length} candidates
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-outline-variant">
              {["#", "File", "BM25", "W2V", "BERT", "Composite", "Fit"].map((h) => (
                <th key={h} className="text-left py-sm pr-md font-label-md text-label-md text-on-surface-variant last:pr-0">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.ranked.map((c, i) => {
              const pct = topScore > 0 ? (c.composite / topScore) * 100 : 0;
              return (
                <tr key={c.resume_id} className="border-b border-outline-variant/40 hover:bg-surface-container transition-colors">
                  <td className="py-sm pr-md">
                    <span className={`w-6 h-6 rounded-full inline-flex items-center justify-center font-label-sm text-label-sm ${
                      i === 0 ? "bg-secondary text-on-secondary" :
                      i === 1 ? "bg-secondary-container text-on-secondary-container" :
                                "bg-surface-container text-on-surface-variant"
                    }`}>
                      {i + 1}
                    </span>
                  </td>
                  <td className="py-sm pr-md max-w-[180px]">
                    <span className="font-body-md text-body-md text-on-surface truncate block">{c.file_name}</span>
                    <div className="mt-1 w-full bg-surface-container rounded-full h-1">
                      <div className="bg-secondary h-full rounded-full transition-all" style={{ width: `${pct}%` }} />
                    </div>
                  </td>
                  <td className="py-sm pr-md font-label-md text-label-md text-on-surface-variant">
                    {c.bm25 != null ? c.bm25.toFixed(3) : <span className="text-outline">—</span>}
                  </td>
                  <td className="py-sm pr-md font-label-md text-label-md text-on-surface-variant">
                    {c.word2vec != null ? c.word2vec.toFixed(3) : <span className="text-outline">—</span>}
                  </td>
                  <td className="py-sm pr-md font-label-md text-label-md text-on-surface-variant">
                    {c.bert != null ? c.bert.toFixed(3) : <span className="text-outline">—</span>}
                  </td>
                  <td className="py-sm pr-md">
                    <span className="font-label-md text-label-md text-on-surface font-bold">{c.composite.toFixed(3)}</span>
                  </td>
                  <td className="py-sm">
                    {c.is_good_fit == null ? (
                      <span className="text-outline font-label-sm text-label-sm">—</span>
                    ) : c.is_good_fit ? (
                      <span className="px-xs py-0.5 bg-secondary-container text-on-secondary-container rounded font-label-sm text-label-sm">Good fit</span>
                    ) : (
                      <span className="px-xs py-0.5 bg-error-container text-on-error-container rounded font-label-sm text-label-sm">Not a fit</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {result.ranked.some((c) => c.explanation) && (
        <div className="space-y-sm pt-sm border-t border-outline-variant">
          <p className="font-label-md text-label-md text-on-surface-variant">AI Explanations (top candidates)</p>
          {result.ranked
            .filter((c) => c.explanation)
            .map((c) => (
              <div key={c.resume_id} className="rounded-lg bg-surface-container p-sm border border-outline-variant/40">
                <p className="font-label-md text-label-md text-on-surface mb-xs">{c.file_name}</p>
                <p className="font-body-md text-body-md text-on-surface-variant">{c.explanation}</p>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
