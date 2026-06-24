from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
APOEMA_APP = (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8")
APOEMA_USERS_PAGE = (ROOT / "frontend/itam-platform/src/apoema/pages/UsersPage.tsx").read_text(encoding="utf-8")
APOEMA_USER_DETAILS = (ROOT / "frontend/itam-platform/src/apoema/pages/UserDetailsPage.tsx").read_text(encoding="utf-8")
LEGACY_USERS_PAGE = (ROOT / "frontend/itam-platform/src/pages/UsersPage.tsx").read_text(encoding="utf-8")
LEGACY_USER_DETAILS = (ROOT / "frontend/itam-platform/src/pages/UserDetailsPage.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4j-users/USERS_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")


def read_apoema_sources() -> str:
    parts: list[str] = []
    apoema_root = ROOT / "frontend/itam-platform/src/apoema"
    for path in sorted(apoema_root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


APOEMA = read_apoema_sources()


class ApoemaUsersParityContractTest(unittest.TestCase):
    def test_parity_matrix_documents_safe_redirect_policy(self) -> None:
        self.assertIn("Users Parity Matrix", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("/users", MATRIX)
        self.assertIn("/apoema/users", MATRIX)
        self.assertIn("Lista/tabela de usuários", MATRIX)
        self.assertIn("Status ativo/inativo", MATRIX)
        self.assertIn("Papel/perfil", MATRIX)

    def test_users_routes_move_to_apoema_and_keep_compatibility_alias(self) -> None:
        normalized = APP.replace("\n", " ")
        self.assertIn('path="/apoema" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema/*" element={<ApoemaRoute />}', normalized)
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', normalized)
        self.assertIn("<LegacyApoemaAliasRoutes />", APP)

        legacy_match = re.search(r"const legacyCompatibilityRoutes: LegacyCompatibilityRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(legacy_match)
        legacy_block = legacy_match.group(1)
        self.assertNotIn('path: "/users"', legacy_block)
        self.assertNotIn('path: "/users/:id"', legacy_block)

        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)
        self.assertIn('path: "/users"', alias_block)
        self.assertIn('path: "/users/:id"', alias_block)
        self.assertIn('migrationTarget: "apoema:users"', alias_block)
        self.assertIn('redirectTo: "/apoema/users"', alias_block)
        self.assertIn('redirectTo: "/apoema/users/:id"', alias_block)

    def test_apoema_app_exposes_users_surface(self) -> None:
        self.assertIn('path="users" element={<UsersPage />}', APOEMA_APP)
        self.assertIn('path="users/:id" element={<UserDetailsPage />}', APOEMA_APP)
        self.assertIn("Users, WandSparkles", APOEMA_APP)
        self.assertIn('to: "users", label: "Usuários"', APOEMA_APP)

    def test_users_page_keeps_base44_operational_surface_and_internal_links(self) -> None:
        for term in (
            "Apoema Usuários",
            "Base44FilterPanel",
            "Base44OperationalGrid",
            "Base44PageHeader",
            "Base44UserCard",
            "Base44UserRoleBadge",
            "DataTable",
            "canWriteOperationalData",
            "canDeleteOperationalData",
            "/apoema/users/",
            "Abrir detalhe",
            "Novo colaborador",
        ):
            self.assertIn(term, APOEMA_USERS_PAGE)

    def test_user_details_page_keeps_detail_links_and_related_surface(self) -> None:
        for term in (
            "Apoema Usuários",
            "Base44OperationalGrid",
            "Base44PageHeader",
            "Base44UserCard",
            "Base44UserRoleBadge",
            "DataTable",
            "/apoema/users",
            "/apoema/signatures",
            "api.userAssets",
        ):
            self.assertIn(term, APOEMA_USER_DETAILS)

    def test_legacy_user_files_remain_available_for_compatibility(self) -> None:
        for term in ("Colaboradores / Usuários", "Abrir detalhe"):
            self.assertIn(term, LEGACY_USERS_PAGE)
        for term in ("Detalhe do usuario", "Gerar assinatura"):
            self.assertIn(term, LEGACY_USER_DETAILS)

    def test_apoema_stays_free_of_direct_provider_calls(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA)

    def test_lazy_loading_and_shell_boundary_remain_preserved(self) -> None:
        self.assertIn('lazy(() => import("./apoema")', APP)
        self.assertIn('Suspense fallback={<RouteLoading />}', APP)
        self.assertIn("function LegacyShellRoute()", APP)
        self.assertIn("<AppShell>", APP)


if __name__ == "__main__":
    unittest.main()
