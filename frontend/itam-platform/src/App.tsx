import type { ReactNode } from "react";
import { lazy, Suspense } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { RouteLoading } from "./components/RouteLoading";
import { useAuth } from "./lib/auth";
import type { Role } from "./lib/types";

const AppShell = lazy(() => import("./components/AppShell").then((module) => ({ default: module.AppShell })));
const ApoemaApp = lazy(() => import("./apoema").then((module) => ({ default: module.ApoemaApp })));
const AiChatPage = lazy(() => import("./pages/AiChatPage").then((module) => ({ default: module.AiChatPage })));
const AssetDetailsPage = lazy(() => import("./pages/AssetDetailsPage").then((module) => ({ default: module.AssetDetailsPage })));
const AssetsPage = lazy(() => import("./pages/AssetsPage").then((module) => ({ default: module.AssetsPage })));
const AssignmentsPage = lazy(() => import("./pages/AssignmentsPage").then((module) => ({ default: module.AssignmentsPage })));
const AuditLogsPage = lazy(() => import("./pages/AuditLogsPage").then((module) => ({ default: module.AuditLogsPage })));
const DashboardPage = lazy(() => import("./pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const ImportsPage = lazy(() => import("./pages/ImportsPage").then((module) => ({ default: module.ImportsPage })));
const LoginPage = lazy(() => import("./pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const MacrosPage = lazy(() => import("./pages/MacrosPage").then((module) => ({ default: module.MacrosPage })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then((module) => ({ default: module.NotFoundPage })));
const SettingsPage = lazy(() => import("./pages/SettingsPage").then((module) => ({ default: module.SettingsPage })));
const SignaturesPage = lazy(() => import("./pages/SignaturesPage").then((module) => ({ default: module.SignaturesPage })));
const StockPage = lazy(() => import("./pages/StockPage").then((module) => ({ default: module.StockPage })));
const UserDetailsPage = lazy(() => import("./pages/UserDetailsPage").then((module) => ({ default: module.UserDetailsPage })));
const UsersPage = lazy(() => import("./pages/UsersPage").then((module) => ({ default: module.UsersPage })));

function ProtectedRoute({ children, roles }: { children: ReactNode; roles?: Role[] }) {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <RouteLoading />;
  }

  if (!token || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <main className="screen-center">Acesso nao autorizado.</main>;
  }

  return <Suspense fallback={<RouteLoading />}>{children}</Suspense>;
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
  return <Suspense fallback={<RouteLoading />}>{children}</Suspense>;
}

export function App() {
  return (
    <Suspense fallback={<RouteLoading />}>
      <Routes>
        <Route path="/apoema/*" element={<ProtectedRoute><ApoemaApp /></ProtectedRoute>} />
        <Route path="/apoema-preview/*" element={<ProtectedRoute><ApoemaApp /></ProtectedRoute>} />
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
    </Suspense>
  );
}
