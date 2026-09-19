import { Link } from "react-router-dom";
import { Button } from "@/components/ui/primitives";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <p className="text-5xl font-bold text-brand-700">404</p>
      <h1 className="text-lg font-semibold text-ink">Page not found</h1>
      <p className="max-w-sm text-sm text-ink-faint">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <Link to="/"><Button>Back to home</Button></Link>
    </div>
  );
}
