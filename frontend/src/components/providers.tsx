"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { Toaster, toast } from "sonner";
import { api, clearTokens, getStoredTokens, storeTokens, type TokenPair } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = async () => {
    const response = await api.get<User>("/auth/me");
    setUser(response.data);
  };

  useEffect(() => {
    const init = async () => {
      try {
        if (getStoredTokens()) {
          await refreshMe();
        }
      } catch {
        clearTokens();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    void init();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login: async (email: string, password: string) => {
        const response = await api.post<TokenPair>("/auth/login", { email, password });
        storeTokens(response.data);
        await refreshMe();
        toast.success("Signed in");
      },
      logout: () => {
        clearTokens();
        setUser(null);
        toast.message("Signed out");
      },
      refreshMe
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient());
  return (
    <QueryClientProvider client={client}>
      <AuthProvider>
        {children}
        <Toaster richColors position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  );
}
