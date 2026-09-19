import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button, Input, Card, CardContent } from "@/components/ui/primitives";
import { ApiError } from "@/lib/api";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [organization, setOrganization] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await signup(email, password, fullName, organization);
      navigate("/app", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-subtle px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">
            CG
          </div>
          <h1 className="text-xl font-semibold text-ink">Create your account</h1>
          <p className="text-sm text-ink-faint">Start tracking climate risk for your region</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <Input label="Full name" name="fullName" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              <Input label="Organization (optional)" name="organization" value={organization} onChange={(e) => setOrganization(e.target.value)} />
              <Input
                label="Email" type="email" name="email" autoComplete="email" required
                value={email} onChange={(e) => setEmail(e.target.value)}
              />
              <Input
                label="Password" type="password" name="password" autoComplete="new-password" required
                value={password} onChange={(e) => setPassword(e.target.value)}
                hint="At least 8 characters, with a letter and a number."
              />
              {error && <p role="alert" className="text-sm text-risk-critical">{error}</p>}
              <Button type="submit" className="w-full" isLoading={isLoading}>
                Create account
              </Button>
            </form>
          </CardContent>
        </Card>
        <p className="mt-6 text-center text-sm text-ink-faint">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-700 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
