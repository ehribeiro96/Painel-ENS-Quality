import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { Archive, ArrowLeftRight, BarChart3, Brain, FileSignature, FileUp, Layers3, Package, Palette, Search, Settings2, ShieldAlert, SplitSquareHorizontal, TextCursorInput, Users, WandSparkles } from "lucide-react";
import { ApoemaLogo } from "./components/ApoemaLogo";
import { ThemeSelector } from "./components/ThemeSelector";
import { useThemeMode } from "./hooks/useThemeMode";
import { DashboardPage } from "./pages/DashboardPage";
import { AssetsPage } from "./pages/AssetsPage";
import { AssetDetailPage } from "./pages/AssetDetailPage";
import { AssignmentsPage } from "./pages/AssignmentsPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";
import { ImportsPage } from "./pages/ImportsPage";
import { MacrosPage } from "./pages/MacrosPage";
import { ChatPage } from "./pages/ChatPage";
import { ArtifactsPage } from "./pages/ArtifactsPage";
import { ArtifactDetailPage } from "./pages/ArtifactDetailPage";
import { RagPage } from "./pages/RagPage";
import { RagDocumentPage } from "./pages/RagDocumentPage";
import { RagCourseContextPage } from "./pages/RagCourseContextPage";
import { DesignerPage } from "./pages/DesignerPage";
import { IntegrationsPage } from "./pages/IntegrationsPage";
import { UserDetailsPage } from "./pages/UserDetailsPage";
import { UsersPage } from "./pages/UsersPage";
import { SignaturesPage } from "./pages/SignaturesPage";
import { SettingsPage } from "./pages/SettingsPage";
import { StockPage } from "./pages/StockPage";
import { StatusPill } from "./components/StatusPill";
import "./styles/apoema.css";

const navItems = [
  { to: "dashboard", label: "Visão geral", icon: BarChart3 },
  { to: "assets", label: "Ativos", icon: Layers3 },
  { to: "users", label: "Usuários", icon: Users },
  { to: "assignments", label: "Movimentações", icon: ArrowLeftRight },
  { to: "signatures", label: "Assinaturas", icon: FileSignature },
  { to: "stock", label: "Estoque", icon: Package },
  { to: "imports", label: "Importações", icon: FileUp },
  { to: "macros", label: "Macros ITIL", icon: TextCursorInput },
  { to: "audit-logs", label: "Auditoria", icon: ShieldAlert },
  { to: "chat", label: "IA", icon: Brain },
  { to: "artifacts", label: "Artefatos", icon: Archive, badge: "Backend" },
  { to: "rag", label: "RAG", icon: Search, badge: "Mock" },
  { to: "designer", label: "Designer", icon: Palette, badge: "Beta controlado" },
  { to: "integrations", label: "Integrações", icon: SplitSquareHorizontal },
  { to: "settings", label: "Ajustes", icon: Settings2 }
];

function ApoemaShell({ theme }: { theme: ReturnType<typeof useThemeMode> }) {
  return (
    <div className="apoema-shell">
      <aside className="apoema-sidebar">
        <ApoemaLogo />
        <nav className="apoema-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `apoema-nav-item ${isActive ? "is-active" : ""}`}>
                <Icon size={16} />
                <span>{item.label}</span>
                {"badge" in item ? <small className="apoema-nav-badge">{item.badge}</small> : null}
              </NavLink>
            );
          })}
        </nav>

        <div className="apoema-sidebar-card">
          <StatusPill tone="success">
            <WandSparkles size={14} />
            Console pronto
          </StatusPill>
          <p>Console compacto para N2 e administração, com foco em leitura rápida e contexto local.</p>
        </div>
      </aside>

      <main className="apoema-main">
        <header className="apoema-topbar">
          <div>
            <span className="apoema-topbar-kicker">Apoema Preview</span>
            <strong>Console Inteligente de Operações, Inventário e Suporte N2</strong>
          </div>
          <div className="apoema-topbar-actions">
            <ThemeSelector value={theme.mode} onChange={theme.setMode} />
          </div>
        </header>
        <Outlet />
      </main>

      <aside className="apoema-rail">
        <div className="apoema-rail-card">
          <StatusPill tone="info">Saúde</StatusPill>
          <strong>Operação estável</strong>
          <p>Camada local e contexto operacional ativos para navegação assistida.</p>
        </div>
        <div className="apoema-rail-card">
          <StatusPill tone="warning">Atenção</StatusPill>
          <strong>Segredos bloqueados</strong>
          <p>Arquivos sensíveis, tokens e credenciais permanecem fora do fluxo.</p>
        </div>
      </aside>
    </div>
  );
}

export function ApoemaApp() {
  const theme = useThemeMode();

  return (
    <div className="apoema-root" data-theme={theme.resolvedTheme}>
      <Routes>
        <Route element={<ApoemaShell theme={theme} />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="assets/:id" element={<AssetDetailPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="users/:id" element={<UserDetailsPage />} />
          <Route path="assignments" element={<AssignmentsPage />} />
          <Route path="signatures" element={<SignaturesPage />} />
          <Route path="stock" element={<StockPage />} />
          <Route path="imports" element={<ImportsPage />} />
          <Route path="macros" element={<MacrosPage />} />
          <Route path="audit-logs" element={<AuditLogsPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="artifacts" element={<ArtifactsPage />} />
          <Route path="artifacts/:artifactId" element={<ArtifactDetailPage />} />
          <Route path="rag" element={<RagPage />} />
          <Route path="rag/documents/:documentId" element={<RagDocumentPage />} />
          <Route path="rag/courses/:courseId" element={<RagCourseContextPage />} />
          <Route path="designer" element={<DesignerPage />} />
          <Route path="integrations" element={<IntegrationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </div>
  );
}
