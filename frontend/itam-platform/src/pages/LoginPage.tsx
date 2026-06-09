import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { BrandMark } from "@/components/brand/BrandMark";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { SentinelHero } from "@/components/brand/SentinelHero";
import { useAuth } from "@/lib/auth";

export function LoginPage() {
  const { token, login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (loading) {
    return <main className="screen-center">Validando sessao...</main>;
  }

  if (token) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      const state = location.state as { from?: { pathname?: string } } | null;
      navigate(state?.from?.pathname || "/", { replace: true });
    } catch {
      setError("Credenciais invalidas ou usuario sem senha local configurada.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-screen">
      <section className="login-hero">
        <SentinelHero
          chips={(
            <>
              <HermesStatusPill state="Online">Agente local</HermesStatusPill>
              <HermesStatusPill state="Auditável">Rastreabilidade ativa</HermesStatusPill>
            </>
          )}
          description="Centro de comando local para inventário, automação controlada, macros ITIL, KCS e auditoria operacional."
          eyebrow="Acesso ao HermesOps Sentinel"
          subtitle="Guardião local da infraestrutura"
          title="HermesOps Sentinel"
        />
      </section>
      <form className="card login-card" onSubmit={handleSubmit}>
        <BrandMark compact subtitle="Guardião local da infraestrutura" title="HermesOps Sentinel" />
        <p className="login-copy">Acesso operacional com rastreabilidade. Use suas credenciais locais para entrar no centro de comando.</p>
        {error ? <div className="alert danger">{error}</div> : null}
        <input className="input" placeholder="E-mail" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        <input className="input" placeholder="Senha" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        <button className="button" type="submit" disabled={submitting}>{submitting ? "Entrando..." : "Entrar"}</button>
      </form>
    </main>
  );
}
