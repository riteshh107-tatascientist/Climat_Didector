import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, getToken, setToken, clearToken, ApiError } from "@/lib/api";
import type { User } from "@/types/api";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string, organization?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    api
      .get<User>("/auth/me")
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const res = await api.post<{ access_token: string }>("/auth/login", { email, password });
    setToken(res.access_token);
    const me = await api.get<User>("/auth/me");
    setUser(me);
  }

  async function signup(email: string, password: string, fullName?: string, organization?: string) {
    await api.post<User>("/auth/signup", {
      email,
      password,
      full_name: fullName || undefined,
      organization: organization || undefined,
    });
    await login(email, password);
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } catch (e) {
      // Logout should always succeed client-side even if the network call
      // fails (token already invalid, offline, etc.)
      if (!(e instanceof ApiError)) throw e;
    } finally {
      clearToken();
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: !!user, login, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
