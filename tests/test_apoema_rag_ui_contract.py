from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "frontend" / "itam-platform" / "src" / "App.tsx"
APOEMA_APP = ROOT / "frontend" / "itam-platform" / "src" / "apoema" / "ApoemaApp.tsx"
APOEMA = ROOT / "frontend" / "itam-platform" / "src" / "apoema"
RAG_API = APOEMA / "lib" / "apoemaRagApi.ts"
RAG_PAGE = APOEMA / "pages" / "RagPage.tsx"
RAG_DOCUMENT_PAGE = APOEMA / "pages" / "RagDocumentPage.tsx"
RAG_COURSE_PAGE = APOEMA / "pages" / "RagCourseContextPage.tsx"
RAG_COLLECTION_FILTER = APOEMA / "components" / "RagCollectionFilter.tsx"
RAG_SEARCH_RESULTS = APOEMA / "components" / "RagSearchResults.tsx"
RAG_DOCUMENT_CARD = APOEMA / "components" / "RagDocumentCard.tsx"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_apoema_rag_routes_are_registered_inside_apoema_shell() -> None:
    content = read(APOEMA_APP)

    assert 'path="rag"' in content
    assert 'path="rag/documents/:documentId"' in content
    assert 'path="rag/courses/:courseId"' in content
    assert "RagPage" in content
    assert "RagDocumentPage" in content
    assert "RagCourseContextPage" in content


def test_legacy_top_level_rag_aliases_are_not_reintroduced() -> None:
    app = read(APP)

    for route in ('path="/rag"', 'path="/knowledge"', 'path="/mcp"'):
        assert route not in app


def test_rag_client_is_scoped_to_backend_api_and_status_mapping() -> None:
    content = read(RAG_API)

    assert 'const API_BASE = "/api/v1"' in content
    assert 'fetch(`${API_BASE}${path}`' in content
    assert 'credentials: init.credentials ?? "include"' in content
    assert '/rag/collections' in content
    assert '/rag/search' in content
    assert '/rag/documents/' in content
    assert '/rag/course-context/' in content
    assert '/rag/audit/recent' in content
    for status_code in ("401", "403", "404", "410", "429"):
        assert status_code in content


def test_rag_ui_text_is_honest_and_read_only() -> None:
    page = read(RAG_PAGE)

    assert "RAG Institucional" in page
    assert "Mock determinístico" in page
    assert "RAG MCP Mock" in page
    assert "runtime externo direto" in page
    assert "read-only" in page.lower()
    assert "contexto de curso" in page.lower()
    assert "internal_path" not in page
    assert "storage_path" not in page
    assert "signed_token" not in page
    assert "ingest" not in page.lower()
    assert "memory write" not in page.lower()
    assert "chat-rag" not in page.lower()


def test_rag_document_and_course_pages_are_safe() -> None:
    document_page = read(RAG_DOCUMENT_PAGE)
    course_page = read(RAG_COURSE_PAGE)

    assert "useParams" in document_page
    assert "documentId" in document_page
    assert "Documento RAG" in document_page
    assert "internal_path" not in document_page
    assert "storage_path" not in document_page
    assert "signed_token" not in document_page

    assert "useParams" in course_page
    assert "courseId" in course_page
    assert "Contexto de curso" in course_page
    assert "internal_path" not in course_page
    assert "storage_path" not in course_page


def test_rag_components_support_read_only_navigation_and_filters() -> None:
    filter_content = read(RAG_COLLECTION_FILTER)
    results_content = read(RAG_SEARCH_RESULTS)
    document_card_content = read(RAG_DOCUMENT_CARD)

    assert "Todas as collections" in filter_content
    assert "RagCollection" in filter_content
    assert "Ver documento" in results_content
    assert "Copiar referência" in results_content
    assert "RagDocumentCard" in results_content
    assert "RagDocumentCard" in document_card_content
    assert "internal_path" not in document_card_content
    assert "storage_path" not in document_card_content
    assert "signed_token" not in document_card_content


def test_rag_ui_does_not_call_providers_or_mcp_directly() -> None:
    files = [RAG_API, RAG_PAGE, RAG_DOCUMENT_PAGE, RAG_COURSE_PAGE, RAG_COLLECTION_FILTER, RAG_SEARCH_RESULTS, RAG_DOCUMENT_CARD]
    forbidden_patterns = (
        re.compile(r"from\s+['\"](?:openai|@google|googleapis|@google-cloud|ollama|composio)"),
        re.compile(r"https?://[^'\"]*(?:openai|gemini|googleapis|vertex|imagen|ollama|composio)", re.IGNORECASE),
        re.compile(r"\b(?:apiKey|api_key|providerKey|VITE_[A-Z0-9_]*KEY|process\.env)\b"),
        re.compile(r"\b(?:MCP_SERVER|VECTOR_DB|QDRANT|PINECONE|CHROMA)\b", re.IGNORECASE),
    )

    for path in files:
        content = read(path)
        assert "XMLHttpRequest" not in content
        assert "axios" not in content
        for pattern in forbidden_patterns:
            assert not pattern.search(content), f"direct provider/vector pattern in {path}: {pattern.pattern}"


def test_storage_state_and_sensitive_artifacts_are_not_reintroduced() -> None:
    suspicious_names = ["auth-state", "storageState", "playwright/.auth", "uat-auth", "cookie", "token", "signed_url", "id_ed25519", "id_rsa"]
    for base in [APOEMA, ROOT / "docs" / "audit" / "frontend-m9b-rag-ui"]:
        if not base.exists():
            continue
        paths = [base] if base.is_file() else [path for path in base.rglob("*") if path.is_file()]
        for path in paths:
            normalized = str(path.relative_to(ROOT))
            assert not any(fragment in normalized for fragment in suspicious_names)


def test_rag_client_maps_http_errors_explicitly() -> None:
    content = read(RAG_API)

    for kind in ("auth_required", "forbidden", "not_found", "expired", "rate_limited", "backend_error", "network_unavailable"):
        assert kind in content
