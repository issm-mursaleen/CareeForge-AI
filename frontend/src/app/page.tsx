import { Navbar } from "@/components/landing/navbar";
import { Hero } from "@/components/landing/hero";
import { Features } from "@/components/landing/features";
import { Stats } from "@/components/landing/stats";
import { Pricing } from "@/components/landing/pricing";
import { Footer } from "@/components/landing/footer";

export default function Landing() {
  return (
    <main>
      <Navbar />
      <Hero />
      <Stats />
      <Features />
      <Pricing />
      <Footer />
    </main>
  );
}
