from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA = ROOT / "frontend" / "itam-platform" / "src" / "apoema"
APP = ROOT / "frontend" / "itam-platform" / "src" / "App.tsx"
APOEMA_APP = APOEMA / "ApoemaApp.tsx"
CHAT_PAGE = APOEMA / "pages" / "ChatPage.tsx"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_canonical_apoema_ui_stub_routes_exist() -> None:
    content = read(APOEMA_APP)
    chat_page = read(CHAT_PAGE)

    assert "DonorAppShell" in content
    assert 'path="dashboard" element={<DashboardPage />}' in content
    assert 'path="integrations" element={<IntegrationsPage />}' in content
    assert 'path="artifacts"' in content
    assert 'path="rag"' in content
    assert 'path="designer"' in content
    assert 'Chat IA' in chat_page
    assert 'Conversas' in chat_page
    assert 'Hermes real no centro da operação' in chat_page
    assert 'Pronto para operar' in chat_page


def test_apoema_preview_alias_is_controlled_by_app_route_only() -> None:
    app = read(APP)

    assert 'path="/apoema-preview/*"' in app
    assert 'path="/apoema/*"' in app


def test_legacy_top_level_aliases_were_not_reintroduced() -> None:
    app = read(APP)

    forbidden_routes = ['path="/artifacts"', 'path="/rag"', 'path="/designer"', 'path="/files"']
    for route in forbidden_routes:
        assert route not in app


def test_stub_pages_expose_required_safety_copy() -> None:
    artifacts = read(APOEMA / "pages" / "ArtifactsPage.tsx")
    rag = read(APOEMA / "pages" / "RagPage.tsx")
    designer = read(APOEMA / "pages" / "DesignerPage.tsx")

    assert "Backend Artifact Storage" in artifacts
    assert "backend-owned" in artifacts
    assert "não expõe caminho interno" in artifacts
    assert "não é registrada em console" in artifacts

    assert "RAG MCP Mock" in rag
    assert "Mock determinístico" in rag
    assert "MCP real, vector store e provider real não estão ativos" in rag

    assert "Designer Mock" in designer
    assert "Mock determinístico" in designer
    assert "Não há geração real de imagem nem provider real" in designer
    assert "Download-url bloqueado/não disponível" in designer


def test_expected_frontend_clients_exist_and_use_api_v1_paths() -> None:
    client_paths = [
        APOEMA / "lib" / "apoemaArtifactsApi.ts",
        APOEMA / "lib" / "apoemaRagApi.ts",
        APOEMA / "lib" / "apoemaDesignerApi.ts",
    ]

    for path in client_paths:
        content = read(path)
        assert 'const API_BASE = "/api/v1"' in content
        assert "fetch(`${API_BASE}${path}`" in content
        assert "credentials: init.credentials ?? \"include\"" in content
        assert "http://" not in content
        assert "https://" not in content


def test_storage_state_is_not_present_in_tracked_or_m6b_paths() -> None:
    suspicious_names = ["auth-state", "storageState", "playwright/.auth", "uat-auth", "cookie", "token", "signed_url"]
    checked_paths = [
        APOEMA,
        ROOT / "tests" / "test_apoema_ui_stubs_contract.py",
        ROOT / "tests" / "test_apoema_no_direct_provider_contract.py",
        ROOT / "docs" / "audit" / "external-ens-unified-migration-m6b-apoema-ui-stubs",
    ]

    for base in checked_paths:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for path in paths:
            normalized = str(path.relative_to(ROOT))
            assert not any(fragment in normalized for fragment in suspicious_names)
