import type { ReactNode } from "react";
import { lazy, Suspense } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { RouteLoading } from "./components/RouteLoading";
import { useAuth } from "./lib/auth";
import type { Role } from "./lib/types";

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

export function App() {
  return (
    <Suspense fallback={<RouteLoading />}>
      <Routes>
        <ApoemaRoutes />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}
