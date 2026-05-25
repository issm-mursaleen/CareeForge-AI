const companies = ["TECHCORP", "NEXUS", "ZENITH", "ORBIT", "VANTAGE"];

export function Stats() {
  return (
    <section id="trust" className="bg-surface-container-low py-xl px-margin border-y border-outline-variant">
      <div className="max-w-7xl mx-auto text-center">
        <span className="font-label-md text-label-md text-outline uppercase tracking-widest mb-lg block">
          Fueling Careers At Global Leaders
        </span>
        <div className="flex flex-wrap justify-center items-center gap-xl opacity-50 hover:opacity-100 transition-all">
          {companies.map((c) => (
            <div key={c} className="font-headline-lg text-headline-lg font-bold text-on-surface-variant">
              {c}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
