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
  email: z.string().email(),
  password: z.string().min(8, "Min 8 characters"),
});
type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();

  async function onSubmit(values: FormValues) {
    setSubmitting(true);
    try {
      const tokens = await authService.login(values);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await authService.me();
      setUser(me);
      toast.success(`Welcome back, ${me.full_name}`);
      router.push("/dashboard");
    } catch (e: any) {
      console.error("Login failed with error:", e);
      toast.error(e?.response?.data?.message ?? e?.message ?? "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">Email</label>
        <Input type="email" placeholder="you@careerforge.ai" {...register("email")} />
        {errors.email && <p className="mt-1 text-xs text-error">{errors.email.message}</p>}
      </div>
      <div>
        <label className="mb-2 block font-label-md text-label-md text-on-surface-variant">Password</label>
        <Input type="password" placeholder="••••••••" {...register("password")} />
        {errors.password && <p className="mt-1 text-xs text-error">{errors.password.message}</p>}
      </div>
      <Button type="submit" loading={submitting} className="w-full">Sign in</Button>
    </form>
  );
}
