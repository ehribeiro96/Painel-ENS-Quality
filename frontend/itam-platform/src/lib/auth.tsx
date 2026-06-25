import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, api, configureApiAuth } from "./api";
import type { TokenResponse, User } from "./types";

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
let sharedRefreshRequest: Promise<TokenResponse> | null = null;

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
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [bootError, setBootError] = useState<string | null>(null);
  const tokenRef = useRef<string | null>(null);
  const bootSeqRef = useRef(0);

  function setAccessToken(nextToken: string | null) {
    tokenRef.current = nextToken;
    setTokenState(nextToken);
  }

  function clearSession() {
    setAccessToken(null);
    setUser(null);
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
        setAccessToken(result.access_token);
        setUser(result.user);
        setBootError(null);
        return result.access_token;
      })
      .catch((error: unknown) => {
        if (isAbortError(error)) {
          throw error;
        }
        if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
          clearSession();
          setBootError(null);
          return null;
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
