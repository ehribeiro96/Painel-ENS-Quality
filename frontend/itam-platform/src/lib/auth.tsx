import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, api, configureApiAuth } from "./api";
import type { User } from "./types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  loading: boolean;
  bootError: string | null;
  login: (email: string, password: string, signal?: AbortSignal) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const AUTH_BOOT_TIMEOUT_MS = 8000;

function isBootUnavailableError(error: unknown) {
  if (error instanceof DOMException && error.name === "AbortError") {
    return true;
  }
  if (!(error instanceof ApiError)) {
    return true;
  }
  return error.status >= 500;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [bootError, setBootError] = useState<string | null>(null);
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

  async function refreshSession(signal?: AbortSignal) {
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }
    const controller = new AbortController();
    const abortFromCaller = () => controller.abort();
    if (signal) {
      if (signal.aborted) {
        controller.abort();
      } else {
        signal.addEventListener("abort", abortFromCaller, { once: true });
      }
    }
    const timeoutId = window.setTimeout(() => controller.abort(), AUTH_BOOT_TIMEOUT_MS);
    refreshPromiseRef.current = api
      .refresh({ signal: controller.signal })
      .then((result) => {
        setAccessToken(result.access_token);
        setUser(result.user);
        setBootError(null);
        return result.access_token;
      })
      .catch((error: unknown) => {
        clearSession();
        if (isBootUnavailableError(error)) {
          setBootError("Backend indisponível. O formulário de login continua disponível.");
        } else {
          setBootError(null);
        }
        return null;
      })
      .finally(() => {
        window.clearTimeout(timeoutId);
        if (signal) {
          signal.removeEventListener("abort", abortFromCaller);
        }
        refreshPromiseRef.current = null;
      });
    return refreshPromiseRef.current;
  }

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    configureApiAuth({
      refreshAccessToken: refreshSession,
      handleUnauthorized: clearSession
    });
    setLoading(true);
    refreshSession(controller.signal)
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
      controller.abort();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      loading,
      bootError,
      async login(email: string, password: string, signal?: AbortSignal) {
        const result = await api.login(email, password, { signal });
        setAccessToken(result.access_token);
        setUser(result.user);
        setBootError(null);
      },
      async logout() {
        await api.logout(tokenRef.current).catch(() => undefined);
        clearSession();
        setBootError(null);
      }
    }),
    [bootError, loading, token, user]
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
