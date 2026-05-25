"use client";

import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";

export function Topbar() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();

  return (
    <header className="fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-md shadow-sm border-b border-outline-variant h-16 flex items-center md:hidden">
      <div className="flex justify-between items-center px-4 w-full">
        <span className="font-headline-md text-headline-md font-bold text-primary">CareerForge AI</span>
        <div className="flex items-center gap-sm">
          <span className="font-label-sm text-label-sm text-on-surface-variant hidden sm:block">
            {user?.full_name ?? "—"}
          </span>
          <button
            onClick={() => { logout(); router.push("/login"); }}
            className="w-10 h-10 rounded-full bg-surface-container border border-outline-variant flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>logout</span>
          </button>
        </div>
      </div>
    </header>
  );
}
