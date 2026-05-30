import { AuthGuard } from "@/components/dashboard/auth-guard";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Topbar } from "@/components/dashboard/topbar";
import { BottomNav } from "@/components/dashboard/bottom-nav";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-surface">
        {/* Desktop sidebar */}
        <Sidebar />

        {/* Mobile top bar + slide-out drawer */}
        <Topbar />

        {/* Mobile bottom navigation */}
        <BottomNav />

        {/* Main content */}
        <main className="flex-1 md:ml-64 pt-20 md:pt-10 px-4 md:px-gutter pb-24 md:pb-10 min-h-screen">
          <div className="page-animate max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
