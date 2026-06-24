import type { ReactNode } from "react";
import { lazy, Suspense, useMemo } from "react";
import { Navigate, Outlet, Route, Routes, useLocation, useParams } from "react-router-dom";
import { RouteLoading } from "./components/RouteLoading";
import { useAuth } from "./lib/auth";
import type { Role } from "./lib/types";

const AppShell = lazy(() => import("./components/AppShell").then((module) => ({ default: module.AppShell })));
const ApoemaApp = lazy(() => import("./apoema").then((module) => ({ default: module.ApoemaApp })));
const LoginPage = lazy(() => import("./pages/LoginPage").then((module) => ({ default: module.LoginPage })));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage").then((module) => ({ default: module.NotFoundPage })));
const SettingsPage = lazy(() => import("./pages/SettingsPage").then((module) => ({ default: module.SettingsPage })));
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

function RoleGuard({ children, roles }: { children: ReactNode; roles: Role[] }) {
  const { user } = useAuth();
  if (!user || !roles.includes(user.role)) {
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

type LegacyApoemaAliasRouteDefinition = {
  path: string;
  temporaryCompatibility: true;
  migrationTarget: string;
  redirectTo: string;
};

const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition[] = [
  {
    path: "/ai-chat",
    temporaryCompatibility: true,
    migrationTarget: "apoema:chat",
    redirectTo: "/apoema/chat"
  },
  {
    path: "/audit-logs",
    temporaryCompatibility: true,
    migrationTarget: "apoema:audit-logs",
    redirectTo: "/apoema/audit-logs"
  },
  {
    path: "/assets",
    temporaryCompatibility: true,
    migrationTarget: "apoema:assets",
    redirectTo: "/apoema/assets"
  },
  {
    path: "/assets/:id",
    temporaryCompatibility: true,
    migrationTarget: "apoema:assets",
    redirectTo: "/apoema/assets/:id"
  },
  {
    path: "/assignments",
    temporaryCompatibility: true,
    migrationTarget: "apoema:movements",
    redirectTo: "/apoema/assignments"
  },
  {
    path: "/imports",
    temporaryCompatibility: true,
    migrationTarget: "apoema:imports",
    redirectTo: "/apoema/imports"
  },
  {
    path: "/macros",
    temporaryCompatibility: true,
    migrationTarget: "apoema:macros",
    redirectTo: "/apoema/macros"
  },
  {
    path: "/signatures",
    temporaryCompatibility: true,
    migrationTarget: "apoema:signatures",
    redirectTo: "/apoema/signatures"
  },
  {
    path: "/stock",
    temporaryCompatibility: true,
    migrationTarget: "apoema:stock",
    redirectTo: "/apoema/stock"
  }
];

function ApoemaCompatibilityAliasRoute({ to }: { to: string }) {
  const location = useLocation();
  const params = useParams();
  const resolvedTo = useMemo(
    () =>
      Object.entries(params).reduce((accumulator, [key, value]) => accumulator.replace(`:${key}`, value ?? ""), to),
    [params, to]
  );

  return (
    <ProtectedRoute>
      <Navigate to={{ pathname: resolvedTo, search: location.search, hash: location.hash }} replace />
    </ProtectedRoute>
  );
}

function LegacyApoemaAliasRoutes() {
  return (
    <>
      {legacyApoemaAliasRoutes.map((route) => (
        <Route key={route.path} path={route.path} element={<ApoemaCompatibilityAliasRoute to={route.redirectTo} />} />
      ))}
    </>
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
      <LegacyApoemaAliasRoutes />
      <Route path="/login" element={<LoginPage />} />
    </>
  );
}

type LegacyCompatibilityRouteDefinition = {
  path: string;
  element: ReactNode;
  temporaryCompatibility: true;
  migrationTarget: string;
};

const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [
  {
    path: "/users",
    element: <UsersPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:users"
  },
  {
    path: "/users/:id",
    element: <UserDetailsPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:users"
  },
  {
    path: "/settings",
    element: (
      <RoleGuard roles={["ADMIN"]}>
        <SettingsPage />
      </RoleGuard>
    ),
    temporaryCompatibility: true,
    migrationTarget: "apoema:settings"
  }
];

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
