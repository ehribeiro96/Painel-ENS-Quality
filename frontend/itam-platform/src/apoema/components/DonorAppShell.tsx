import type { CSSProperties } from "react";
import { useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  Bot,
  Database,
  FileDown,
  FileCode2,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  MessageSquarePlus,
  PlugZap,
  ScanSearch,
  Settings,
  ShieldCheck,
  Signature,
  Users,
  Warehouse,
  Workflow,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

type NavItem = {
  label: string;
  to: string;
  icon: typeof LayoutDashboard;
};

const navItems: Array<{ label: string; items: NavItem[] }> = [
  {
    label: "Chat",
    items: [
      { label: "Novo chat", to: "/apoema/chat?new=1", icon: MessageSquarePlus },
      { label: "Chat / Histórico", to: "/apoema/chat", icon: Bot },
    ],
  },
  {
    label: "Operação",
    items: [
      { label: "Dashboard / Overview", to: "/apoema/dashboard", icon: LayoutDashboard },
      { label: "Ativos", to: "/apoema/assets", icon: Database },
      { label: "Usuários", to: "/apoema/users", icon: Users },
      { label: "Movimentações", to: "/apoema/assignments", icon: ListChecks },
      { label: "Estoque", to: "/apoema/stock", icon: Warehouse },
    ],
  },
  {
    label: "Automação",
    items: [
      { label: "Macros", to: "/apoema/macros", icon: Workflow },
      { label: "Importações", to: "/apoema/imports", icon: FileDown },
      { label: "Assinaturas", to: "/apoema/signatures", icon: Signature },
    ],
  },
  {
    label: "Governança",
    items: [
      { label: "Auditoria", to: "/apoema/audit-logs", icon: ShieldCheck },
      { label: "RAG / Base", to: "/apoema/rag", icon: ScanSearch },
      { label: "Artefatos", to: "/apoema/artifacts", icon: FileCode2 },
      { label: "Integrações", to: "/apoema/integrations", icon: PlugZap },
      { label: "Configurações", to: "/apoema/settings", icon: Settings },
    ],
  },
];

function routeTitle(pathname: string) {
  const normalized = pathname.replace(/\/+$/, "");
  if (normalized === "/apoema" || normalized === "/apoema/chat" || normalized === "/apoema/ai-chat") {
    return { title: "Chat IA", subtitle: "Hermes real, histórico persistente e anexos honestos" };
  }
  if (normalized === "/apoema/dashboard") return { title: "Dashboard", subtitle: "Visão operacional do painel" };
  if (normalized === "/apoema/assets") return { title: "Ativos", subtitle: "Inventário e estado atual" };
  if (normalized === "/apoema/users") return { title: "Usuários", subtitle: "Cadastro operacional e vínculos" };
  if (normalized === "/apoema/macros") return { title: "Macros", subtitle: "Templates e geração controlada" };
  if (normalized === "/apoema/imports") return { title: "Importações", subtitle: "Upload guiado, revisão e aplicação" };
  if (normalized === "/apoema/assignments") return { title: "Movimentações", subtitle: "Vínculos e histórico auditável" };
  if (normalized === "/apoema/stock") return { title: "Estoque", subtitle: "Disponibilidade por status" };
  if (normalized === "/apoema/signatures") return { title: "Assinaturas", subtitle: "Modelos corporativos" };
  if (normalized === "/apoema/audit-logs") return { title: "Auditoria", subtitle: "Eventos e rastreabilidade" };
  if (normalized === "/apoema/rag") return { title: "RAG / Base", subtitle: "Busca e contexto operacional" };
  if (normalized === "/apoema/artifacts") return { title: "Artefatos", subtitle: "Arquivos, previews e downloads" };
  if (normalized === "/apoema/integrations") return { title: "Integrações", subtitle: "Adaptadores e cobertura" };
  if (normalized === "/apoema/settings") return { title: "Configurações", subtitle: "Tema, segurança e densidade" };
  return { title: "Apoema", subtitle: "Painel ENS-Quality" };
}

function isActiveRoute(currentPath: string, target: string) {
  const targetPath = target.split("?")[0];
  if (targetPath === "/apoema/chat") {
    return currentPath === "/apoema" || currentPath.startsWith("/apoema/chat") || currentPath.startsWith("/apoema/ai-chat");
  }
  return currentPath === targetPath || currentPath.startsWith(`${targetPath}/`);
}

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const location = useLocation();
  const currentPath = location.pathname;
  const currentFullPath = `${location.pathname}${location.search}`;

  return (
    <div className="flex h-full min-h-0 flex-col rounded-[28px] border border-white/10 bg-slate-950/75 p-3 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.8)] backdrop-blur-xl">
      <div className="flex items-center gap-3 rounded-[22px] border border-white/10 bg-white/5 px-3 py-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-300/25">
          <img src="/logo.svg" alt="Apoema" className="h-7 w-7" />
        </div>
        <div className="min-w-0 overflow-hidden transition-all duration-300 group-hover/sidebar:opacity-100 group-focus-within/sidebar:opacity-100 lg:max-w-0 lg:opacity-0 lg:group-hover/sidebar:max-w-[180px] lg:group-focus-within/sidebar:max-w-[180px]">
          <p className="text-[11px] uppercase tracking-[0.32em] text-slate-400">Apoema</p>
          <strong className="block truncate text-sm text-slate-100">Painel ENS-Quality</strong>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2 lg:justify-center">
        <Button asChild className="h-10 w-full justify-start rounded-2xl bg-cyan-400 px-3 text-slate-950 hover:bg-cyan-300 lg:w-10 lg:justify-center">
          <Link to="/apoema/chat?new=1" onClick={onNavigate} aria-label="Novo chat">
            <MessageSquarePlus className="h-4 w-4 shrink-0" />
            <span className="truncate lg:hidden xl:inline-flex">Novo chat</span>
          </Link>
        </Button>
      </div>

      <nav
        className={cn(
          "mt-4 min-h-0 flex-1 space-y-4 overflow-y-auto pr-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden",
          "lg:pr-2",
        )}
        aria-label="Navegação principal"
      >
        {navItems.map((group) => (
          <section key={group.label} className="space-y-2">
            <div className="flex items-center justify-between px-2">
              <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500 transition-all duration-300 group-hover/sidebar:text-slate-300 group-focus-within/sidebar:text-slate-300 lg:max-w-0 lg:overflow-hidden lg:opacity-0 lg:group-hover/sidebar:max-w-[120px] lg:group-focus-within/sidebar:max-w-[120px]">
                {group.label}
              </p>
              <span className="hidden h-px flex-1 bg-white/10 lg:block" />
            </div>
            <div className="space-y-1">
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = item.to.includes("?")
                  ? currentFullPath === item.to
                  : isActiveRoute(currentPath, item.to) && currentFullPath !== "/apoema/chat?new=1";
                return (
                  <NavLink
                    key={`${group.label}:${item.label}:${item.to}`}
                    to={item.to}
                    onClick={onNavigate}
                    className={cn(
                      "flex items-center gap-3 rounded-2xl border px-3 py-3 text-sm transition-all duration-300",
                      "border-transparent text-slate-300 hover:border-white/10 hover:bg-white/6 hover:text-white",
                      active ? "border-cyan-300/20 bg-cyan-400/12 text-cyan-100 shadow-[0_10px_30px_-20px_rgba(34,211,238,0.85)]" : "bg-transparent",
                      "lg:justify-start",
                    )}
                  >
                    <span className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl ring-1 ring-inset", active ? "bg-cyan-300/15 ring-cyan-200/20" : "bg-white/5 ring-white/10")}>
                      <Icon className={cn("h-4 w-4", active ? "text-cyan-100" : "text-slate-300")} />
                    </span>
                    <span className="min-w-0 flex-1 overflow-hidden transition-all duration-300 group-hover/sidebar:opacity-100 group-focus-within/sidebar:opacity-100 lg:max-w-0 lg:opacity-0 lg:group-hover/sidebar:max-w-[180px] lg:group-focus-within/sidebar:max-w-[180px]">
                      <span className="block truncate font-medium">{item.label}</span>
                    </span>
                  </NavLink>
                );
              })}
            </div>
          </section>
        ))}
      </nav>

      <div className="mt-3 rounded-[22px] border border-white/10 bg-white/5 p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-slate-100 ring-1 ring-white/10">
            <Bell className="h-4 w-4" />
          </div>
          <div className="min-w-0 transition-all duration-300 group-hover/sidebar:opacity-100 group-focus-within/sidebar:opacity-100 lg:max-w-0 lg:opacity-0 lg:group-hover/sidebar:max-w-[180px] lg:group-focus-within/sidebar:max-w-[180px]">
            <p className="truncate text-sm font-medium text-slate-100">Hermes real pronto</p>
            <p className="truncate text-xs text-slate-400">Sem fallback visual no caminho de sucesso</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function MobileSidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="h-full min-h-0">
      <SidebarContent onNavigate={onNavigate} />
    </div>
  );
}

