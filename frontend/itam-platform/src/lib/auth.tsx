import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, api, configureApiAuth } from "./api";
import type { TokenResponse, User } from "./types";

type ApoemaProfile = {
  id: string;
  role: "user" | "admin" | "broker" | "owner" | "tenant";
  full_name?: string | null;
  email?: string | null;
  updated_at?: string | null;
  created_at?: string | null;
  avatar_url?: string | null;
};

type ApoemaSession = {
  access_token: string;
  token_type: string;
  user: User;
} | null;

type AuthContextValue = {
  token: string | null;
  session: ApoemaSession;
  user: User | null;
  profile: ApoemaProfile | null;
  loading: boolean;
  bootError: string | null;
  isAdmin: boolean;
  login: (email: string, password: string, signal?: AbortSignal) => Promise<void>;
  logout: () => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const AUTH_BOOT_TIMEOUT_MS = 8000;
const AUTH_SESSION_STORAGE_KEY = "apoema.auth.session";
let sharedRefreshRequest: Promise<TokenResponse> | null = null;

function readStoredSession(): { token: string | null; user: User | null } {
  if (typeof window === "undefined") {
    return { token: null, user: null };
  }
  try {
    const raw = window.localStorage.getItem(AUTH_SESSION_STORAGE_KEY);
    if (!raw) {
      return { token: null, user: null };
    }
    const parsed = JSON.parse(raw) as { token?: string | null; user?: User | null };
    return {
      token: parsed.token ?? null,
      user: parsed.user ?? null,
    };
  } catch {
    return { token: null, user: null };
  }
}

function storeSession(token: string | null, user: User | null) {
  if (typeof window === "undefined") {
    return;
  }
  if (!token || !user) {
    window.localStorage.removeItem(AUTH_SESSION_STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(AUTH_SESSION_STORAGE_KEY, JSON.stringify({ token, user }));
}

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}

function isBootUnavailableError(error: unknown) {
  if (isAbortError(error)) {
    return true;
  }
  if (!(error instanceof ApiError)) {
    return true;
  }
  return error.status >= 500;
}

function requestRefresh(signal?: AbortSignal) {
  if (!signal && sharedRefreshRequest) {
    return sharedRefreshRequest;
  }
  const refreshRequest = api.refresh({ signal }).finally(() => {
    if (sharedRefreshRequest === refreshRequest) {
      sharedRefreshRequest = null;
    }
  });
  if (!signal) {
    sharedRefreshRequest = refreshRequest;
  }
  return refreshRequest;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const storedSession = readStoredSession();
  const [token, setTokenState] = useState<string | null>(storedSession.token);
  const [user, setUser] = useState<User | null>(storedSession.user);
  const [loading, setLoading] = useState(true);
  const [bootError, setBootError] = useState<string | null>(null);
  const tokenRef = useRef<string | null>(storedSession.token);
  const bootSeqRef = useRef(0);

  function setAccessToken(nextToken: string | null) {
    tokenRef.current = nextToken;
    setTokenState(nextToken);
  }

  function setSession(nextToken: string | null, nextUser: User | null) {
    setAccessToken(nextToken);
    setUser(nextUser);
    storeSession(nextToken, nextUser);
  }

  function clearSession() {
    setSession(null, null);
  }

  async function refreshSession(signal?: AbortSignal) {
    const controller = new AbortController();
    const abortFromCaller = () => controller.abort();
    if (signal) {
      if (signal.aborted) {
        controller.abort();
      } else {
        signal.addEventListener("abort", abortFromCaller, { once: true });
      }
    }
    const timeoutId = signal ? window.setTimeout(() => controller.abort(), AUTH_BOOT_TIMEOUT_MS) : null;
    const refreshPromise = requestRefresh(signal ? controller.signal : undefined)
      .then((result) => {
        setSession(result.access_token, result.user);
        setBootError(null);
        return result.access_token;
      })
      .catch((error: unknown) => {
        if (isAbortError(error)) {
          throw error;
        }
        if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
          if (!tokenRef.current) {
            clearSession();
          }
          setBootError(null);
          return tokenRef.current;
        }
        if (isBootUnavailableError(error)) {
          setBootError("Backend indisponível. O formulário de login continua disponível.");
        }
        throw error;
      })
      .finally(() => {
        if (timeoutId !== null) {
          window.clearTimeout(timeoutId);
        }
        if (signal) {
          signal.removeEventListener("abort", abortFromCaller);
        }
      });
    return refreshPromise;
  }

  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const bootSeq = ++bootSeqRef.current;
    configureApiAuth({
      refreshAccessToken: refreshSession,
      handleUnauthorized: clearSession
    });
    setLoading(true);
    refreshSession()
      .then(() => {
        if (active && bootSeq === bootSeqRef.current) {
          setLoading(false);
        }
      })
      .catch((error: unknown) => {
        if (active && bootSeq === bootSeqRef.current && !isAbortError(error)) {
          clearSession();
          setLoading(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  async function performLogout() {
    await api.logout(tokenRef.current).catch(() => undefined);
    clearSession();
    setBootError(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      session: token && user ? { access_token: token, token_type: "bearer", user } : null,
      user,
      profile: user
        ? {
            id: user.id,
            role: user.role === "ADMIN" ? "admin" : user.role === "MANAGER" ? "owner" : "user",
            full_name: user.name,
            email: user.email,
            created_at: user.created_at,
            updated_at: user.updated_at,
          }
        : null,
      loading,
      bootError,
      isAdmin: user?.role === "ADMIN" || user?.role === "MANAGER",
      async login(email: string, password: string, signal?: AbortSignal) {
        const result = await api.login(email, password, { signal });
        setSession(result.access_token, result.user);
        setBootError(null);
      },
      logout: performLogout,
      signOut: performLogout
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
