export function Footer() {
  return (
    <footer className="w-full py-xl bg-surface-container-low border-t border-outline-variant">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-lg px-margin max-w-7xl mx-auto">
        <div className="col-span-1">
          <span className="font-headline-md text-headline-md font-bold text-primary mb-md block">
            CareerForge AI
          </span>
          <p className="text-on-surface-variant font-body-md text-body-md mb-md">
            Accelerating professional momentum with AI-powered insights and strategic career roadmaps.
          </p>
          <div className="flex gap-md">
            <a href="#" className="text-on-surface-variant hover:text-primary transition-colors">
              <span className="material-symbols-outlined">public</span>
            </a>
            <a href="#" className="text-on-surface-variant hover:text-primary transition-colors">
              <span className="material-symbols-outlined">alternate_email</span>
            </a>
          </div>
        </div>

        <div className="space-y-sm">
          <h4 className="font-label-md text-label-md text-on-surface font-bold uppercase">Product</h4>
          <ul className="space-y-xs">
            {["Features", "Pricing", "AI Insights"].map((l) => (
              <li key={l}>
                <a href="#" className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md">
                  {l}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-sm">
          <h4 className="font-label-md text-label-md text-on-surface font-bold uppercase">Support</h4>
          <ul className="space-y-xs">
            {["Help Center", "Privacy", "Terms"].map((l) => (
              <li key={l}>
                <a href="#" className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md">
                  {l}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-sm">
          <h4 className="font-label-md text-label-md text-on-surface font-bold uppercase">Stay Updated</h4>
          <div className="flex items-center bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden p-1">
            <input
              className="border-none focus:ring-0 w-full font-body-md px-2 bg-transparent text-on-surface text-sm outline-none"
              placeholder="Email address"
              type="email"
            />
            <button className="bg-primary text-on-primary px-sm py-1 rounded-md">
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-margin mt-xl pt-lg border-t border-outline-variant">
        <p className="text-on-surface-variant font-body-md text-body-md text-center opacity-80">
          © {new Date().getFullYear()} CareerForge AI. Accelerating professional momentum.
        </p>
      </div>
    </footer>
  );
}
