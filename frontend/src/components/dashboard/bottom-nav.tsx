"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";

const TABS = [
  { href: "/dashboard", label: "Home",     icon: "home"        },
  { href: "/analyzer",  label: "Analyze",  icon: "description" },
  { href: "/chat",      label: "Advisor",  icon: "chat"        },
  { href: "/roadmap",   label: "Roadmap",  icon: "route"       },
  { href: "/interview", label: "Prep",     icon: "psychology"  },
];

export function BottomNav() {
  const pathname = usePathname();
  const role = useAuthStore((s) => s.user?.role);

  const tabs = TABS.filter((t) => {
    if (t.href === "/ranking") return role === "recruiter" || role === "admin";
    return true;
  });

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 md:hidden
                 bg-surface/95 backdrop-blur-xl border-t border-outline-variant
                 flex items-stretch pb-safe"
      style={{ height: "calc(3.75rem + env(safe-area-inset-bottom, 0px))" }}
    >
      {tabs.map(({ href, label, icon }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={href as any}
            className={cn(
              "flex-1 flex flex-col items-center justify-center gap-0.5 touch-btn",
              "transition-all duration-150 select-none",
              active ? "text-primary" : "text-on-surface-variant"
            )}
          >
            {/* Active indicator dot */}
            {active && (
              <span
                className="absolute top-1.5 w-1 h-1 rounded-full bg-primary"
                style={{ animation: "pulseDot 1.2s ease-in-out 1" }}
              />
            )}
            <span
              className={cn(
                "material-symbols-outlined transition-all duration-200",
                active ? "scale-110" : "scale-100"
              )}
              style={{
                fontSize: 24,
                fontVariationSettings: active ? "'FILL' 1, 'wght' 600" : "'FILL' 0, 'wght' 400",
              }}
            >
              {icon}
            </span>
            <span
              className={cn(
                "font-label-sm text-label-sm transition-all duration-200",
                active ? "font-bold" : "font-normal"
              )}
              style={{ fontSize: 10 }}
            >
              {label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
