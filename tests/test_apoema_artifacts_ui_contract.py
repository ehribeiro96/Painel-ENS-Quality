from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "frontend" / "itam-platform" / "src"
APOEMA = SRC / "apoema"
APP = SRC / "App.tsx"
APOEMA_APP = APOEMA / "ApoemaApp.tsx"
ARTIFACTS_PAGE = APOEMA / "pages" / "ArtifactsPage.tsx"
ARTIFACT_DETAIL_PAGE = APOEMA / "pages" / "ArtifactDetailPage.tsx"
ARTIFACTS_CLIENT = APOEMA / "lib" / "apoemaArtifactsApi.ts"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_apoema_artifact_routes_are_registered_without_legacy_alias() -> None:
    apoema_app = read(APOEMA_APP)
    app = read(APP)

    assert 'path="artifacts"' in apoema_app
    assert 'path="artifacts/:artifactId"' in apoema_app
    assert "ArtifactDetailPage" in apoema_app
    assert 'path="/apoema/*"' in app
    assert 'path="/apoema-preview/*"' in app
    assert 'path="/artifacts"' not in app
    assert "AppShell" not in app


def test_apoema_artifact_files_exist_and_use_backend_api() -> None:
    assert ARTIFACTS_PAGE.exists()
    assert ARTIFACT_DETAIL_PAGE.exists()
    assert ARTIFACTS_CLIENT.exists()

    client = read(ARTIFACTS_CLIENT)
    assert 'const API_BASE = "/api/v1"' in client
    assert '"/artifacts"' in client
    assert "`/artifacts/${encodeURIComponent(artifactId)}`" in client
    assert "`/artifacts/${encodeURIComponent(artifactId)}/download-url`" in client
    assert 'method: "DELETE"' in client
    assert "new FormData()" in client
    assert 'headers.set("content-type"' not in client.lower()


def test_apoema_artifact_ui_handles_expected_backend_states() -> None:
    combined = "\n".join([read(ARTIFACTS_PAGE), read(ARTIFACT_DETAIL_PAGE), read(ARTIFACTS_CLIENT)])

    for marker in ["auth_required", "forbidden", "not_found", "expired", "network_unavailable"]:
        assert marker in combined

    assert "Sessão expirada" in combined
    assert "Sem permissão" in combined
    assert "Artefato não encontrado" in combined
    assert "Link expirado" in combined


def test_apoema_artifact_ui_requires_confirmation_before_delete() -> None:
    combined = "\n".join([read(ARTIFACTS_PAGE), read(ARTIFACT_DETAIL_PAGE)])

    assert "window.confirm" in combined
    assert "irreversível" in combined
    assert "deleteArtifact" in combined


def test_apoema_artifact_ui_does_not_expose_storage_or_raw_temporary_token() -> None:
    combined = "\n".join([read(ARTIFACTS_PAGE), read(ARTIFACT_DETAIL_PAGE), read(ARTIFACTS_CLIENT)])
    forbidden_literals = [
        "data/artifacts" + "/private",
        "private" + "_root",
        "storage" + "_name",
        "storage" + "_path",
        "internal" + "_path",
        "download_token",
        "console.log",
        "console.error",
        "localStorage",
        "sessionStorage",
    ]

    for literal in forbidden_literals:
        assert literal not in combined

    assert "window.open(result.url" in combined
    assert "navigator.clipboard.writeText" not in combined
    assert "result.url}" not in combined


def test_apoema_artifact_frontend_does_not_call_storage_directly() -> None:
    combined = "\n".join([read(ARTIFACTS_PAGE), read(ARTIFACT_DETAIL_PAGE), read(ARTIFACTS_CLIENT)])

    assert "XMLHttpRequest" not in combined
    assert "axios" not in combined
    assert "http://" not in combined
    assert "https://" not in combined
    assert "fetch(`${API_BASE}${path}`" in combined
