import { ServerWakeup } from "@/components/auth/server-wakeup";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-surface flex flex-col">
      <ServerWakeup />
      <div className="flex items-center px-margin h-16 border-b border-outline-variant">
        <span className="font-headline-md text-headline-md font-bold text-primary">CareerForge AI</span>
      </div>
      <div className="flex flex-1 items-center justify-center px-margin py-xl">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </main>
  );
}
