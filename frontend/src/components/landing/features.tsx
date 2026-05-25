const features = [
  {
    icon: "description",
    title: "Intelligent Resume Scoring",
    body: "Our AI analyzes your experience against thousands of successful industry profiles to give you an objective score and actionable improvements.",
    bullets: ["Keyword Optimization", "ATS Compatibility Check"],
    wide: true,
  },
  {
    icon: "route",
    title: "Personal Roadmaps",
    body: "Step-by-step milestones tailored to your career goals and current skill set gaps.",
    wide: false,
  },
];

export function Features() {
  return (
    <section id="features" className="px-margin py-xl max-w-7xl mx-auto">
      <div className="text-center mb-xl">
        <h2 className="font-headline-lg text-headline-lg text-on-surface mb-xs">
          Engineered for Your Growth
        </h2>
        <p className="text-on-surface-variant font-body-lg text-body-lg max-w-2xl mx-auto">
          Precision tools designed to eliminate the guesswork from your career advancement journey.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        {/* Resume Scoring — wide */}
        <div className="md:col-span-8 bg-surface-container-lowest border border-outline-variant rounded-xl p-lg flex flex-col md:flex-row gap-lg hover:shadow-md transition-all group">
          <div className="flex-1">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-md group-hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined text-primary">description</span>
            </div>
            <h3 className="font-headline-md text-headline-md mb-xs">Intelligent Resume Scoring</h3>
            <p className="text-on-surface-variant font-body-md text-body-md mb-md">
              Our AI analyzes your experience against thousands of successful industry profiles to give
              you an objective score and actionable improvements.
            </p>
            <ul className="space-y-2">
              {["Keyword Optimization", "ATS Compatibility Check"].map((b) => (
                <li key={b} className="flex items-center gap-xs font-label-md text-label-md text-on-surface">
                  <span
                    className="material-symbols-outlined text-secondary"
                    style={{ fontSize: 18, fontVariationSettings: "'FILL' 1" }}
                  >
                    check_circle
                  </span>
                  {b}
                </li>
              ))}
            </ul>
          </div>
          <div className="flex-1 bg-surface-container rounded-lg p-sm border border-outline-variant/20 flex flex-col justify-center">
            <div className="space-y-xs">
              <div className="flex justify-between items-end">
                <span className="text-xs font-label-sm uppercase text-outline">Actionable Impact</span>
                <span className="text-secondary font-bold font-label-md">+42% Higher Reach</span>
              </div>
              <div className="flex gap-1 h-12 items-end">
                {[40, 55, 35, 70, 95].map((h, i) => (
                  <div
                    key={i}
                    className={`w-full rounded-t ${i === 4 ? "bg-secondary" : "bg-primary/40"}`}
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Personal Roadmap — narrow */}
        <div className="md:col-span-4 bg-surface-container-lowest border border-outline-variant rounded-xl p-lg hover:shadow-md transition-all group">
          <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-md group-hover:bg-secondary/20 transition-colors">
            <span className="material-symbols-outlined text-secondary">route</span>
          </div>
          <h3 className="font-headline-md text-headline-md mb-xs">Personal Roadmaps</h3>
          <p className="text-on-surface-variant font-body-md text-body-md mb-md">
            Step-by-step milestones tailored to your career goals and current skill set gaps.
          </p>
          <div className="relative pl-xs">
            <div className="absolute left-1 top-1 bottom-1 w-px bg-outline-variant" />
            <div className="space-y-md">
              <div className="relative flex items-center gap-sm">
                <div className="w-2 h-2 rounded-full bg-secondary z-10 -ml-[5px]" />
                <span className="font-label-sm text-label-sm">Certify: Cloud Arch</span>
              </div>
              <div className="relative flex items-center gap-sm">
                <div className="w-2 h-2 rounded-full bg-primary z-10 -ml-[5px]" />
                <span className="font-label-sm text-label-sm text-outline">Milestone: Senior Lead</span>
              </div>
            </div>
          </div>
        </div>

        {/* AI Interview Coaching — full width */}
        <div className="md:col-span-12 bg-inverse-surface text-inverse-on-surface rounded-xl p-lg flex flex-col md:flex-row items-center gap-lg">
          <div className="flex-1">
            <div className="inline-flex items-center gap-xs px-sm py-1 bg-primary-container/20 rounded-full mb-md">
              <span className="font-label-sm text-label-sm text-primary-fixed-dim">Real-time Feedback</span>
            </div>
            <h3 className="font-headline-lg text-headline-lg mb-md">AI Interview Coaching</h3>
            <p className="font-body-lg text-body-lg text-surface-variant mb-lg">
              Practice with an AI that mimics senior hiring managers. Get instant feedback on your
              tone, pacing, and content quality.
            </p>
            <a
              href="/register"
              className="inline-flex items-center gap-sm bg-secondary text-on-secondary px-md py-xs rounded-lg font-label-md hover:opacity-90 transition-all"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>mic</span>
              Start Mock Session
            </a>
          </div>
          <div className="flex-1 w-full">
            <div className="aspect-video bg-surface-container-highest/10 rounded-lg border border-outline/30 flex items-center justify-center">
              <div className="flex flex-col items-center gap-sm">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center shadow-lg">
                  <span className="material-symbols-outlined text-white" style={{ fontSize: 32 }}>play_arrow</span>
                </div>
                <span className="font-label-sm text-label-sm">Watch Demo</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
