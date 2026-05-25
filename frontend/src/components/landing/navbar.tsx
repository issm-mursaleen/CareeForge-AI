"use client";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-md border-b border-outline-variant shadow-sm">
      <nav className="flex justify-between items-center px-margin py-xs max-w-7xl mx-auto w-full h-16">
        <div className="flex items-center gap-xs">
          <span className="font-headline-md text-headline-md font-bold text-primary">CareerForge AI</span>
        </div>

        <div className="hidden md:flex items-center gap-lg">
          <Link href="#features" className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md">
            Features
          </Link>
          <Link href="#trust" className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md">
            Customers
          </Link>
          <Link href="#pricing" className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-body-md">
            Pricing
          </Link>
        </div>

        <div className="flex items-center gap-md">
          <Link href="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link href="/register">
            <Button size="sm">Get started</Button>
          </Link>
        </div>
      </nav>
    </header>
  );
}
