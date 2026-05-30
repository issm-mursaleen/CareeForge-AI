"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <header
        className={cn(
          "fixed top-0 w-full z-50 transition-all duration-300",
          scrolled
            ? "bg-surface/95 backdrop-blur-xl border-b border-outline-variant shadow-sm"
            : "bg-transparent"
        )}
      >
        <nav className="flex justify-between items-center px-4 md:px-margin max-w-7xl mx-auto w-full h-16">
          {/* Brand */}
          <Link href="/" className="font-bold text-primary text-lg">
            CareerForge AI
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-lg">
            {(["Features", "Customers", "Pricing"] as const).map((label) => (
              <a
                key={label}
                href={`#${label.toLowerCase()}`}
                className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md"
              >
                {label}
              </a>
            ))}
          </div>

          {/* CTA */}
          <div className="flex items-center gap-2">
            <Link href="/login" className="hidden sm:block">
              <Button variant="ghost" size="sm">Log in</Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Get started</Button>
            </Link>
            {/* Mobile hamburger */}
            <button
              className="touch-btn md:hidden w-10 h-10 flex items-center justify-center
                         rounded-xl bg-surface-container border border-outline-variant text-on-surface-variant ml-1"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle menu"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 22 }}>
                {menuOpen ? "close" : "menu"}
              </span>
            </button>
          </div>
        </nav>

        {/* Mobile menu dropdown */}
        {menuOpen && (
          <div className="md:hidden bg-surface border-b border-outline-variant px-4 pb-4 space-y-1 sheet-enter">
            {[
              { href: "#features",  label: "Features"  },
              { href: "#trust",     label: "Customers" },
              { href: "#pricing",   label: "Pricing"   },
            ].map(({ href, label }) => (
              <a
                key={href}
                href={href}
                onClick={() => setMenuOpen(false)}
                className="block px-sm py-sm rounded-xl text-on-surface-variant
                           hover:bg-surface-container-high font-label-md text-label-md
                           transition-colors touch-btn"
              >
                {label}
              </a>
            ))}
            <Link
              href="/login"
              onClick={() => setMenuOpen(false)}
              className="block px-sm py-sm rounded-xl text-on-surface-variant
                         hover:bg-surface-container-high font-label-md text-label-md
                         transition-colors touch-btn"
            >
              Log in
            </Link>
          </div>
        )}
      </header>
    </>
  );
}
