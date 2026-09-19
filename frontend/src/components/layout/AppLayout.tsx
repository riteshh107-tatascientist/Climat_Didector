import { type ReactNode } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, AlertTriangle, MapPin, History, ClipboardList,
  Leaf, Settings, LogOut, Menu, X,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/app", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/app/risk-analysis", label: "Risk Analysis", icon: AlertTriangle },
  { to: "/app/locations", label: "Locations", icon: MapPin },
  { to: "/app/history", label: "History", icon: History },
  { to: "/app/recommendations", label: "Recommendations", icon: ClipboardList },
  { to: "/app/impact", label: "Impact", icon: Leaf },
];

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-1 flex-col gap-1 px-3">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              isActive
                ? "bg-brand-50 text-brand-800"
                : "text-ink-muted hover:bg-surface-muted hover:text-ink"
            )
          }
        >
          <Icon className="h-[18px] w-[18px]" />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

function BrandMark() {
  return (
    <div className="flex items-center gap-2 px-4 py-4">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-sm font-bold text-white">
        CG
      </div>
      <span className="text-[15px] font-semibold text-ink">ClimateGuard</span>
    </div>
  );
}

export function AppLayout(): ReactNode {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <div className="flex min-h-screen bg-surface-subtle">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-ink/8 bg-surface md:flex">
        <BrandMark />
        <NavItems />
        <div className="border-t border-ink/8 p-3">
          <NavLink
            to="/app/profile"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium",
                isActive ? "bg-brand-50 text-brand-800" : "text-ink-muted hover:bg-surface-muted hover:text-ink"
              )
            }
          >
            <Settings className="h-[18px] w-[18px]" />
            Profile & Settings
          </NavLink>
          <div className="mt-1 flex items-center justify-between rounded-lg px-3 py-2">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-ink">{user?.full_name || user?.email}</p>
              <p className="truncate text-xs text-ink-faint">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              aria-label="Log out"
              className="shrink-0 rounded-md p-1.5 text-ink-faint hover:bg-surface-muted hover:text-risk-critical"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile top bar */}
      <div className="fixed inset-x-0 top-0 z-30 flex h-14 items-center justify-between border-b border-ink/8 bg-surface px-4 md:hidden">
        <BrandMark />
        <button onClick={() => setMobileMenuOpen(true)} aria-label="Open menu" className="p-2">
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {/* Mobile menu overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/40 md:hidden" onClick={() => setMobileMenuOpen(false)}>
          <div
            className="absolute left-0 top-0 flex h-full w-72 flex-col bg-surface"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <BrandMark />
              <button onClick={() => setMobileMenuOpen(false)} aria-label="Close menu" className="mr-4 p-2">
                <X className="h-5 w-5" />
              </button>
            </div>
            <NavItems onNavigate={() => setMobileMenuOpen(false)} />
            <div className="border-t border-ink/8 p-3">
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-risk-critical hover:bg-risk-critical/5"
              >
                <LogOut className="h-[18px] w-[18px]" />
                Log out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="min-w-0 flex-1 pb-16 pt-14 md:pb-0 md:pt-0">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>

      {/* Mobile bottom nav */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-ink/8 bg-surface md:hidden">
        {NAV_ITEMS.slice(0, 5).map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] font-medium",
                isActive ? "text-brand-700" : "text-ink-faint"
              )
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
