import { FormEvent, useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const LOGIN_TIMEOUT_MS = 8000;

type LoginMode = "login" | "requestReset" | "setNewPassword";

function getLoginErrorMessage(error: unknown) {
  if (error instanceof DOMException && error.name === "AbortError") {
    return "Backend indisponível. Tente novamente em instantes.";
  }
  if (error instanceof ApiError) {
    if (error.status === 401) return "Credenciais inválidas. Verifique e-mail e senha.";
    if (error.status === 403) return "Você não tem permissão para usar este recurso.";
    if (error.status === 422) return "Dados de login inválidos. Revise e-mail e senha.";
    if (error.status === 429) return "Limite de tentativas atingido. Aguarde alguns instantes e tente novamente.";
    if (error.status >= 500) return "Backend indisponível. Tente novamente em instantes.";
  }
  return "Backend indisponível. Tente novamente em instantes.";
}

function TransitionOverlay() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-xl">
      <div className="flex flex-col items-center gap-4 rounded-[28px] border border-white/10 bg-slate-950/90 px-8 py-10 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.85)]">
        <div className="flex h-24 w-24 items-center justify-center rounded-[28px] border border-white/10 bg-white/5 shadow-lg">
          <img src="/logo.svg" alt="Apoema" className="h-16 w-16" />
        </div>
        <p className="text-lg font-semibold text-slate-100">Carregando módulo...</p>
      </div>
    </div>
  );
}

function LoginBootState() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(34,211,238,0.12),transparent_26%),linear-gradient(180deg,#07111f_0%,#09131f_100%)] p-4">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-96 w-96 animate-pulse rounded-full bg-sky-400/10 blur-3xl delay-1000" />
      </div>

      <div className="z-10 flex flex-col items-center gap-4 rounded-[32px] border border-white/10 bg-slate-950/70 px-8 py-10 shadow-[0_24px_80px_-28px_rgba(0,0,0,0.85)] backdrop-blur-xl">
        <div className="flex h-24 w-24 items-center justify-center rounded-[28px] border border-white/10 bg-white/5 shadow-lg">
          <img src="/logo.svg" alt="Apoema" className="h-16 w-16" />
        </div>
        <div className="text-center">
          <p className="text-xs uppercase tracking-[0.45em] text-slate-400">Apoema</p>
          <p className="mt-2 text-lg font-semibold text-slate-100">Carregando módulo...</p>
        </div>
      </div>
    </main>
  );
}

export function LoginPage() {
  const { token, login, loading, bootError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState<LoginMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    const hash = window.location.hash || "";
    const params = new URLSearchParams(hash.startsWith("#") ? hash.slice(1) : hash);
    if (params.get("type") === "recovery") {
      setMode("setNewPassword");
    }
  }, []);

  if (loading) {
    return <LoginBootState />;
  }

  if (token) {
    return <Navigate to="/apoema/chat" replace />;
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), LOGIN_TIMEOUT_MS);
    try {
      await login(email, password, controller.signal);
      setTransitioning(true);
      window.setTimeout(() => {
        const state = location.state as { from?: { pathname?: string } } | null;
        navigate(state?.from?.pathname || "/apoema/chat", { replace: true });
      }, 3000);
    } catch (submitError) {
      setError(getLoginErrorMessage(submitError));
      setSubmitting(false);
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  async function handleResetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      if (mode === "requestReset") {
        setError("Recuperação de senha indisponível neste ambiente.");
        return;
      }
      if (mode === "setNewPassword") {
        setError("Atualização de senha indisponível neste ambiente.");
        return;
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(34,211,238,0.12),transparent_26%),linear-gradient(180deg,#07111f_0%,#09131f_100%)] p-4">
      {transitioning ? <TransitionOverlay /> : null}

      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-sky-400/10 blur-3xl delay-1000" />
      </div>

      <div className="z-10 w-full max-w-md space-y-8">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-[28px] border border-white/10 bg-white/5 shadow-[0_18px_50px_-24px_rgba(0,0,0,0.85)] backdrop-blur-md">
            <img src="/logo.svg" alt="Apoema" className="h-16 w-16" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-slate-50">Apoema</h2>
          <p className="mt-2 text-slate-400">Painel ENS-Quality</p>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-slate-950/70 p-8 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.8)] backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4">
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">Entrar</p>
              <p className="text-sm text-slate-300">Painel ENS-Quality</p>
            </div>
            <span className="inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-sm">
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              Acesso seguro
            </span>
          </div>

          {mode === "login" ? (
            <form onSubmit={handleLogin} className="mt-8 space-y-6">
              {error ? (
                <div className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{error}</div>
              ) : bootError ? (
                <div className="rounded-2xl border border-amber-400/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">{bootError}</div>
              ) : null}

              <div className="space-y-2">
                <Label htmlFor="email" className="text-slate-200">
                  E-mail
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500 focus-visible:border-cyan-300/40 focus-visible:ring-cyan-300/20"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between gap-4">
                  <Label htmlFor="password" className="text-slate-200">
                    Senha
                  </Label>
                  <button
                    type="button"
                    onClick={() => setMode("requestReset")}
                    className="text-xs text-cyan-200 hover:underline"
                  >
                    Esqueceu a senha?
                  </button>
                </div>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500 focus-visible:border-cyan-300/40 focus-visible:ring-cyan-300/20"
                />
              </div>

              <Button
                type="submit"
                className="w-full rounded-2xl bg-cyan-400 text-slate-950 shadow-[0_18px_40px_-20px_rgba(34,211,238,0.75)] transition-all hover:scale-[1.01] hover:bg-cyan-300"
                disabled={submitting}
              >
                {submitting ? "Entrando..." : "Entrar"}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="mt-8 space-y-6">
              <div className="space-y-2 text-center">
                <h3 className="text-lg font-semibold text-slate-100">
                  {mode === "requestReset" ? "Redefinir senha" : "Definir nova senha"}
                </h3>
                <p className="text-sm text-slate-400">
                  {mode === "requestReset"
                    ? "Enviaremos um link de redefinição para seu e-mail."
                    : "Crie uma nova senha para sua conta."}
                </p>
              </div>

              {mode === "requestReset" ? (
                <div className="space-y-2">
                  <Label htmlFor="reset-email" className="text-slate-200">
                    E-mail
                  </Label>
                  <Input
                    id="reset-email"
                    name="reset-email"
                    type="email"
                    autoComplete="email"
                    placeholder="seu@email.com"
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    required
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                  />
                </div>
              ) : null}

              {mode === "setNewPassword" ? (
                <div className="space-y-2">
                  <Label htmlFor="new-password" className="text-slate-200">
                    Nova senha
                  </Label>
                  <Input
                    id="new-password"
                    name="new-password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    className="border-white/10 bg-white/5 text-slate-50 placeholder:text-slate-500"
                  />
                </div>
              ) : null}

              <div className="flex flex-col gap-3 pt-2">
                <Button
                  type="submit"
                  className="w-full rounded-2xl bg-cyan-400 text-slate-950 transition-all hover:bg-cyan-300"
                  disabled={submitting}
                >
                  {submitting ? "Processando..." : mode === "requestReset" ? "Enviar link de redefinição" : "Salvar nova senha"}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    window.location.hash = "";
                    setMode("login");
                    setNewPassword("");
                  }}
                  className="w-full rounded-2xl text-slate-200 hover:bg-white/5"
                >
                  Voltar para Login
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </main>
  );
}
