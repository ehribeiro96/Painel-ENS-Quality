from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APOEMA = ROOT / "frontend" / "itam-platform" / "src" / "apoema"
NEW_MODULE_FILES = [
    APOEMA / "lib" / "apoemaArtifactsApi.ts",
    APOEMA / "lib" / "apoemaRagApi.ts",
    APOEMA / "lib" / "apoemaDesignerApi.ts",
    APOEMA / "pages" / "ArtifactsPage.tsx",
    APOEMA / "pages" / "RagPage.tsx",
    APOEMA / "pages" / "DesignerPage.tsx",
]

PROVIDER_DIRECT_PATTERNS = [
    re.compile(r"from\s+['\"](?:openai|@google|googleapis|@google-cloud|ollama|composio)"),
    re.compile(r"https?://[^'\"]*(?:openai|gemini|googleapis|vertex|imagen|ollama|composio)", re.IGNORECASE),
    re.compile(r"\b(?:apiKey|api_key|providerKey|VITE_[A-Z0-9_]*KEY|process\.env)\b"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_new_apoema_modules_do_not_call_providers_directly() -> None:
    for path in NEW_MODULE_FILES:
        content = read(path)
        for pattern in PROVIDER_DIRECT_PATTERNS:
            assert not pattern.search(content), f"direct provider pattern in {path}: {pattern.pattern}"


def test_new_apoema_modules_only_use_backend_api_v1_for_network_calls() -> None:
    for path in NEW_MODULE_FILES:
        content = read(path)
        assert "XMLHttpRequest" not in content
        assert "axios" not in content
        if "fetch(" in content:
            assert 'const API_BASE = "/api/v1"' in content
            assert "fetch(`${API_BASE}${path}`" in content
            assert "http://" not in content
            assert "https://" not in content


def test_no_provider_key_or_secret_material_in_new_apoema_modules() -> None:
    forbidden = re.compile(
        r"(sk-[A-Za-z0-9_-]+|ghp_[A-Za-z0-9_-]+|xoxb-[A-Za-z0-9_-]+|AKIA[A-Z0-9]{16}|BEGIN .*PRIVATE KEY|VITE_[A-Z0-9_]*KEY|providerKey|apiKey|api_key)",
        re.IGNORECASE,
    )
    for path in NEW_MODULE_FILES:
        assert not forbidden.search(read(path)), f"secret/provider-key-like material in {path}"


def test_backend_owned_clients_do_not_expose_internal_artifact_path_or_signed_url_logs() -> None:
    artifacts_page = read(APOEMA / "pages" / "ArtifactsPage.tsx")
    artifacts_client = read(APOEMA / "lib" / "apoemaArtifactsApi.ts")

    assert "console.log" not in artifacts_page
    assert "console.error" not in artifacts_page
    assert "private_root" not in artifacts_page
    assert "storage_name" not in artifacts_page
    assert "/artifacts/${encodeURIComponent(artifactId)}/download-url" in artifacts_client


def test_mock_boundaries_are_explicit_for_rag_and_designer() -> None:
    rag = read(APOEMA / "pages" / "RagPage.tsx")
    designer = read(APOEMA / "pages" / "DesignerPage.tsx")

    assert "MCP real, vector store e provider real não estão ativos" in rag
    assert "runtime externo direto" in rag
    assert "sem geração real de imagem" in designer.lower()
    assert "nenhuma chave de provider" in designer.lower()
