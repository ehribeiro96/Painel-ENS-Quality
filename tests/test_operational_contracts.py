from __future__ import annotations

import importlib.util
import unittest
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OperationalContractsTest(unittest.TestCase):
    def test_alembic_revision_ids_fit_default_version_table(self) -> None:
        versions_dir = ROOT / "backend" / "alembic" / "versions"
        for migration in versions_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(migration.stem, migration)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            revision = module.revision
            self.assertLessEqual(len(revision), 32, f"{migration.name} revision id exceeds Alembic default VARCHAR(32)")

    def test_legacy_requirements_wrapper_points_to_legacy_file(self) -> None:
        wrapper = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("-r requirements-legacy.txt", wrapper)
        self.assertTrue((ROOT / "requirements-legacy.txt").exists())

    def test_fastapi_mounts_critical_routes(self) -> None:
        import sys

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.main import app

        routes = {getattr(route, "path", "") for route in app.routes}
        self.assertIn("/health", routes)
        self.assertIn("/health/ready", routes)
        self.assertIn("/api/v1/auth/login", routes)
        self.assertIn("/api/v1/assets", routes)
        self.assertIn("/api/v1/imports/lansweeper", routes)
        self.assertIn("/admin", routes)
        self.assertIn("/assinaturas", routes)

    def test_user_update_schema_does_not_expose_role_changes(self) -> None:
        import sys

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.domains.users.schemas import UserUpdate

        self.assertNotIn("role", UserUpdate.model_fields)

    def test_user_read_allows_legacy_reserved_domain_email(self) -> None:
        import sys
        from types import SimpleNamespace
        from uuid import uuid4

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.domains.users.schemas import UserRead
        from app.shared.enums import Role, UserStatus

        user = SimpleNamespace(
            id=uuid4(),
            name="Legacy Local User",
            email="legacy@example.test",
            job_title=None,
            department=None,
            business_unit=None,
            manager_name=None,
            phone=None,
            status=UserStatus.ACTIVE,
            role=Role.VIEWER,
            source="legacy",
            source_metadata=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        payload = UserRead.model_validate(user)

        self.assertEqual("legacy@example.test", payload.email)

    def test_movement_read_accepts_history_traceability_fields(self) -> None:
        import sys
        from types import SimpleNamespace
        from uuid import uuid4

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.domains.movements.schemas import MovementRead
        from app.shared.enums import AssetStatus

        movement_id = uuid4()
        asset_id = uuid4()
        user_id = uuid4()
        responsible_id = uuid4()
        generation_id = uuid4()
        payload = MovementRead.model_validate(
            SimpleNamespace(
                id=movement_id,
                asset_id=asset_id,
                previous_user_id=None,
                new_user_id=user_id,
                previous_status=AssetStatus.STOCK,
                new_status=AssetStatus.IN_USE,
                previous_location="Estoque",
                new_location="Matriz",
                responsible_id=responsible_id,
                previous_user_name=None,
                new_user_name="Colaborador Teste",
                responsible_name="Tecnico N2",
                asset_label="RJMTEST-HISTORY",
                macro_generation_id=generation_id,
                macro_copied=True,
                macro_copied_at=datetime.now(UTC),
                justification="Entrega controlada",
                notes=None,
                created_at=datetime.now(UTC),
            )
        )

        self.assertEqual(payload.new_user_name, "Colaborador Teste")
        self.assertEqual(payload.responsible_name, "Tecnico N2")
        self.assertEqual(payload.asset_label, "RJMTEST-HISTORY")
        self.assertEqual(payload.macro_generation_id, generation_id)
        self.assertTrue(payload.macro_copied)

    def test_page_params_allows_operational_page_size_200(self) -> None:
        import sys

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.shared.pagination import PageParams

        self.assertEqual(PageParams(page=1, page_size=200).page_size, 200)


if __name__ == "__main__":
    unittest.main()
