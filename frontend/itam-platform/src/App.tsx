import type { ReactNode } from "react";
import { lazy, Suspense } from "react";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { RouteLoading } from "./components/RouteLoading";
import { useAuth } from "./lib/auth";
import type { Role } from "./lib/types";

const AppShell = lazy(() => import("./components/AppShell").then((module) => ({ default: module.AppShell })));
const ApoemaApp = lazy(() => import("./apoema").then((module) => ({ default: module.ApoemaApp })));
const LoginPage = lazy(() => import("./pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then((module) => ({ default: module.NotFoundPage })));

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

function ApoemaRoute() {
  return (
    <ProtectedRoute>
      <ApoemaApp />
    </ProtectedRoute>
  );
}

function ApoemaRoutes() {
  return (
    <>
      <Route path="/" element={<Navigate to="/apoema" replace />} />
      <Route path="/apoema" element={<ApoemaRoute />} />
      <Route path="/apoema/*" element={<ApoemaRoute />} />
      <Route path="/apoema-preview" element={<ApoemaRoute />} />
      <Route path="/apoema-preview/*" element={<ApoemaRoute />} />
      <Route path="/login" element={<LoginPage />} />
    </>
  );
}

type LegacyCompatibilityRouteDefinition = {
  path: string;
  element: ReactNode;
};

const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [];

// Legacy routes are retained temporarily while Apoema becomes the primary surface.
function LegacyShellRoute() {
  return (
    <ProtectedRoute>
      <AppShell>
        <Outlet />
      </AppShell>
    </ProtectedRoute>
  );
}

function LegacyRoutes() {
  return (
    <Route element={<LegacyShellRoute />}>
      {legacyCompatibilityRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={route.element} />
      ))}
    </Route>
  );
}

export function App() {
  return (
    <Suspense fallback={<RouteLoading />}>
      <Routes>
        <ApoemaRoutes />
        <LegacyRoutes />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}
