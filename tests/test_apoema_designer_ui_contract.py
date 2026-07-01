from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "frontend" / "itam-platform" / "src"
APOEMA = SRC / "apoema"
APP = SRC / "App.tsx"
APOEMA_APP = APOEMA / "ApoemaApp.tsx"
DESIGNER_API = APOEMA / "lib" / "apoemaDesignerApi.ts"
DESIGNER_PAGE = APOEMA / "pages" / "DesignerPage.tsx"
DESIGNER_JOB_PAGE = APOEMA / "pages" / "DesignerJobPage.tsx"
DESIGNER_FORM = APOEMA / "components" / "DesignerBannerForm.tsx"
DESIGNER_SELECTOR = APOEMA / "components" / "DesignerTemplateSelector.tsx"
DESIGNER_STATUS = APOEMA / "components" / "DesignerJobStatus.tsx"
DESIGNER_ITEMS = APOEMA / "components" / "DesignerJobItems.tsx"
TYPES = APOEMA / "types.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_designer_files_exist_and_routes_are_registered_without_legacy_alias() -> None:
    assert DESIGNER_API.exists()
    assert DESIGNER_PAGE.exists()
    assert DESIGNER_JOB_PAGE.exists()
    assert DESIGNER_FORM.exists()
    assert DESIGNER_SELECTOR.exists()
    assert DESIGNER_STATUS.exists()
    assert DESIGNER_ITEMS.exists()

    apoema_app = read(APOEMA_APP)
    app = read(APP)

    assert 'path="designer" element={<DesignerPage />}' in apoema_app
    assert 'path="designer/jobs/:jobId" element={<DesignerJobPage />}' in apoema_app
    assert 'path="/apoema/*"' in app
    assert 'path="/apoema-preview/*"' in app
    assert 'path="/designer"' not in app
    assert 'path="/banners"' not in app
    assert 'path="/banner-generator"' not in app
    assert "AppShell" not in app


def test_designer_api_uses_backend_contract_and_avoids_blocked_endpoints() -> None:
    client = read(DESIGNER_API)

    for snippet in (
        'const API_BASE = "/api/v1"',
        '"/designer/health"',
        '"/designer/templates"',
        '"/designer/form-options"',
        '"/designer/banners/json"',
        '"/designer/jobs/${encodeURIComponent(jobId)}"',
        '"/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/adjust"',
        '"/designer/jobs/${encodeURIComponent(jobId)}/items/${encodeURIComponent(itemId)}/refresh-url"',
        '"/designer/jobs/${encodeURIComponent(jobId)}/cancel"',
        "network_unavailable",
        "rate_limited",
        "conflict",
        "validation_error",
    ):
        assert snippet in client

    assert '"/designer/banners"' not in client
    assert 'download-url' not in client
    assert "new FormData()" not in client


def test_designer_ui_handles_expected_backend_states_honestly() -> None:
    combined = "\n".join([read(DESIGNER_PAGE), read(DESIGNER_JOB_PAGE), read(DESIGNER_FORM), read(DESIGNER_SELECTOR), read(DESIGNER_STATUS), read(DESIGNER_ITEMS), read(DESIGNER_API), read(TYPES)])

    for marker in ("auth_required", "forbidden", "not_found", "conflict", "expired", "validation_error", "rate_limited", "network_unavailable"):
        assert marker in combined

    for snippet in (
        "Sua sessão expirou ou não foi autenticada.",
        "Você não tem permissão para usar o Designer.",
        "O job está em um estado incompatível com esta ação.",
        "Revise os campos do formulário.",
        "Limite de geração atingido. Tente novamente mais tarde.",
        "Este recurso não está mais disponível.",
        "Falha de rede ao acessar o Designer.",
    ):
        assert snippet in combined


def test_designer_ui_prompts_for_item_actions_and_requires_confirmation_before_cancel() -> None:
    combined = "\n".join([read(DESIGNER_PAGE), read(DESIGNER_JOB_PAGE), read(DESIGNER_ITEMS)])

    assert "window.prompt" in combined
    assert "window.confirm" in combined
    assert "adjustDesignerJobItem" in combined
    assert "refreshDesignerJobItemUrl" in combined
    assert "cancelDesignerJob" in combined


def test_designer_ui_does_not_expose_internal_paths_or_provider_secrets() -> None:
    combined = "\n".join([read(DESIGNER_PAGE), read(DESIGNER_JOB_PAGE), read(DESIGNER_FORM), read(DESIGNER_SELECTOR), read(DESIGNER_STATUS), read(DESIGNER_ITEMS), read(DESIGNER_API), read(TYPES)])

    forbidden_literals = [
        "data/artifacts" + "/private",
        "storage" + "_path",
        "internal" + "_path",
        "download" + "_token",
        "provider" + "_key",
        "console.log",
        "console.error",
        "localStorage",
        "sessionStorage",
    ]

    for literal in forbidden_literals:
        assert literal not in combined

    forbidden_patterns = [
        re.compile(r"from\s+['\"](?:openai|@google|googleapis|@google-cloud|ollama)"),
        re.compile(r"https?://[^'\"]*(?:openai|gemini|googleapis|vertex|image|ollama)", re.IGNORECASE),
        re.compile(r"\b(?:apiKey|api_key|providerKey|VITE_[A-Z0-9_]*KEY|process\.env)\b"),
        re.compile(r"sk-[A-Za-z0-9_-]+|ghp_[A-Za-z0-9_-]+|xoxb-[A-Za-z0-9_-]+|AKIA[A-Z0-9]{16}|BEGIN .*PRIVATE KEY", re.IGNORECASE),
    ]

    for pattern in forbidden_patterns:
        assert pattern.search(combined) is None, pattern.pattern
