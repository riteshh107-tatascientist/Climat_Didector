import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button, Input, Card, CardContent } from "@/components/ui/primitives";
import { ApiError } from "@/lib/api";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      const from = (location.state as { from?: Location })?.from?.pathname || "/app";
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? String(err.detail) : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-subtle px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">
            CG
          </div>
          <h1 className="text-xl font-semibold text-ink">Welcome back</h1>
          <p className="text-sm text-ink-faint">Log in to your ClimateGuard AI account</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <Input
                label="Email" type="email" name="email" autoComplete="email" required
                value={email} onChange={(e) => setEmail(e.target.value)}
              />
              <Input
                label="Password" type="password" name="password" autoComplete="current-password" required
                value={password} onChange={(e) => setPassword(e.target.value)}
              />
              {error && (
                <p role="alert" className="text-sm text-risk-critical">{error}</p>
              )}
              <Button type="submit" className="w-full" isLoading={isLoading}>
                Log in
              </Button>
            </form>
          </CardContent>
        </Card>
        <p className="mt-6 text-center text-sm text-ink-faint">
          Don't have an account?{" "}
          <Link to="/signup" className="font-medium text-brand-700 hover:underline">
            Sign up
          </Link>
        </p>
        <p className="mt-2 text-center text-xs text-ink-faint">
          Judging the platform? You can also{" "}
          <Link to="/demo" className="font-medium text-brand-700 hover:underline">
            try a live demo without an account
          </Link>.
        </p>
      </div>
    </div>
  );
}
