import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { LogOut, Search, Users } from "lucide-react";
import { BrandMark } from "@/components/brand/BrandMark";
import { HermesStatusPill } from "@/components/brand/HermesStatusPill";
import { Base44ShellAccent } from "@/components/base44/Base44ShellAccent";
import { Base44StatusBadge } from "@/components/base44/Base44StatusBadge";
import {
  AgentOrbitIcon,
  AuditReportIcon,
  DatabasePulseIcon,
  DocumentBoltIcon,
  HermesCoreIcon,
  NeuralNodeIcon,
  PackageChipIcon,
  RadarCircuitIcon,
  SettingsCircuitIcon,
  ShieldCheckIcon,
  TransferCircuitIcon
} from "@/components/icons/HermesIcons";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { accessModeLabel, canWriteOperationalData } from "@/lib/permissions";
import type { SearchResult } from "@/lib/types";

const nav = [
  { href: "/", label: "Centro de Comando", icon: RadarCircuitIcon },
  { href: "/assets", label: "Inventário", icon: PackageChipIcon },
  { href: "/users", label: "Colaboradores", icon: Users },
  { href: "/assignments", label: "Movimentações", icon: TransferCircuitIcon },
  { href: "/signatures", label: "Assinaturas", icon: ShieldCheckIcon },
  { href: "/macros", label: "Macros ITIL", icon: DocumentBoltIcon },
  { href: "/ai-chat", label: "IA Assistiva", icon: NeuralNodeIcon },
  { href: "/audit-logs", label: "Auditoria", icon: AuditReportIcon },
  { href: "/imports", label: "Importação Lansweeper", icon: DatabasePulseIcon },
  { href: "/settings", label: "Configurações", icon: SettingsCircuitIcon }
];

export function AppShell({ children }: { children: ReactNode }) {
  const { token, user, logout } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const canWrite = canWriteOperationalData(user?.role);

  useEffect(() => {
    if (!token || query.trim().length < 2) {
      setResults([]);
      setSearching(false);
      return;
    }
    const handle = window.setTimeout(() => {
      setSearching(true);
      api
        .globalSearch(token, query.trim())
        .then((response) => setResults(response.items))
        .catch(() => setResults([]))
        .finally(() => setSearching(false));
    }, 250);
    return () => window.clearTimeout(handle);
  }, [query, token]);

  return (
    <div className="shell base44-shell">
      <aside className="sidebar base44-sidebar" aria-label="Menu lateral">
        <Base44ShellAccent
          title="Painel ENS-Quality"
          subtitle="Fonte visual Base44, contratos reais preservados"
        />
        <BrandMark compact={false} />
        <nav className="nav base44-nav" aria-label="Navegação principal">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.href} to={item.href} className={({ isActive }) => (isActive ? "active" : undefined)} end={item.href === "/"}>
                <Icon size={17} aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip" aria-label="Usuário logado">
            <span className="avatar" aria-hidden>{user?.name?.[0] ?? "U"}</span>
            <span className="user-chip-text">
              <strong>{user?.name ?? "Usuário"}</strong>
              <small>{user?.role ?? "OPERADOR"}</small>
            </span>
          </div>
          <button className="logout-link" type="button" onClick={() => void logout()}>
            <LogOut size={16} aria-hidden />
            <span>Sair</span>
          </button>
          <a className="legacy-link" href="/assinaturas/" title="Abrir módulo legado de assinaturas">
            <ShieldCheckIcon size={16} aria-hidden="true" />
            <span>Assinaturas legado</span>
          </a>
        </div>
      </aside>
      <main className="main base44-main">
        <header className="topbar base44-topbar">
          <div className="toolbar global-search base44-global-search" role="search">
            <Search size={17} aria-hidden />
            <input
              className="input search"
              aria-label="Busca global"
              placeholder="Buscar ativo, colaborador, patrimônio ou serial"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            {query.trim().length >= 2 ? (
              <div className="search-results" aria-live="polite">
                {searching ? <div className="search-result muted">Buscando...</div> : null}
                {!searching && results.length === 0 ? <div className="search-result muted">Nenhum resultado</div> : null}
                {results.map((result) => (
                  <Link className="search-result" key={`${result.type}-${result.id}`} to={result.href} onClick={() => setQuery("")}>
                    <strong>{result.title}</strong>
                    <span>{result.subtitle || result.type}</span>
                  </Link>
                ))}
              </div>
            ) : null}
          </div>
          <div className="toolbar topbar-status base44-topbar-status" aria-label="Status da aplicação">
            <HermesStatusPill state="Online">Agente local</HermesStatusPill>
            <HermesStatusPill state="Auditável">Inventário auditável</HermesStatusPill>
            <Base44StatusBadge status={canWrite ? "auditavel" : "leitura"}>{accessModeLabel(user?.role)}</Base44StatusBadge>
            <span className="topbar-user">
              <HermesCoreIcon size={16} aria-hidden="true" />
              <span>
                <strong>{user?.name ?? "Usuário"}</strong>
                <small>{user?.role ?? "OPERADOR"}</small>
              </span>
            </span>
            <button className="logout-link topbar-logout" type="button" onClick={() => void logout()}>
              <LogOut size={16} aria-hidden />
              <span>Sair</span>
            </button>
          </div>
        </header>
        <section className="content">{children}</section>
      </main>
    </div>
  );
}
