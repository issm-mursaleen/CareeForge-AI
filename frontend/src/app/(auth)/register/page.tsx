import Link from "next/link";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RegisterForm } from "@/components/auth/register-form";

export default function RegisterPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Create your CareerForge AI account</CardTitle>
        <CardDescription>Free for candidates. No credit card required.</CardDescription>
      </CardHeader>
      <RegisterForm />
      <p className="mt-6 text-center font-body-md text-body-md text-on-surface-variant">
        Already have an account?{" "}
        <Link className="text-primary hover:underline font-bold" href="/login">
          Sign in
        </Link>
      </p>
    </Card>
  );
}
