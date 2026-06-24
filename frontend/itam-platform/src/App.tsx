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
  temporaryCompatibility: true;
  migrationTarget: string;
};

const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition[] = [
  {
    path: "/assets",
    element: <AssetsPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:assets"
  },
  {
    path: "/assets/:id",
    element: <AssetDetailsPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:assets"
  },
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
    path: "/assignments",
    element: <AssignmentsPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:movements"
  },
  {
    path: "/stock",
    element: <StockPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:stock"
  },
  {
    path: "/imports",
    element: (
      <RoleGuard roles={["ADMIN", "TECHNICIAN"]}>
        <ImportsPage />
      </RoleGuard>
    ),
    temporaryCompatibility: true,
    migrationTarget: "apoema:imports"
  },
  {
    path: "/macros",
    element: (
      <RoleGuard roles={["ADMIN", "TECHNICIAN"]}>
        <MacrosPage />
      </RoleGuard>
    ),
    temporaryCompatibility: true,
    migrationTarget: "apoema:macros"
  },
  {
    path: "/ai-chat",
    element: <AiChatPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:chat"
  },
  {
    path: "/signatures",
    element: <SignaturesPage />,
    temporaryCompatibility: true,
    migrationTarget: "apoema:signatures"
  },
  {
    path: "/audit-logs",
    element: (
      <RoleGuard roles={["ADMIN", "MANAGER"]}>
        <AuditLogsPage />
      </RoleGuard>
    ),
    temporaryCompatibility: true,
    migrationTarget: "apoema:audit-logs"
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
