import Link from "next/link";

export function Pricing() {
  return (
    <section id="pricing" className="py-xl px-margin">
      <div className="max-w-5xl mx-auto bg-primary rounded-3xl p-lg md:p-xl text-center relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 bg-secondary/20 rounded-full blur-3xl" />

        <h2 className="font-display-lg text-display-lg text-white mb-md relative z-10">
          Ready to accelerate your flow?
        </h2>
        <p className="font-body-lg text-body-lg text-primary-fixed mb-lg max-w-xl mx-auto relative z-10">
          Join 50,000+ professionals who have boosted their interview callbacks by 3× using CareerForge AI.
        </p>

        <div className="flex flex-col sm:flex-row gap-md justify-center relative z-10">
          <Link href="/register">
            <button className="bg-white text-primary px-lg py-sm rounded-lg font-headline-md hover:bg-surface-bright transition-all active:scale-95">
              Get Started Free
            </button>
          </Link>
          <Link href="/login">
            <button className="bg-primary-container text-on-primary-container px-lg py-sm rounded-lg font-headline-md border border-white/20 hover:bg-primary-container/80 transition-all">
              Sign In
            </button>
          </Link>
        </div>
      </div>
    </section>
  );
}
