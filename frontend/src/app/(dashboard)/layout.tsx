import { AuthGuard } from "@/components/dashboard/auth-guard";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Topbar } from "@/components/dashboard/topbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-surface">
        <Sidebar />
        {/* Mobile topbar */}
        <Topbar />
        {/* Desktop top bar (logout visible on desktop too) */}
        <DesktopTopbar />
        <main className="flex-1 md:ml-64 pt-20 md:pt-10 px-gutter pb-32 md:pb-10 min-h-screen">
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}

function DesktopTopbar() {
  return (
    <div className="hidden md:block" suppressHydrationWarning>
      {/* Logout is accessible from sidebar on desktop; topbar only shows on mobile */}
    </div>
  );
}
