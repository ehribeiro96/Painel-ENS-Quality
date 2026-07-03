import "./styles/apoema.css";

import { Navigate, Route, Routes } from "react-router-dom";

import { DonorAppShell } from "./components/DonorAppShell";
import { DonorNotFound } from "./components/DonorNotFound";
import { ArtifactDetailPage } from "./pages/ArtifactDetailPage";
import { ArtifactsPage } from "./pages/ArtifactsPage";
import { AssetDetailPage } from "./pages/AssetDetailPage";
import { AssetsPage } from "./pages/AssetsPage";
import { AssignmentsPage } from "./pages/AssignmentsPage";
import { AuditLogsPage } from "./pages/AuditLogsPage";
import { ChatPage } from "./pages/ChatPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DesignerJobPage } from "./pages/DesignerJobPage";
import { DesignerPage } from "./pages/DesignerPage";
import { ImportsPage } from "./pages/ImportsPage";
import { IntegrationsPage } from "./pages/IntegrationsPage";
import { MacrosPage } from "./pages/MacrosPage";
import { RagCourseContextPage } from "./pages/RagCourseContextPage";
import { RagDocumentPage } from "./pages/RagDocumentPage";
import { RagPage } from "./pages/RagPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SignaturesPage } from "./pages/SignaturesPage";
import { StockPage } from "./pages/StockPage";
import { UserDetailsPage } from "./pages/UserDetailsPage";
import { UsersPage } from "./pages/UsersPage";

export function ApoemaApp() {
  return (
    <Routes>
      <Route element={<DonorAppShell />}>
        <Route index element={<Navigate to="chat" replace />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="assets/:id" element={<AssetDetailPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="users/:id" element={<UserDetailsPage />} />
        <Route path="assignments" element={<AssignmentsPage />} />
        <Route path="signatures" element={<SignaturesPage />} />
        <Route path="stock" element={<StockPage />} />
        <Route path="artifacts" element={<ArtifactsPage />} />
        <Route path="artifacts/:artifactId" element={<ArtifactDetailPage />} />
        <Route path="rag" element={<RagPage />} />
        <Route path="rag/documents/:documentId" element={<RagDocumentPage />} />
        <Route path="rag/courses/:courseId" element={<RagCourseContextPage />} />
        <Route path="designer" element={<DesignerPage />} />
        <Route path="designer/jobs/:jobId" element={<DesignerJobPage />} />
        <Route path="audit-logs" element={<AuditLogsPage />} />
        <Route path="imports" element={<ImportsPage />} />
        <Route path="macros" element={<MacrosPage />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="ai-chat" element={<Navigate to="/apoema/chat" replace />} />
        <Route path="*" element={<DonorNotFound />} />
      </Route>
    </Routes>
  );
}
