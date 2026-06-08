import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Activity, ClipboardList, Gauge, Import, Link2, LogOut, MessageSquareText, Monitor, Search, Shield, ShieldCheck, Signature, Users } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { enableAiChat } from "@/lib/features";
import type { SearchResult } from "@/lib/types";

const nav = [
  { href: "/", label: "Dashboard", icon: Gauge },
  { href: "/assets", label: "Ativos", icon: Monitor },
  { href: "/users", label: "Colaboradores", icon: Users },
  { href: "/assignments", label: "Atribuições", icon: Link2 },
  { href: "/signatures", label: "Assinaturas", icon: Signature },
  { href: "/macros", label: "Macros", icon: MessageSquareText },
  { href: "/ai-chat", label: "IA Chat", icon: MessageSquareText },
  { href: "/audit-logs", label: "Auditoria", icon: ClipboardList },
  { href: "/imports", label: "Importar/Exportar", icon: Import }
];

export function AppShell({ children }: { children: ReactNode }) {
  const { token, user, logout } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

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
    <div className="shell">
      <aside className="sidebar" aria-label="Menu lateral">
        <div className="brand-block">
          <div className="brand-mark"><Shield size={22} aria-hidden /></div>
          <div>
            <strong>Funenseg</strong>
            <span>Inventário TI</span>
          </div>
        </div>
        <nav className="nav" aria-label="Navegação principal">
          {nav.filter((item) => item.href !== "/ai-chat" || enableAiChat || !enableAiChat).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.href} to={item.href} className={({ isActive }) => (isActive ? "active" : undefined)} end={item.href === "/"}>
                <Icon size={17} aria-hidden />
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
            <ShieldCheck size={16} aria-hidden />
            <span>Assinaturas legado</span>
          </a>
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div className="toolbar global-search" role="search">
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
          <div className="toolbar topbar-status" aria-label="Status da aplicação">
            <Activity size={17} aria-hidden />
            <span>ENS ITAM Platform</span>
          </div>
        </header>
        <section className="content">{children}</section>
      </main>
    </div>
  );
}
