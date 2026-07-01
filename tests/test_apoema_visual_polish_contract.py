from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "frontend" / "itam-platform" / "src" / "App.tsx"
STYLES = ROOT / "frontend" / "itam-platform" / "src" / "styles.css"
APOEMA_STYLES = ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "styles" / "apoema.css"
CHAT_SIDEBAR = ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "components" / "ChatConversationSidebar.tsx"
ARTIFACT_DETAIL = ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "pages" / "ArtifactDetailPage.tsx"
LOGIN_PAGE = ROOT / "frontend" / "itam-platform" / "src" / "pages" / "LoginPage.tsx"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_apoema_routes_keep_wildcard_only_for_nested_navigation() -> None:
    app = read(APP)

    assert '<Route path="/apoema/*" element={<ApoemaRoute />}' in app
    assert '<Route path="/apoema-preview/*" element={<ApoemaRoute />}' in app
    assert '<Route path="/apoema" element=' not in app
    assert '<Route path="/apoema-preview" element=' not in app
    assert "ProtectedRoute" in app


def test_chat_sidebar_headings_do_not_break_conversation_title() -> None:
    styles = read(APOEMA_STYLES)
    sidebar = read(CHAT_SIDEBAR)

    assert ".apoema-section-head h2" in styles
    assert ".apoema-chat-sidebar h2" in styles
    assert "overflow-wrap: break-word;" in styles
    assert "word-break: normal;" in styles
    assert "min-width: 0;" in styles
    assert "Conversas" in sidebar


def test_login_shell_is_compacted_on_notebook_and_mobile() -> None:
    styles = read(STYLES)

    assert ".base44-login-hero-surface {" in styles
    assert "height: 100%;" not in styles.split(".base44-login-hero-surface {", 1)[1].split("}", 1)[0]
    assert "@media (max-width: 1180px)" in styles
    assert "min-height: auto;" in styles
    assert "align-items: start;" in styles
    assert "place-items: start;" in styles
    assert "padding: 14px;" in styles


def test_artifact_detail_title_keeps_safe_wrapping() -> None:
    styles = read(APOEMA_STYLES)
    artifact_detail = read(ARTIFACT_DETAIL)

    assert "Detalhe do artefato" in artifact_detail
    assert "line-height: 1.04;" in styles
    assert "overflow-wrap: break-word;" in styles
    assert "word-break: normal;" in styles


def test_visual_polish_does_not_reintroduce_auth_or_provider_risks() -> None:
    combined = "\n".join([read(APP), read(STYLES), read(APOEMA_STYLES), read(CHAT_SIDEBAR), read(ARTIFACT_DETAIL), read(LOGIN_PAGE)])

    for forbidden in (
        "openai",
        "gemini",
        "ollama",
        "MCP_SERVER",
        "VECTOR_DB",
        "QDRANT",
        "PINECONE",
        "CHROMA",
        "storage_path",
        "internal_path",
        "signed_url",
        "access_token",
        "refresh_token",
        "Cookie",
        "Set-Cookie",
        "Authorization",
        "Bearer",
    ):
        assert forbidden not in combined
