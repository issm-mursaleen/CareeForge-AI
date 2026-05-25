"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function AdminPage() {
  const { data } = useQuery({
    queryKey: ["admin-overview"],
    queryFn: async () => (await api.get("/admin/overview")).data,
  });
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">Admin</h1>
        <p className="text-slate-400">Platform health, usage, and AI cost.</p>
      </header>
      <div className="grid gap-4 md:grid-cols-4">
        <Stat label="Users" value={data?.total_users ?? 0} />
        <Stat label="Resumes" value={data?.total_resumes ?? 0} />
        <Stat label="AI calls" value={data?.total_ai_calls ?? 0} />
        <Stat label="Cost (USD)" value={`$${(data?.estimated_cost_usd ?? 0).toFixed(4)}`} />
      </div>
      <Card>
        <CardTitle>Users by role</CardTitle>
        <CardDescription>Membership breakdown.</CardDescription>
        <ul className="mt-4 space-y-2 text-sm">
          {data?.users_by_role && Object.entries(data.users_by_role).map(([role, n]) => (
            <li key={role} className="flex justify-between border-b border-white/[0.06] py-2">
              <span className="capitalize">{role}</span><span>{n as number}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardDescription>{label}</CardDescription>
      <div className="mt-2 text-3xl font-bold">{value}</div>
    </Card>
  );
}
