"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth";

const items = [
  { href: "/dashboard", label: "Overview", icon: "dashboard", roles: null },
  { href: "/analyzer", label: "Resume Analyzer", icon: "description", roles: null },
  { href: "/ranking", label: "Ranking", icon: "analytics", roles: ["recruiter", "admin"] },
  { href: "/interview", label: "Interview Prep", icon: "psychology", roles: null },
  { href: "/roadmap", label: "Roadmap", icon: "route", roles: null },
  { href: "/chat", label: "AI Advisor", icon: "chat", roles: null },
  { href: "/admin", label: "Admin", icon: "shield", roles: ["admin"] },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const role = useAuthStore((s) => s.user?.role);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <aside className="hidden md:flex h-screen w-64 fixed left-0 top-0 border-r border-outline-variant flex-col p-md gap-xs bg-surface z-40">
      <div className="mb-lg">
        <Link href="/">
          <h1 className="font-headline-md text-headline-md font-bold text-primary">CareerForge AI</h1>
        </Link>
        <p className="font-label-sm text-label-sm text-on-surface-variant">Pro Account</p>
      </div>

      <div className="flex flex-col gap-xs flex-grow">
        {items
          .filter((i) => !i.roles || (role && i.roles.includes(role)))
          .map(({ href, label, icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href as any}
                className={cn(
                  "flex items-center gap-sm px-sm py-xs rounded-lg transition-all font-label-md text-label-md",
                  active
                    ? "bg-primary-container text-on-primary-container font-bold"
                    : "text-on-surface-variant hover:bg-surface-container-high",
                )}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 20 }}>{icon}</span>
                {label}
              </Link>
            );
          })}
      </div>

      <div className="mt-auto space-y-xs">
        <div className="px-sm py-xs rounded-lg bg-surface-container">
          <p className="font-label-sm text-label-sm text-on-surface-variant truncate">
            {user?.full_name ?? "—"}
          </p>
          <p className="font-label-sm text-label-sm text-outline capitalize">{user?.role}</p>
        </div>
        <Link href="/analyzer">
          <button className="w-full py-sm bg-primary text-on-primary rounded-xl font-bold hover:opacity-90 active:scale-95 transition-all font-label-md text-label-md">
            New Analysis
          </button>
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-sm px-sm py-xs rounded-lg text-on-surface-variant hover:bg-surface-container-high transition-all font-label-md text-label-md"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>logout</span>
          Sign out
        </button>
      </div>
    </aside>
  );
}
