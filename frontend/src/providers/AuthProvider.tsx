"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";

interface User {
  id: string;
  email: string;
  fullName?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "ApplyBots_access_token";
const REFRESH_KEY = "ApplyBots_refresh_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const getTokens = useCallback(() => {
    if (typeof window === "undefined") return { access: null, refresh: null };
    return {
      access: localStorage.getItem(TOKEN_KEY),
      refresh: localStorage.getItem(REFRESH_KEY),
    };
  }, []);

  const setTokens = useCallback((access: string, refresh: string) => {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  }, []);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }, []);

  const fetchUser = useCallback(async (token: string) => {
    try {
      console.log("[Auth] Fetching user with token:", token ? `${token.substring(0, 20)}...` : "NO TOKEN");
      
      const response = await fetch("/api/v1/profile", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
      });

      console.log("[Auth] Profile response status:", response.status);

      if (response.ok) {
        const profile = await response.json();
        console.log("[Auth] Profile loaded:", profile.user_id);
        setUser({
          id: profile.user_id,
          email: profile.email || "",
          fullName: profile.full_name,
        });
      } else {
        const errorText = await response.text();
        console.log("[Auth] Profile error:", errorText);
        clearTokens();
        setUser(null);
      }
    } catch (err) {
      console.error("[Auth] Fetch error:", err);
      clearTokens();
      setUser(null);
    }
  }, [clearTokens]);

  useEffect(() => {
    const initAuth = async () => {
      const { access } = getTokens();
      if (access) {
        await fetchUser(access);
      }
      setIsLoading(false);
    };

    initAuth();
  }, [fetchUser, getTokens]);

  const login = async (email: string, password: string) => {
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);
    await fetchUser(data.access_token);
    router.push("/dashboard");
  };

  const signup = async (email: string, password: string, fullName?: string) => {
    const response = await fetch("/api/v1/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Signup failed");
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);
    await fetchUser(data.access_token);
    router.push("/dashboard/profile");
  };

  const logout = async () => {
    const { access } = getTokens();
    if (access) {
      try {
        await fetch("/api/v1/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${access}` },
        });
      } catch {
        // Ignore logout errors
      }
    }
    clearTokens();
    setUser(null);
    router.push("/login");
  };

  const refreshToken = async () => {
    const { refresh } = getTokens();
    if (!refresh) {
      clearTokens();
      setUser(null);
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });

      if (response.ok) {
        const data = await response.json();
        setTokens(data.access_token, data.refresh_token);
      } else {
        clearTokens();
        setUser(null);
      }
    } catch {
      clearTokens();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, signup, logout, refreshToken }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
