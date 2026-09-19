import { useAuth } from "@/context/AuthContext";
import { Card, CardContent, CardHeader, CardTitle, Badge } from "@/components/ui/primitives";

export default function Profile() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Profile & Settings</h1>
        <p className="text-sm text-ink-faint">Your account details.</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Account</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex justify-between border-b border-ink/8 pb-3">
            <span className="text-ink-faint">Name</span>
            <span className="text-ink">{user.full_name || "—"}</span>
          </div>
          <div className="flex justify-between border-b border-ink/8 pb-3">
            <span className="text-ink-faint">Email</span>
            <span className="text-ink">{user.email}</span>
          </div>
          <div className="flex justify-between border-b border-ink/8 pb-3">
            <span className="text-ink-faint">Organization</span>
            <span className="text-ink">{user.organization || "—"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-ink-faint">Role</span>
            <Badge variant="brand">{user.role}</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
