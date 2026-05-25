"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { authService } from "@/services/auth";
import { useAuthStore } from "@/store/auth";

const schema = z.object({
  full_name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(["user", "recruiter"]).default("user"),
});
type FormValues = z.infer<typeof schema>;

export function RegisterForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: "user" },
  });
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();

  async function onSubmit(values: FormValues) {
    setSubmitting(true);
    try {
      const tokens = await authService.register(values);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await authService.me();
      setUser(me);
      toast.success("Account created");
      router.push("/dashboard");
    } catch (e: any) {
      toast.error(e?.response?.data?.message ?? "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">Full name</label>
        <Input {...register("full_name")} />
        {errors.full_name && <p className="mt-1 text-xs text-error">{errors.full_name.message}</p>}
      </div>
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">Email</label>
        <Input type="email" {...register("email")} />
        {errors.email && <p className="mt-1 text-xs text-error">{errors.email.message}</p>}
      </div>
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">Password</label>
        <Input type="password" {...register("password")} />
        {errors.password && <p className="mt-1 text-xs text-error">{errors.password.message}</p>}
      </div>
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">I am a</label>
        <select
          {...register("role")}
          className="h-11 w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-4 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition"
        >
          <option value="user">Candidate</option>
          <option value="recruiter">Recruiter</option>
        </select>
      </div>
      <Button type="submit" loading={submitting} className="w-full">Create account</Button>
    </form>
  );
}
