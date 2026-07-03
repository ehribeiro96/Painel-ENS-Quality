from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_AUDIT_LOGS = (ROOT / "frontend/itam-platform/src/apoema/pages/AuditLogsPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4d-audit-logs/AUDIT_LOGS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


class ApoemaAuditLogsParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Audit Logs Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/audit-logs", MATRIX)
        self.assertIn("/apoema/audit-logs", MATRIX)
        self.assertIn("Paridade", MATRIX)

    def test_audit_logs_route_points_to_apoema_logs_page_without_legacy_alias(self) -> None:
        self.assertIn('path="audit-logs" element={<AuditLogsPage />}', APOEMA_APP)
        self.assertNotIn("legacyCompatibilityRoutes", APP)
        self.assertNotIn("legacyApoemaAliasRoutes", APP)
        self.assertNotIn("LegacyApoemaAliasRoutes", APP)
        self.assertNotIn('path: "/audit-logs"', APP)
        self.assertNotIn('redirectTo: "/apoema/audit-logs"', APP)

    def test_audit_logs_page_contains_operational_filters_and_states(self) -> None:
        for term in ("DonorPanelPageLayout", "DonorSelect", "DonorFieldGrid", "DonorTextInput", "DonorChip", "Base44AuditEventCard", "Base44EmptyState", "LoadingBlock", ".audit(token, query)"):
            self.assertIn(term, APOEMA_AUDIT_LOGS)
        for term in ("pt-BR", "request_id", "correlation_id", "entity_id", "entity_type", "date_from", "date_to"):
            self.assertIn(term, APOEMA_AUDIT_LOGS)
        self.assertIn("Logs de Auditoria", APOEMA_AUDIT_LOGS)
        self.assertIn("Paginação", APOEMA_AUDIT_LOGS)
        for term in ("Base44FilterPanel", "Base44InfoGrid", "Base44PageHeader", "<select"):
            self.assertNotIn(term, APOEMA_AUDIT_LOGS)

    def test_no_direct_provider_calls_in_apoema_audit_logs(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA_AUDIT_LOGS)


if __name__ == "__main__":
    unittest.main()
