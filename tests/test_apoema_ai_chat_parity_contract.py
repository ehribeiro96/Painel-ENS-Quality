from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "frontend/itam-platform/src/App.tsx").read_text(encoding="utf-8")
MATRIX = (ROOT / "docs/audit/apoema-only-phase-4a-ai-chat/AI_CHAT_PARITY_MATRIX_20260623.md").read_text(encoding="utf-8")
APOEMA = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "frontend/itam-platform/src/apoema").rglob("*"))
    if path.suffix in {".ts", ".tsx", ".css"}
)


class ApoemaAiChatParityContractTest(unittest.TestCase):
    def test_parity_matrix_names_the_legacy_and_apoema_targets(self) -> None:
        self.assertIn("/ai-chat legacy", MATRIX)
        self.assertIn("Apoema Chat", MATRIX)
        self.assertIn("POLICY_A_SAFE_REDIRECT", MATRIX)
        self.assertIn("parity_minimum_met", MATRIX)

    def test_ai_chat_alias_points_to_apoema_chat(self) -> None:
        alias_match = re.search(r"const legacyApoemaAliasRoutes: LegacyApoemaAliasRouteDefinition\[] = \[(.*?)\n\];", APP, re.S)
        self.assertIsNotNone(alias_match)
        alias_block = alias_match.group(1)
        self.assertIn('path: "/ai-chat"', alias_block)
        self.assertIn('migrationTarget: "apoema:chat"', alias_block)
        self.assertIn("function LegacyApoemaAliasRoutes()", APP)
        self.assertIn("<LegacyApoemaAliasRoutes />", APP)
        self.assertIn('to="/apoema/chat"', APP)

    def test_apoema_preview_chat_remains_preserved(self) -> None:
        self.assertIn('path="/apoema-preview/*" element={<ApoemaRoute />}', APP.replace("\n", " "))
        self.assertIn('path="chat" element={<ChatPage />}', (ROOT / "frontend/itam-platform/src/apoema/ApoemaApp.tsx").read_text(encoding="utf-8"))

    def test_apoema_chat_keeps_auth_and_fallback_contract(self) -> None:
        self.assertIn('return "auth_required"', APOEMA)
        self.assertIn('return "forbidden"', APOEMA)
        self.assertIn('kind === "network_unavailable"', APOEMA)
        self.assertIn('source: "fallback"', APOEMA)
        self.assertIn("Backend indisponível. Exibindo resposta local de fallback.", APOEMA)
        self.assertIn("Fallback local ativo", APOEMA)

    def test_no_direct_provider_calls_in_apoema(self) -> None:
        for term in ("localhost:11434", "127.0.0.1:11434", "OLLAMA_BASE_URL", "HERMES_BASE_URL", "COMPOSIO", "/api/chat"):
            self.assertNotIn(term, APOEMA)

    def test_lazy_loading_and_suspense_remain(self) -> None:
        self.assertIn("lazy(() => import(\"./apoema\")", APP)
        self.assertIn("Suspense fallback={<RouteLoading />}", APP)


if __name__ == "__main__":
    unittest.main()
