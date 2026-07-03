import { useMemo, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import {
  Archive,
  ArrowLeftRight,
  Brain,
  FileSignature,
  FileUp,
  LayoutDashboard,
  Menu,
  Package,
  Palette,
  Search,
  Settings2,
  ShieldAlert,
  Sparkles,
  SplitSquareHorizontal,
  TextCursorInput,
  Users,
  Megaphone,
  MessageSquare,
} from "lucide-react";

type NavItem = {
  to: string;
  label: string;
  detail: string;
  icon: LucideIcon;
};

const navigationSections: Array<{ label: string; items: NavItem[] }> = [
  {
    label: "Workspace",
    items: [
      { to: "chat", label: "Chat", icon: MessageSquare, detail: "Centro da operação" },
      { to: "dashboard", label: "Dashboard / Overview", icon: LayoutDashboard, detail: "Resumo executivo" },
      { to: "assets", label: "Ativos", icon: Package, detail: "Inventário" },
      { to: "users", label: "Usuários", icon: Users, detail: "RBAC e perfis" },
      { to: "macros", label: "Macros", icon: TextCursorInput, detail: "Textos operacionais" },
      { to: "imports", label: "Importações", icon: FileUp, detail: "Entrada de dados" },
    ],
  },
  {
    label: "Operação",
    items: [
      { to: "stock", label: "Estoque", icon: Package, detail: "Reserva e disponibilidade" },
      { to: "signatures", label: "Assinaturas", icon: FileSignature, detail: "Fluxos aprovativos" },
      { to: "audit-logs", label: "Auditoria", icon: ShieldAlert, detail: "Rastreabilidade" },
      { to: "rag", label: "RAG / Base", icon: Search, detail: "Consulta e busca" },
      { to: "artifacts", label: "Artefatos", icon: Archive, detail: "Contratos e entregas" },
      { to: "integrations", label: "Integrações", icon: SplitSquareHorizontal, detail: "Adapters e bridges" },
      { to: "settings", label: "Configurações", icon: Settings2, detail: "Tema e políticas" },
      { to: "designer", label: "Designer", icon: Palette, detail: "Fluxos e jobs" },
      { to: "assignments", label: "Movimentações", icon: ArrowLeftRight, detail: "Eventos append-only" },
    ],
  },
];

function shellRouteBase(pathname: string) {
  return pathname.startsWith("/apoema-preview") ? "/apoema-preview" : "/apoema";
}

function ShellNavItem({ routeBase, item }: { routeBase: string; item: NavItem }) {
  const Icon = item.icon;

  return (
    <NavLink
      to={`${routeBase}/${item.to}`}
      className={({ isActive }) => `apoema-rail-nav-item ${isActive ? "is-active" : ""}`}
      aria-label={item.label}
      title={item.label}
    >
      <span className="apoema-rail-nav-icon" aria-hidden="true">
        <Icon size={18} />
      </span>
      <span className="apoema-rail-nav-copy">
        <strong>{item.label}</strong>
        <small>{item.detail}</small>
      </span>
    </NavLink>
  );
}

export function ChatFirstShell() {
  const { pathname } = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const routeBase = useMemo(() => shellRouteBase(pathname), [pathname]);

  return (
    <div className="apoema-root" data-theme="light">
      <div className="apoema-chat-first-root">
        <div className="apoema-chat-first-shell">
          <aside className="apoema-rail" aria-label="Navegação principal do Apoema">
            <div className="apoema-rail-inner">
              <NavLink
                to={`${routeBase}/chat`}
                className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-white/80 shadow-glass ring-1 ring-white/70 transition-transform hover:scale-105"
                title="Apoema"
                aria-label="Ir para o chat principal"
              >
                <img src="/icon-robo.svg" alt="" className="h-11 w-11" aria-hidden="true" />
              </NavLink>

              <NavLink
                to={`${routeBase}/chat`}
                className="apoema-rail-cta apoema-primary-button"
                title="Nova conversa"
                aria-label="Nova conversa"
              >
                <Sparkles size={16} />
                <span>Nova conversa</span>
              </NavLink>

              {navigationSections.map((section) => (
                <section key={section.label} className="apoema-rail-section">
                  <p className="apoema-rail-section-head">{section.label}</p>
                  <div className="apoema-rail-nav" aria-label={section.label}>
                    {section.items.map((item) => (
                      <ShellNavItem key={item.to} routeBase={routeBase} item={item} />
                    ))}
                  </div>
                </section>
              ))}

              <NavLink
                to={`${routeBase}/settings`}
                className="apoema-rail-cta apoema-secondary-button"
                title="Configurações"
                aria-label="Configurações"
              >
                <Settings2 size={16} />
                <span>Configurações</span>
              </NavLink>
            </div>
          </aside>

          <main className="apoema-chat-first-main">
            <header className="apoema-chat-first-topbar">
              <div className="apoema-chat-first-topbar-leading">
                <details className="apoema-mobile-drawer">
                  <summary aria-label="Abrir navegação">
                    <span className="apoema-chat-icon-button" aria-hidden="true">
                      <Menu size={18} />
                    </span>
                    <span>Menu</span>
                  </summary>
                  <div className="apoema-mobile-drawer-panel">
                    <NavLink to={`${routeBase}/chat`} className="apoema-mobile-drawer-cta">
                      <Sparkles size={16} />
                      <span>Nova conversa</span>
                    </NavLink>
                    <div className="apoema-mobile-drawer-grid">
                      {navigationSections.map((section) => (
                        <section key={section.label} className="apoema-rail-section">
                          <p className="apoema-rail-section-head">{section.label}</p>
                          {section.items.map((item) => (
                            <NavLink
                              key={item.to}
                              to={`${routeBase}/${item.to}`}
                              className={({ isActive }) => `apoema-mobile-drawer-item ${isActive ? "is-active" : ""}`}
                            >
                              <span className="apoema-rail-nav-icon" aria-hidden="true">
                                <item.icon size={18} />
                              </span>
                              <span className="min-w-0">
                                <strong className="block truncate">{item.label}</strong>
                                <small className="block truncate">{item.detail}</small>
                              </span>
                            </NavLink>
                          ))}
                        </section>
                      ))}
                    </div>
                  </div>
                </details>

                <div className="glass-surface flex items-center gap-3 rounded-full px-4 py-2 shadow-glass">
                  <img src="/icon-robo.svg" alt="Apoema" className="h-5 w-auto" />
                  <span className="text-sm font-medium text-text-primary">Apoema</span>
                </div>
              </div>

              <div className="apoema-chat-first-topbar-actions">
                <button type="button" className="chat-send-button text-white rounded-xl px-6 shadow-glass hover:scale-105 transition-transform">
                  <Megaphone className="w-4 h-4 mr-2" />
                  Hermes Bridge
                </button>
              </div>
            </header>

            <div className="apoema-chat-first-content">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
