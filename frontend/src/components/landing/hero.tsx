"use client";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="px-margin py-xl pt-32 relative overflow-hidden bg-hero-gradient">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-xl items-center">
        {/* Left: Copy */}
        <div className="z-10">
          <div className="inline-flex items-center gap-xs px-sm py-1 bg-secondary-container/20 border border-secondary/20 rounded-full mb-md">
            <span className="material-symbols-outlined text-secondary text-sm" style={{ fontSize: 16 }}>auto_awesome</span>
            <span className="font-label-sm text-label-sm text-on-secondary-container">AI-Powered Career Advancement</span>
          </div>

          <h1 className="font-display-lg text-display-lg text-on-surface mb-md leading-tight">
            Your Professional{" "}
            <span className="text-primary">Momentum</span> Starts Here.
          </h1>

          <p className="font-body-lg text-body-lg text-on-surface-variant mb-lg max-w-xl">
            Transform your career trajectory with data-driven resume scoring, personalized
            development roadmaps, and AI-led interview practice.
          </p>

          <div className="flex flex-col sm:flex-row gap-md items-start sm:items-center">
            <Link href="/register">
              <Button size="lg" className="flex items-center gap-sm">
                <span className="material-symbols-outlined" style={{ fontSize: 20 }}>upload_file</span>
                Upload Resume
              </Button>
            </Link>
            <div className="flex flex-col">
              <span className="font-label-md text-label-md text-on-surface">Trusted by 50,000+ Professionals</span>
              <div className="flex gap-1 mt-2">
                {["G", "M", "A"].map((i) => (
                  <div key={i} className="w-8 h-8 rounded-full bg-secondary-container border-2 border-surface flex items-center justify-center font-bold text-xs text-on-secondary-container">
                    {i}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Preview widget */}
        <div className="relative">
          <div className="absolute -inset-4 bg-primary/5 blur-3xl rounded-full" />
          <div className="relative bg-surface-container-lowest rounded-xl shadow-xl border border-outline-variant p-md overflow-hidden">
            <div className="flex items-center justify-between mb-lg">
              <div className="flex items-center gap-xs">
                <div className="w-3 h-3 rounded-full bg-error" />
                <div className="w-3 h-3 rounded-full bg-secondary" />
                <div className="w-3 h-3 rounded-full bg-primary" />
              </div>
              <span className="font-label-sm text-label-sm text-outline">Analysis Dashboard</span>
            </div>

            <div className="space-y-md">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md">Resume Match Score</span>
                <span className="font-label-md text-label-md text-secondary">88% Optimal</span>
              </div>
              <div className="w-full bg-surface-container-low h-3 rounded-full overflow-hidden">
                <div className="bg-secondary h-full rounded-full" style={{ width: "88%" }} />
              </div>

              <div className="grid grid-cols-2 gap-sm pt-md">
                <div className="p-sm bg-surface-container rounded-lg border border-outline-variant/30">
                  <span className="font-label-sm text-label-sm text-outline block mb-1">Interviews Ready</span>
                  <span className="font-headline-md text-headline-md text-primary">12 Ready</span>
                </div>
                <div className="p-sm bg-surface-container rounded-lg border border-outline-variant/30">
                  <span className="font-label-sm text-label-sm text-outline block mb-1">Growth Tasks</span>
                  <span className="font-headline-md text-headline-md text-secondary">5 Done</span>
                </div>
              </div>

              <div className="rounded-lg border border-outline-variant bg-surface-container-low h-32 flex items-center justify-center mt-md">
                <div className="flex items-end gap-1 h-20 px-4">
                  {[40, 55, 35, 70, 95].map((h, i) => (
                    <div
                      key={i}
                      className={`w-8 rounded-t ${i === 4 ? "bg-secondary" : "bg-primary/40"}`}
                      style={{ height: `${h}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
