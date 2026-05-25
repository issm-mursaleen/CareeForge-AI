import Link from "next/link";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Sign in to CareerForge AI</CardTitle>
        <CardDescription>Use your email to access your dashboard.</CardDescription>
      </CardHeader>
      <LoginForm />
      <p className="mt-6 text-center font-body-md text-body-md text-on-surface-variant">
        New here?{" "}
        <Link className="text-primary hover:underline font-bold" href="/register">
          Create an account
        </Link>
      </p>
    </Card>
  );
}
