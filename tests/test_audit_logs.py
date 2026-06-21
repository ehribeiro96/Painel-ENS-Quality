from __future__ import annotations

import unittest
from datetime import datetime, timezone
from uuid import uuid4

from tests.operational_http import ROOT

import sys

backend_path = str(ROOT / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.api.v1.routes.audit import build_audit_filters  # noqa: E402
from app.domains.audit.models import AuditLog  # noqa: E402
from app.shared.enums import AuditAction  # noqa: E402


class AuditLogFiltersTest(unittest.TestCase):
    def test_build_audit_filters_without_filters_preserves_default_listing(self) -> None:
        self.assertEqual([], build_audit_filters())

    def test_build_audit_filters_uses_existing_traceability_columns(self) -> None:
        entity_id = uuid4()
        user_id = uuid4()
        date_from = datetime(2026, 6, 1, tzinfo=timezone.utc)
        date_to = datetime(2026, 6, 21, tzinfo=timezone.utc)

        filters = build_audit_filters(
            entity_type="Asset",
            entity_id=entity_id,
            action=AuditAction.MOVE,
            user_id=user_id,
            source="api",
            correlation_id="corr-audit-h1",
            request_id="req-audit-h1",
            date_from=date_from,
            date_to=date_to,
        )

        compiled = "\n".join(str(item.compile(compile_kwargs={"literal_binds": True})) for item in filters)
        self.assertIn("audit_logs.entity", compiled)
        self.assertIn("audit_logs.entity_id", compiled)
        self.assertIn("audit_logs.action", compiled)
        self.assertIn("audit_logs.actor_id", compiled)
        self.assertIn("audit_logs.source", compiled)
        self.assertIn("audit_logs.correlation_id", compiled)
        self.assertIn("audit_logs.request_id", compiled)
        self.assertIn("audit_logs.created_at", compiled)

    def test_build_audit_filters_searches_text_and_ids_without_migration(self) -> None:
        filters = build_audit_filters(search="asset-123")

        self.assertEqual(1, len(filters))
        compiled = str(filters[0].compile(compile_kwargs={"literal_binds": True}))
        self.assertIn("lower(audit_logs.entity)", compiled)
        self.assertIn("lower(audit_logs.source)", compiled)
        self.assertIn("lower(audit_logs.request_id)", compiled)
        self.assertIn("lower(audit_logs.correlation_id)", compiled)
        self.assertIn("audit_logs.entity_id", compiled)
        self.assertIn("audit_logs.actor_id", compiled)

    def test_audit_log_model_has_expected_filterable_columns(self) -> None:
        columns = set(AuditLog.__table__.columns.keys())
        self.assertTrue(
            {
                "actor_id",
                "action",
                "entity",
                "entity_id",
                "request_id",
                "correlation_id",
                "source",
                "created_at",
            }.issubset(columns)
        )


if __name__ == "__main__":
    unittest.main()
