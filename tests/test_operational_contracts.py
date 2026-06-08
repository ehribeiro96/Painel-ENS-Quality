from __future__ import annotations

import importlib.util
import unittest
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

    def test_page_params_allows_operational_page_size_200(self) -> None:
        import sys

        backend_path = str(ROOT / "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.shared.pagination import PageParams

        self.assertEqual(PageParams(page=1, page_size=200).page_size, 200)


if __name__ == "__main__":
    unittest.main()