export function DonorTopBar() {
  const { user, signOut } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const title = routeTitle(location.pathname);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="rounded-[28px] border border-white/10 bg-slate-950/70 px-4 py-3 shadow-[0_24px_80px_-28px_rgba(0,0,0,0.8)] backdrop-blur-xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500">Apoema / Painel ENS-Quality</p>
          <h1 className="truncate text-lg font-semibold text-slate-100">{title.title}</h1>
          <p className="truncate text-sm text-slate-400">{title.subtitle}</p>
        </div>

        <div className="flex items-center gap-2">
          <Dialog open={mobileOpen} onOpenChange={setMobileOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10 lg:hidden">
                <Menu className="h-4 w-4" />
                Menu
              </Button>
            </DialogTrigger>
            <DialogContent className="left-0 top-0 h-full max-w-[360px] translate-x-0 translate-y-0 rounded-none border-r border-white/10 bg-slate-950 p-0 text-slate-100 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.9)]">
              <DialogTitle className="sr-only">Menu principal</DialogTitle>
              <div className="h-full p-3">
                <MobileSidebar
                  onNavigate={() => {
                    setMobileOpen(false);
                  }}
                />
              </div>
            </DialogContent>
          </Dialog>

          <div className="hidden min-w-[180px] rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-right sm:block">
            <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Sessão</p>
            <p className="truncate text-sm font-medium text-slate-100">{user?.name ?? user?.email ?? "Apoema"}</p>
          </div>

          <Button
            variant="outline"
            className="rounded-2xl border-white/10 bg-white/5 text-slate-100 hover:bg-white/10"
            onClick={() => {
              void signOut();
              navigate("/login");
            }}
          >
            <LogOut className="h-4 w-4" />
            Sair
          </Button>
        </div>
      </div>
    </header>
  );
}

