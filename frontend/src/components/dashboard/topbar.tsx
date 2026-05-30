"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview",        icon: "dashboard",    roles: null },
  { href: "/analyzer",  label: "Resume Analyzer", icon: "description",  roles: null },
  { href: "/ranking",   label: "Ranking",         icon: "analytics",    roles: ["recruiter", "admin"] },
  { href: "/interview", label: "Interview Prep",  icon: "psychology",   roles: null },
  { href: "/roadmap",   label: "Roadmap",         icon: "route",        roles: null },
  { href: "/chat",      label: "AI Advisor",      icon: "chat",         roles: null },
  { href: "/admin",     label: "Admin",           icon: "shield",       roles: ["admin"] },
];

export function Topbar() {
  const [open, setOpen] = useState(false);
  const pathname  = usePathname();
  const router    = useRouter();
  const user      = useAuthStore((s) => s.user);
  const logout    = useAuthStore((s) => s.logout);
  const role      = useAuthStore((s) => s.user?.role);

  // Close drawer on route change
  useEffect(() => { setOpen(false); }, [pathname]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const filteredItems = NAV_ITEMS.filter(
    (i) => !i.roles || (role && i.roles.includes(role))
  );

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <>
      {/* ── Top bar ─────────────────────────────────────────────────── */}
      <header className="fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-4
                         bg-surface/90 backdrop-blur-xl border-b border-outline-variant shadow-sm md:hidden">
        {/* Hamburger */}
        <button
          onClick={() => setOpen(true)}
          className="touch-btn w-10 h-10 flex items-center justify-center rounded-xl
                     bg-surface-container border border-outline-variant text-on-surface-variant"
          aria-label="Open menu"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 22 }}>menu</span>
        </button>

        {/* Brand */}
        <Link href="/dashboard" className="font-bold text-primary" style={{ fontSize: 18 }}>
          CareerForge AI
        </Link>

        {/* Avatar / user initial */}
        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center
                        text-on-primary font-bold text-sm select-none">
          {user?.full_name?.charAt(0)?.toUpperCase() ?? "U"}
        </div>
      </header>

      {/* ── Backdrop ────────────────────────────────────────────────── */}
      {open && (
        <div
          className="fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm overlay-enter md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* ── Drawer ──────────────────────────────────────────────────── */}
      {open && (
        <aside className="fixed top-0 left-0 bottom-0 z-[70] w-72 flex flex-col
                          bg-surface border-r border-outline-variant drawer-enter md:hidden">
          {/* Drawer header */}
          <div className="flex items-center justify-between px-md py-md border-b border-outline-variant">
            <div>
              <p className="font-bold text-primary" style={{ fontSize: 18 }}>CareerForge AI</p>
              <p className="text-xs text-on-surface-variant mt-0.5 capitalize">
                {user?.full_name} · {user?.role}
              </p>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="touch-btn w-9 h-9 flex items-center justify-center rounded-xl
                         bg-surface-container text-on-surface-variant"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>close</span>
            </button>
          </div>

          {/* Nav items */}
          <nav className="flex-1 overflow-y-auto px-sm py-sm space-y-1">
            {filteredItems.map(({ href, label, icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href as any}
                  className={cn(
                    "flex items-center gap-sm px-sm py-sm rounded-xl transition-all duration-150",
                    "font-label-md text-label-md touch-btn",
                    active
                      ? "bg-primary-container text-on-primary-container font-bold"
                      : "text-on-surface-variant hover:bg-surface-container-high active:bg-surface-container"
                  )}
                >
                  <span
                    className="material-symbols-outlined"
                    style={{
                      fontSize: 22,
                      fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0",
                    }}
                  >
                    {icon}
                  </span>
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Bottom actions */}
          <div className="px-sm py-sm border-t border-outline-variant space-y-1 pb-safe">
            <Link href="/analyzer">
              <button className="touch-btn w-full py-sm bg-primary text-on-primary rounded-xl
                                 font-bold font-label-md text-label-md hover:opacity-90">
                <span className="material-symbols-outlined mr-2" style={{ fontSize: 18 }}>add</span>
                New Analysis
              </button>
            </Link>
            <button
              onClick={handleLogout}
              className="touch-btn w-full flex items-center gap-sm px-sm py-xs rounded-xl
                         text-on-surface-variant hover:bg-surface-container-high
                         font-label-md text-label-md transition-colors"
            >
              <span className="material-symbols-outlined" style={{ fontSize: 20 }}>logout</span>
              Sign out
            </button>
          </div>
        </aside>
      )}
    </>
  );
}
