import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { LogIn, ShieldCheck, Sparkles } from "lucide-react";

import { Base44PageHeader } from "@/components/base44/Base44PageHeader";
import { Base44ShellAccent } from "@/components/base44/Base44ShellAccent";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import { Base44Surface } from "@/components/base44/Base44Surface";
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
    <main
      className="base44-login-shell"
      style={{
        display: "grid",
        gridTemplateColumns: "var(--base44-login-columns, minmax(0, 1.15fr) minmax(320px, 0.85fr))",
        gap: "22px",
        alignItems: "stretch",
        width: "min(100%, 1280px)",
      }}
    >
      <section className="base44-login-hero" style={{ alignSelf: "stretch" }}>
        <Base44Surface className="base44-login-hero-surface" style={{ height: "100%" }}>
          <Base44ShellAccent
            title="HermesOps Sentinel"
            subtitle="Centro de comando local para inventário, automação controlada, macros ITIL, KCS e auditoria operacional."
          >
            <Base44StatusBadge status="auditavel">Rastreabilidade ativa</Base44StatusBadge>
            <Base44StatusBadge status="online">Agente local</Base44StatusBadge>
          </Base44ShellAccent>
          <div className="base44-login-hero-copy">
            <p className="base44-eyebrow">Acesso ao HermesOps Sentinel</p>
            <h1>Guardião local da infraestrutura</h1>
            <p>
              O acesso operacional usa a autenticação real do Painel ENS-Quality. A camada visual do Base44 só reescreve a experiência, não os contratos.
            </p>
          </div>
          <div className="base44-login-hero-chips">
            <div>
              <Sparkles size={16} aria-hidden="true" />
              <span>Visão Base44 aplicada apenas na apresentação.</span>
            </div>
            <div>
              <ShieldCheck size={16} aria-hidden="true" />
              <span>Auth, permissões e backend continuam os mesmos.</span>
            </div>
          </div>
        </Base44Surface>
      </section>

      <Base44Surface className="base44-login-card" as="form" onSubmit={handleSubmit}>
        <Base44PageHeader
          eyebrow="Entrar"
          title="Painel ENS-Quality"
          description="Use suas credenciais locais para entrar no centro de comando operacional."
        />

        {error ? <div className="base44-inline-alert danger">{error}</div> : null}

        <label className="base44-field">
          <span>E-mail</span>
          <input className="input base44-input" placeholder="E-mail" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>

        <label className="base44-field">
          <span>Senha</span>
          <input className="input base44-input" placeholder="Senha" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>

        <div className="base44-login-footer">
          <button className="button base44-button-primary" type="submit" disabled={submitting}>
            <LogIn size={16} aria-hidden="true" />
            <span>{submitting ? "Entrando..." : "Entrar"}</span>
          </button>
          <p className="base44-login-note">Acesso auditável com rastreabilidade ativa. Nenhum mock do Base44 participa da autenticação.</p>
        </div>
      </Base44Surface>
    </main>
  );
}
