import type { ReactNode } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { ApoemaApp } from "./apoema";
import { useAuth } from "./lib/auth";
import type { Role } from "./lib/types";
import { AiChatPage } from "./pages/AiChatPage";
import { AssetDetailsPage } from "./pages/AssetDetailsPage";
import { AssetsPage } from "./pages/AssetsPage";
import { AssignmentsPage } from "./pages/AssignmentsPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ImportsPage } from "./pages/ImportsPage";
import { LoginPage } from "./pages/LoginPage";
import { MacrosPage } from "./pages/MacrosPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SignaturesPage } from "./pages/SignaturesPage";
import { StockPage } from "./pages/StockPage";
import { UserDetailsPage } from "./pages/UserDetailsPage";
import { UsersPage } from "./pages/UsersPage";

function ProtectedRoute({ children, roles }: { children: ReactNode; roles?: Role[] }) {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <main className="screen-center">Carregando...</main>;
  }

  if (!token || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <main className="screen-center">Acesso nao autorizado.</main>;
  }

  return children;
}

function ShellRoute() {
  return (
    <ProtectedRoute>
      <AppShell>
        <Outlet />
      </AppShell>
    </ProtectedRoute>
  );
}

function RoleGuard({ children, roles }: { children: ReactNode; roles: Role[] }) {
  const { user } = useAuth();
  if (!user || !roles.includes(user.role)) {
    return <main className="screen-center">Acesso nao autorizado.</main>;
  }
  return children;
}

export function App() {
  return (
    <Routes>
      <Route path="/apoema/*" element={<ApoemaApp />} />
      <Route path="/apoema-preview/*" element={<ApoemaApp />} />
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ShellRoute />}>
        <Route index element={<DashboardPage />} />
        <Route path="/assets" element={<AssetsPage />} />
        <Route path="/assets/:id" element={<AssetDetailsPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/users/:id" element={<UserDetailsPage />} />
        <Route path="/assignments" element={<AssignmentsPage />} />
        <Route path="/stock" element={<StockPage />} />
        <Route path="/imports" element={<RoleGuard roles={["ADMIN", "TECHNICIAN"]}><ImportsPage /></RoleGuard>} />
        <Route path="/macros" element={<RoleGuard roles={["ADMIN", "TECHNICIAN"]}><MacrosPage /></RoleGuard>} />
        <Route path="/ai-chat" element={<AiChatPage />} />
        <Route path="/signatures" element={<SignaturesPage />} />
        <Route path="/audit-logs" element={<RoleGuard roles={["ADMIN", "MANAGER"]}><AuditLogsPage /></RoleGuard>} />
        <Route path="/settings" element={<RoleGuard roles={["ADMIN"]}><SettingsPage /></RoleGuard>} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
