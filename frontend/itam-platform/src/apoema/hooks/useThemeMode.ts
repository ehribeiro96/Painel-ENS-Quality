import { useEffect, useMemo, useState } from "react";
import type { ResolvedTheme, ThemeMode } from "../types";

const STORAGE_KEY = "apoema.theme-mode";

function readStoredTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "auto";
  }

  const value = window.localStorage.getItem(STORAGE_KEY);
  return value === "light" || value === "dark" || value === "auto" ? value : "auto";
}

function getSystemTheme(): ResolvedTheme {
  if (typeof window === "undefined") {
    return "light";
  }

  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function useThemeMode() {
  const [mode, setMode] = useState<ThemeMode>(readStoredTheme);
  const [systemTheme, setSystemTheme] = useState<ResolvedTheme>(getSystemTheme);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (event: MediaQueryListEvent) => {
      setSystemTheme(event.matches ? "dark" : "light");
    };

    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, mode);
  }, [mode]);

  useEffect(() => {
    const root = document.documentElement;
    const resolved = mode === "auto" ? systemTheme : mode;
    root.dataset.apoemaTheme = resolved;
    root.style.colorScheme = resolved;
  }, [mode, systemTheme]);

  const resolvedTheme = useMemo<ResolvedTheme>(() => {
    return mode === "auto" ? systemTheme : mode;
  }, [mode, systemTheme]);

  return {
    mode,
    setMode,
    resolvedTheme
  };
}
