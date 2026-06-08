import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { api, configureApiAuth } from "./api";
import type { User } from "./types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const tokenRef = useRef<string | null>(null);
  const refreshPromiseRef = useRef<Promise<string | null> | null>(null);

  function setAccessToken(nextToken: string | null) {
    tokenRef.current = nextToken;
    setTokenState(nextToken);
  }

  function clearSession() {
    setAccessToken(null);
    setUser(null);
  }

  async function refreshSession() {
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }
    refreshPromiseRef.current = api
      .refresh()
      .then((result) => {
        setAccessToken(result.access_token);
        setUser(result.user);
        return result.access_token;
      })
      .catch(() => {
        clearSession();
        return null;
      })
      .finally(() => {
        refreshPromiseRef.current = null;
      });
    return refreshPromiseRef.current;
  }

  useEffect(() => {
    let active = true;
    configureApiAuth({
      refreshAccessToken: refreshSession,
      handleUnauthorized: clearSession
    });
    setLoading(true);
    refreshSession()
      .then(() => {
        if (active) {
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          clearSession();
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      loading,
      async login(email: string, password: string) {
        const result = await api.login(email, password);
        setAccessToken(result.access_token);
        setUser(result.user);
      },
      async logout() {
        await api.logout(tokenRef.current).catch(() => undefined);
        clearSession();
      }
    }),
    [loading, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
