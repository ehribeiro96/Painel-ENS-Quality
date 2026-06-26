from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.domains.rag.schemas import (  # noqa: E402
    RagAuditEntryDTO,
    RagCollectionDTO,
    RagCourseContextDTO,
    RagDocumentDTO,
    RagError,
    RagSearchRequest,
)
from app.services import rag_mcp_mock  # noqa: E402


class RagMcpMockSecurityTest(unittest.TestCase):
    def test_dtos_do_not_expose_internal_paths_or_provider_secrets(self) -> None:
        payloads = [
            RagCollectionDTO.model_construct(
                id="courses",
                label="Cursos",
                description="desc",
                document_count=1,
                tool_names=["ens_rag_search"],
                updated_at=datetime(2026, 6, 26, tzinfo=UTC),
            ),
            RagDocumentDTO.model_construct(
                document_id="doc-1",
                collection="courses",
                title="Doc",
                summary="Summary",
                citation="Mock citation",
                content="Content",
                tags=["tag"],
                updated_at=datetime(2026, 6, 26, tzinfo=UTC),
            ),
            RagCourseContextDTO.model_construct(
                course_id="course-1",
                collection="courses",
                title="Course",
                summary="Summary",
                audience="audience",
                key_documents=[],
                recommendations=["rec"],
                updated_at=datetime(2026, 6, 26, tzinfo=UTC),
            ),
            RagAuditEntryDTO.model_construct(
                event_id="evt-1",
                event_type="rag_search",
                actor_role="VIEWER",
                collection="courses",
                document_id="doc-1",
                course_id=None,
                result="ok",
                occurred_at=datetime(2026, 6, 26, tzinfo=UTC),
                details={"source": "mock"},
            ),
            RagError.model_construct(code="rag_invalid_query", message="bad", details={"query": "x"}),
        ]
        for payload in payloads:
            text = payload.model_dump_json()
            for term in (
                "provider_key",
                "model_secret",
                "internal_path",
                "storage_path",
                "private/",
                "/tmp/",
                "SECRET",
                "TOKEN",
            ):
                self.assertNotIn(term.lower(), text.lower())

    def test_search_request_validation_defaults_and_limits_are_present(self) -> None:
        request = RagSearchRequest(query="ens", collections=["courses"], limit=3)
        self.assertEqual("ens", request.query)
        self.assertEqual(["courses"], request.collections)
        self.assertEqual(3, request.limit)

    def test_service_caps_and_allowlist_are_defined(self) -> None:
        self.assertEqual(1000, rag_mcp_mock.MAX_QUERY_LENGTH)
        self.assertEqual(10, rag_mcp_mock.MAX_RESULTS)
        self.assertEqual(50, rag_mcp_mock.MAX_AUDIT_ENTRIES)
        self.assertEqual({"courses", "institutional", "marketing", "insights"}, set(rag_mcp_mock.ALLOWED_COLLECTIONS))
        self.assertEqual(
            {
                "ens_rag_search",
                "ens_rag_get_document",
                "ens_rag_get_course_context",
                "ens_rag_list_collections",
                "ens_rag_audit_recent",
            },
            set(rag_mcp_mock.ALLOWED_TOOLS),
        )

    def test_search_service_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(rag_mcp_mock.RagMockError):
            rag_mcp_mock.search("x" * 1001, ["courses"], 3)
        with self.assertRaises(rag_mcp_mock.RagMockError):
            rag_mcp_mock.search("ens", ["forbidden"], 3)
        with self.assertRaises(rag_mcp_mock.RagMockError):
            rag_mcp_mock.search("ens", ["courses"], 11)

    def test_search_service_is_deterministic(self) -> None:
        first = rag_mcp_mock.search("curso atendimento", ["courses", "institutional"], 3)
        second = rag_mcp_mock.search("curso atendimento", ["courses", "institutional"], 3)
        self.assertEqual(first.model_dump(), second.model_dump())
        self.assertGreaterEqual(first.total, 1)
        self.assertTrue(first.items[0].document.citation)

    def test_document_and_course_context_lookup_are_mocked(self) -> None:
        document = rag_mcp_mock.get_document("course-onboarding-01")
        course = rag_mcp_mock.get_course_context("itil-foundations")
        self.assertEqual("course-onboarding-01", document.document_id)
        self.assertEqual("itil-foundations", course.course_id)
        self.assertIn("Mock", document.citation)
        self.assertIn("Mock", course.summary)

    def test_unknown_document_and_course_raise_controlled_error(self) -> None:
        with self.assertRaises(rag_mcp_mock.RagMockError):
            rag_mcp_mock.get_document("missing-document")
        with self.assertRaises(rag_mcp_mock.RagMockError):
            rag_mcp_mock.get_course_context("missing-course")

    def test_audit_recent_honors_limit_and_redacts_sensitive_fields(self) -> None:
        response = rag_mcp_mock.audit_recent(2)
        self.assertLessEqual(len(response.items), 2)
        self.assertTrue(all("provider_key" not in entry.model_dump_json().lower() for entry in response.items))


if __name__ == "__main__":
    unittest.main()
