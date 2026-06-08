from __future__ import annotations

import importlib.util
import os
import subprocess

from tests.operational_http import ROOT, OperationalTestCase


class MigrationsRegressionTest(OperationalTestCase):
    def test_alembic_current_is_head_in_running_stack(self) -> None:
        project_name = os.getenv("OPERATIONAL_PROJECT_NAME", "itam_validation")
        result = subprocess.run(
            ["docker", "compose", "-p", project_name, "exec", "-T", "app", "sh", "-lc", "cd /app/backend && alembic current && alembic heads"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("(head)", result.stdout)
        self.assertIn("0003_startup_auth_obs", result.stdout)

    def test_revision_ids_fit_alembic_default_version_table(self) -> None:
        for migration in (ROOT / "backend" / "alembic" / "versions").glob("*.py"):
            spec = importlib.util.spec_from_file_location(migration.stem, migration)
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.assertLessEqual(len(module.revision), 32)