export function DonorAppShell() {
  const [sidebarExpanded, setSidebarExpanded] = useState(false);

  const shellStyle: CSSProperties = {
    ["--apoema-sidebar-width" as string]: `${sidebarExpanded ? 312 : 88}px`,
  };

  return (
    <div className="min-h-screen overflow-x-clip bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.14),transparent_34%),radial-gradient(circle_at_85%_0%,rgba(56,189,248,0.12),transparent_30%),linear-gradient(180deg,#07111f_0%,#09131f_100%)] text-slate-100">
      <div
        className="mx-auto grid min-h-screen w-full max-w-[1800px] gap-4 p-4 lg:grid-cols-[var(--apoema-sidebar-width)_minmax(0,1fr)] lg:items-start lg:gap-5 lg:transition-[grid-template-columns] lg:duration-300"
        style={shellStyle}
      >
        <aside
          className="group/sidebar sticky top-4 hidden h-[calc(100dvh-2rem)] min-h-0 overflow-hidden lg:block"
          onMouseEnter={() => setSidebarExpanded(true)}
          onMouseLeave={() => setSidebarExpanded(false)}
          onFocusCapture={() => setSidebarExpanded(true)}
          onBlurCapture={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
              setSidebarExpanded(false);
            }
          }}
        >
          <SidebarContent />
        </aside>

        <div className="flex min-w-0 flex-col gap-4">
          <DonorTopBar />
          <main className="relative z-0 min-w-0 rounded-[32px] border border-white/10 bg-slate-950/55 p-4 shadow-[0_24px_80px_-28px_rgba(0,0,0,0.8)] backdrop-blur-xl md:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
