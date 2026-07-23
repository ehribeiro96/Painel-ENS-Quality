from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

import yaml
from app.core import health, startup
from app.core.config.settings import Settings
from scripts.assert_oci_labels import LABELS, assert_labels
from scripts.assert_oci_labels import main as assert_oci_main

SAFE_JWT_VALUE = "runtime-hardening-test-secret-value"
ROOT = Path(__file__).resolve().parents[1]


def settings_for(environment: str, **overrides: object) -> Settings:
    values: dict[str, object] = {"environment": environment, "_env_file": None}
    if environment != "local":
        values["jwt_secret_key"] = SAFE_JWT_VALUE
    if environment == "production":
        values.update(ai_provider="ollama", ai_chat_default_provider="ollama")
    values.update(overrides)
    with patch.dict(os.environ, {}, clear=True):
        return Settings(**values)


class AutoMigrationSettingsContractTest(unittest.TestCase):
    def test_default_false_is_consistent_in_every_environment(self) -> None:
        for environment in ("local", "staging", "production"):
            with self.subTest(environment=environment):
                self.assertFalse(settings_for(environment).app_auto_migrate)

    def test_explicit_false_is_preserved_in_every_environment(self) -> None:
        for environment in ("local", "staging", "production"):
            with self.subTest(environment=environment):
                self.assertFalse(settings_for(environment, app_auto_migrate=False).app_auto_migrate)

    def test_explicit_true_is_preserved_in_every_environment(self) -> None:
        for environment in ("local", "staging", "production"):
            with self.subTest(environment=environment):
                self.assertTrue(settings_for(environment, app_auto_migrate=True).app_auto_migrate)

    def test_installed_pydantic_accepts_compose_boolean_spellings(self) -> None:
        for raw_value, expected in (("false", False), ("0", False), ("true", True), ("1", True)):
            with self.subTest(raw_value=raw_value), patch.dict(
                os.environ, {"APP_AUTO_MIGRATE": raw_value}, clear=True
            ):
                self.assertIs(Settings(_env_file=None).app_auto_migrate, expected)

    def test_precedence_is_direct_init_then_environment_then_dotenv_then_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("APP_AUTO_MIGRATE=true\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                self.assertTrue(Settings(_env_file=env_file).app_auto_migrate)
            with patch.dict(os.environ, {"APP_AUTO_MIGRATE": "false"}, clear=True):
                self.assertFalse(Settings(_env_file=env_file).app_auto_migrate)
                self.assertTrue(Settings(app_auto_migrate=True, _env_file=env_file).app_auto_migrate)
            with patch.dict(os.environ, {}, clear=True):
                self.assertFalse(Settings(_env_file=None).app_auto_migrate)

    def test_pydantic_alias_and_model_fields_set_track_explicit_values(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            by_name = Settings(app_auto_migrate=False, _env_file=None)
            unsupported_init_alias = Settings(APP_AUTO_MIGRATE=True, _env_file=None)
            defaulted = Settings(_env_file=None)
        with patch.dict(os.environ, {"APP_AUTO_MIGRATE": "true"}, clear=True):
            by_environment_variable = Settings(_env_file=None)

        self.assertFalse(by_name.app_auto_migrate)
        self.assertFalse(unsupported_init_alias.app_auto_migrate)
        self.assertTrue(by_environment_variable.app_auto_migrate)
        self.assertIn("app_auto_migrate", by_name.model_fields_set)
        self.assertNotIn("app_auto_migrate", unsupported_init_alias.model_fields_set)
        self.assertIn("app_auto_migrate", by_environment_variable.model_fields_set)
        self.assertNotIn("app_auto_migrate", defaulted.model_fields_set)

    def test_local_ai_chat_contract_remains_independent(self) -> None:
        self.assertTrue(settings_for("local").enable_ai_chat)
        self.assertFalse(settings_for("local", enable_ai_chat=False).enable_ai_chat)
        self.assertTrue(settings_for("local", enable_ai_chat=True).enable_ai_chat)


class StartupMigrationContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_disabled_auto_migration_skips_executor_without_mutating_schema(self) -> None:
        configured = SimpleNamespace(app_auto_migrate=False)
        with (
            patch.object(startup, "settings", configured),
            patch.object(startup, "run_migrations_sync") as migration_executor,
            patch.object(startup, "get_migration_status", new=AsyncMock()) as migration_status,
        ):
            await startup.run_migrations()

        migration_executor.assert_not_called()
        migration_status.assert_not_awaited()
        self.assertEqual("skipped", startup.runtime_state["migration"]["status"])

    async def test_disabled_auto_migration_does_not_stop_non_mutating_startup_checks(self) -> None:
        configured = SimpleNamespace(app_auto_migrate=False, app_startup_step_timeout_seconds=1.0)
        with (
            patch.object(startup, "settings", configured),
            patch.object(startup, "validate_settings_for_startup", new=AsyncMock()) as validate_settings,
            patch.object(startup, "wait_for_dependencies", new=AsyncMock()) as dependencies,
            patch.object(startup, "run_migrations_sync") as migration_executor,
            patch.object(startup, "bootstrap_admin", new=AsyncMock()) as bootstrap_admin,
            patch.object(startup, "check_frontend_runtime", new=AsyncMock()) as frontend_check,
            patch.object(startup, "check_legacy_runtime", new=AsyncMock()) as legacy_check,
        ):
            await startup.enterprise_startup()

        validate_settings.assert_awaited_once()
        dependencies.assert_awaited_once()
        migration_executor.assert_not_called()
        bootstrap_admin.assert_awaited_once()
        frontend_check.assert_awaited_once()
        legacy_check.assert_awaited_once()
        self.assertTrue(startup.runtime_state["startup_complete"])

    async def test_readiness_reports_pending_revision_when_auto_migration_is_disabled(self) -> None:
        with (
            patch.object(health, "check_postgres", new=AsyncMock(return_value={"status": "ok"})),
            patch.object(health, "check_redis", new=AsyncMock(return_value={"status": "ok"})),
            patch.object(
                health,
                "get_migration_status",
                new=AsyncMock(
                    return_value={
                        "status": "pending",
                        "current_revision": "current-test-revision",
                        "head_revision": "head-test-revision",
                    }
                ),
            ) as migration_status,
            patch.object(health, "frontend_ready", return_value=True),
        ):
            result = await health.readiness_health()

        migration_status.assert_awaited_once()
        self.assertTrue(result["database"])
        self.assertTrue(result["redis"])
        self.assertFalse(result["migrations"])

    async def test_enabled_auto_migration_executes_once_and_refreshes_revision_status(self) -> None:
        configured = SimpleNamespace(app_auto_migrate=True)
        expected_status = {
            "status": "up_to_date",
            "current_revision": "head-test-revision",
            "head_revision": "head-test-revision",
        }
        with (
            patch.object(startup, "settings", configured),
            patch.object(startup, "run_migrations_sync") as migration_executor,
            patch.object(startup, "get_migration_status", new=AsyncMock(return_value=expected_status)) as migration_status,
        ):
            await startup.run_migrations()

        migration_executor.assert_called_once_with()
        migration_status.assert_awaited_once_with()
        self.assertEqual(expected_status, startup.runtime_state["migration"])

    async def test_enabled_auto_migration_failure_is_recorded_and_propagated(self) -> None:
        configured = SimpleNamespace(app_auto_migrate=True, app_startup_step_timeout_seconds=1.0)
        with (
            patch.object(startup, "settings", configured),
            patch.object(startup, "run_migrations_sync", side_effect=RuntimeError("controlled migration failure")) as executor,
        ):
            with self.assertRaisesRegex(RuntimeError, "controlled migration failure"):
                await startup._run_startup_step(
                    "migrations",
                    "migrations_begin",
                    "migrations_ok",
                    startup.run_migrations,
                )

        executor.assert_called_once_with()
        self.assertEqual("migrations", startup.runtime_state["last_startup_error"]["failed_step"])
        self.assertEqual("RuntimeError", startup.runtime_state["last_startup_error"]["exception_type"])


class ImageProvenanceContractTest(unittest.TestCase):
    def test_normal_build_supports_non_misleading_oci_identity_arguments(self) -> None:
        dockerfile = Path("backend/Dockerfile").read_text(encoding="utf-8")
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")

        for argument, label in (
            ("OCI_REVISION", "org.opencontainers.image.revision"),
            ("OCI_VERSION", "org.opencontainers.image.version"),
            ("OCI_SOURCE", "org.opencontainers.image.source"),
        ):
            with self.subTest(argument=argument):
                self.assertIn(f"ARG {argument}=unknown", dockerfile)
                self.assertIn(f'{label}="${{{argument}}}"', dockerfile)
                self.assertIn(f"{argument}: ${{{argument}:-unknown}}", compose)

        self.assertNotIn("v1.0.0-rc1", dockerfile)
        self.assertNotIn("v1.0.0-rc1", compose)

    @staticmethod
    def _inspect_payload(**overrides: str | None) -> str:
        labels = {
            LABELS["revision"]: "a" * 40,
            LABELS["version"]: "v1.0.0-rc2-candidate",
            LABELS["source"]: "https://github.com/ehribeiro96/Painel-ENS-Quality",
        }
        for name, value in overrides.items():
            label = LABELS[name]
            if value is None:
                labels.pop(label)
            else:
                labels[label] = value
        return json.dumps([{"Id": "sha256:test-image", "Config": {"Labels": labels}}])

    def test_oci_assertion_accepts_exact_certified_labels(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout=self._inspect_payload(), stderr="")
        with patch("scripts.assert_oci_labels.subprocess.run", return_value=completed):
            result = assert_labels(
                "sha256:test-image",
                "a" * 40,
                "v1.0.0-rc2-candidate",
                "https://github.com/ehribeiro96/Painel-ENS-Quality",
            )
        self.assertEqual("sha256:test-image", result["image_id"])

    def test_oci_assertion_rejects_dirty_worktree_revision_for_certification(self) -> None:
        revision = f"worktree-{'a' * 40}-dirty"
        completed = subprocess.CompletedProcess([], 0, stdout=self._inspect_payload(revision=revision), stderr="")
        with (
            patch("scripts.assert_oci_labels.subprocess.run", return_value=completed),
            self.assertRaises(ValueError),
        ):
            assert_labels(
                "sha256:test-image",
                revision,
                "v1.0.0-rc2-candidate",
                "https://github.com/ehribeiro96/Painel-ENS-Quality",
            )

    def test_oci_assertion_rejects_mismatch_missing_and_unknown(self) -> None:
        cases = (
            {"revision": "b" * 40},
            {"version": "wrong-version"},
            {"source": "ehribeiro96/Painel-ENS-Quality"},
            {"revision": None},
            {"version": "unknown"},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                completed = subprocess.CompletedProcess([], 0, stdout=self._inspect_payload(**overrides), stderr="")
                with (
                    patch("scripts.assert_oci_labels.subprocess.run", return_value=completed),
                    self.assertRaises(ValueError),
                ):
                    assert_labels(
                        "sha256:test-image",
                        "a" * 40,
                        "v1.0.0-rc2-candidate",
                        "https://github.com/ehribeiro96/Painel-ENS-Quality",
                    )

    def test_oci_assertion_rejects_empty_expectation_and_missing_image(self) -> None:
        for invalid_revision in ("", "   ", "unknown", "UNKNOWN", f" {'a' * 40} ", "a" * 39):
            with self.subTest(invalid_revision=invalid_revision), self.assertRaises(ValueError):
                assert_labels(
                    "sha256:test-image",
                    invalid_revision,
                    "v1.0.0-rc2-candidate",
                    "https://github.com/ehribeiro96/Painel-ENS-Quality",
                )
        with self.assertRaises(ValueError):
            assert_labels("sha256:test-image", "a" * 40, "v1.0.0-rc2-candidate", "ehribeiro96/Painel-ENS-Quality")
        with patch(
            "scripts.assert_oci_labels.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, ["docker", "image", "inspect"]),
        ):
            self.assertEqual(
                1,
                assert_oci_main(
                    ["missing", "a" * 40, "v1.0.0-rc2-candidate", "https://github.com/ehribeiro96/Painel-ENS-Quality"]
                ),
            )

    def test_local_ollama_document_remains_outside_the_docker_build_context(self) -> None:
        dockerignore = Path(".dockerignore").read_text(encoding="utf-8").splitlines()

        self.assertIn("docs/*", dockerignore)
        self.assertNotIn("!docs/HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md", dockerignore)


class ComposeInterpolationContractTest(unittest.TestCase):
    @staticmethod
    def _source_app() -> dict[str, Any]:
        document = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
        return document["services"]["app"]

    def test_auto_migrate_interpolation_is_substitutable_and_fail_safe(self) -> None:
        app = self._source_app()
        self.assertEqual("${APP_AUTO_MIGRATE:-false}", app["environment"]["APP_AUTO_MIGRATE"])
        for raw_value, expected in (
            (None, "false"),
            ("", "false"),
            ("false", "false"),
            ("0", "0"),
            ("true", "true"),
            ("1", "1"),
        ):
            with self.subTest(raw_value=raw_value):
                self.assertEqual(expected, raw_value or "false")

    def test_oci_defaults_and_build_definition_are_structured(self) -> None:
        app = self._source_app()
        self.assertEqual(
            {
                "OCI_REVISION": "${OCI_REVISION:-unknown}",
                "OCI_SOURCE": "${OCI_SOURCE:-unknown}",
                "OCI_VERSION": "${OCI_VERSION:-unknown}",
            },
            app["build"]["args"],
        )
        self.assertEqual(".", app["build"]["context"])
        self.assertEqual("backend/Dockerfile", app["build"]["dockerfile"])
        self.assertEqual("${APP_IMAGE:-painel-ens-quality-app}", app["image"])

    def test_image_reference_is_declared_and_substitutable(self) -> None:
        image = self._source_app()["image"]
        self.assertEqual("${APP_IMAGE:-painel-ens-quality-app}", image)


class ReleaseTagContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        base = Path(self.temporary_directory.name)
        self.origin = base / "origin.git"
        self.work = base / "work"
        self.git_wrapper = base / "bin"
        self.git_wrapper.mkdir()
        wrapper = self.git_wrapper / "git"
        wrapper.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys\n"
            "args = sys.argv[1:]\n"
            "if args == ['remote', 'get-url', 'origin']:\n"
            "    print('git@github.com:ehribeiro96/Painel-ENS-Quality.git')\n"
            "    raise SystemExit(0)\n"
            "if args and args[0] in {'fetch', 'ls-remote'}:\n"
            "    args = [os.environ['TEST_ORIGIN'] if arg == 'origin' else arg for arg in args]\n"
            "os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT'], *args])\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        subprocess.run(["git", "init", "--bare", str(self.origin)], check=True, capture_output=True)
        subprocess.run(["git", "init", str(self.work)], check=True, capture_output=True)
        for key, value in (("user.name", "Release Test"), ("user.email", "release-test@example.test")):
            subprocess.run(["git", "-C", str(self.work), "config", key, value], check=True)
        (self.work / "tracked.txt").write_text("release test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.work), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(self.work), "commit", "-m", "test release"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.work), "remote", "add", "origin", str(self.origin)], check=True)
        subprocess.run(["git", "-C", str(self.work), "push", "origin", "HEAD:main"], check=True, capture_output=True)
        self.script = ROOT / "scripts" / "resolve_release_tag.sh"

    def _run(self, target_tag: str | None) -> subprocess.CompletedProcess[str]:
        environment = {
            "PATH": f"{self.git_wrapper}:{os.environ['PATH']}",
            "REAL_GIT": shutil.which("git", path=os.environ["PATH"]) or "git",
            "TEST_ORIGIN": str(self.origin),
        }
        if target_tag is not None:
            environment["TARGET_TAG"] = target_tag
        return subprocess.run(
            ["bash", str(self.script)],
            cwd=self.work,
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_missing_and_nonexistent_target_tag_fail_closed(self) -> None:
        self.assertNotEqual(0, self._run(None).returncode)
        self.assertNotEqual(0, self._run("v9.9.9-does-not-exist").returncode)
        self.assertNotEqual(0, self._run("invalid tag name").returncode)
        self.assertNotEqual(0, self._run(" annotated ").returncode)
        self.assertNotEqual(0, self._run("x;touch-pwned").returncode)
        self.assertFalse((self.work / "touch-pwned").exists())

    def test_unexpected_origin_fails_before_remote_access(self) -> None:
        wrapper = self.git_wrapper / "git"
        content = wrapper.read_text(encoding="utf-8").replace(
            "git@github.com:ehribeiro96/Painel-ENS-Quality.git", "ext::sh -c false"
        )
        wrapper.write_text(content, encoding="utf-8")
        result = self._run("any-tag")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unexpected origin URL", result.stderr)

    def test_annotated_tag_that_exists_only_locally_fails_closed(self) -> None:
        subprocess.run(["git", "-C", str(self.work), "tag", "-a", "local-only", "-m", "not published"], check=True)
        self.assertNotEqual(0, self._run("local-only").returncode)

    def test_tag_that_diverges_from_origin_fails_closed(self) -> None:
        subprocess.run(["git", "-C", str(self.work), "tag", "-a", "divergent", "-m", "published"], check=True)
        subprocess.run(["git", "-C", str(self.work), "push", "origin", "refs/tags/divergent"], check=True, capture_output=True)
        (self.work / "tracked.txt").write_text("second commit\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.work), "commit", "-am", "move local tag"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.work), "tag", "-fa", "divergent", "-m", "local divergence"], check=True, capture_output=True)
        self.assertNotEqual(0, self._run("divergent").returncode)

    def test_forced_tag_fetchspec_cannot_overwrite_divergent_local_tag(self) -> None:
        subprocess.run(["git", "-C", str(self.work), "tag", "-a", "forced-fetchspec", "-m", "published"], check=True)
        subprocess.run(
            ["git", "-C", str(self.work), "push", "origin", "refs/tags/forced-fetchspec"],
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "-C", str(self.work), "tag", "-fa", "forced-fetchspec", "-m", "local divergence"], check=True)
        subprocess.run(
            ["git", "-C", str(self.work), "config", "--add", "remote.origin.fetch", "+refs/tags/*:refs/tags/*"],
            check=True,
        )

        local_before = subprocess.run(
            ["git", "-C", str(self.work), "rev-parse", "refs/tags/forced-fetchspec"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertNotEqual(0, self._run("forced-fetchspec").returncode)
        local_after = subprocess.run(
            ["git", "-C", str(self.work), "rev-parse", "refs/tags/forced-fetchspec"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(local_before, local_after)

    def test_different_tag_object_with_same_peeled_commit_fails_closed(self) -> None:
        subprocess.run(["git", "-C", str(self.work), "tag", "-a", "retagged", "-m", "published object"], check=True)
        subprocess.run(["git", "-C", str(self.work), "push", "origin", "refs/tags/retagged"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.work), "tag", "-fa", "retagged", "-m", "different local object"], check=True, capture_output=True)
        self.assertNotEqual(0, self._run("retagged").returncode)

    def test_only_annotated_tag_resolves_to_full_peeled_commit(self) -> None:
        subprocess.run(["git", "-C", str(self.work), "tag", "lightweight"], check=True)
        subprocess.run(["git", "-C", str(self.work), "tag", "-a", "annotated", "-m", "annotated release"], check=True)
        subprocess.run(["git", "-C", str(self.work), "branch", "annotated"], check=True)
        subprocess.run(["git", "-C", str(self.work), "push", "origin", "--tags"], check=True, capture_output=True)
        self.assertNotEqual(0, self._run("lightweight").returncode)

        expected = subprocess.run(
            ["git", "-C", str(self.work), "rev-parse", "refs/tags/annotated^{}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        result = self._run("annotated")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(expected, result.stdout.strip())

    def test_runbooks_use_variable_identity_and_canonical_source(self) -> None:
        for path in (ROOT / "docs/operations/deployment.md", ROOT / "docs/operations/rollback.md"):
            content = path.read_text(encoding="utf-8")
            self.assertIn("TARGET_TAG", content)
            self.assertIn("resolve_release_tag.sh", content)
            self.assertIn("https://github.com/ehribeiro96/Painel-ENS-Quality", content)
            self.assertNotIn("v1.0.0-rc1", content)

        deployment = (ROOT / "docs/operations/deployment.md").read_text(encoding="utf-8")
        rollback = (ROOT / "docs/operations/rollback.md").read_text(encoding="utf-8")
        release_integrity = (ROOT / "scripts/release_integrity.sh").read_text(encoding="utf-8")
        for content in (deployment, rollback):
            self.assertIn("set -euo pipefail", content)
            self.assertIn("OCI_REVISION=", content)
            self.assertIn("OCI_VERSION=", content)
            self.assertIn("assert_oci_labels.py", content)

        self.assertIn("--porcelain=v1", release_integrity)
        self.assertIn("--untracked-files=all", release_integrity)
        self.assertIn('if ! git -C "${release_source}"', release_integrity)
        self.assertIn("EVIDENCE_ROOT", deployment)
        self.assertIn("EVIDENCE_ROOT must be outside the repository", deployment)
        self.assertIn("--iidfile", deployment)
        self.assertIn("create-build-context", deployment)
        self.assertIn('- <"${BUILD_CONTEXT_TAR}"', deployment)
        self.assertIn("docker compose up -d --no-build --no-deps --force-recreate app", deployment)
        self.assertIn("docker compose ps -q app", deployment)
        self.assertLess(deployment.index("assert-clean"), deployment.index("git switch --detach"))
        self.assertIn("APP_AUTO_MIGRATE=false", rollback)
        self.assertIn("ROLLBACK_IMAGE_ID", rollback)
        self.assertIn("ROLLBACK_REVISION", rollback)
        self.assertIn("git worktree add", rollback)
        self.assertIn("docker image tag", rollback)
        self.assertIn('--project-directory "${ROLLBACK_SOURCE}"', rollback)
        self.assertIn('-f "${ROLLBACK_SOURCE}/docker-compose.yml"', rollback)
        self.assertIn("--no-build", rollback)
        self.assertIn("assert-container-image", rollback)

    def test_evidence_root_contract_distinguishes_inside_and_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.assertTrue((ROOT / "evidence").resolve().is_relative_to(ROOT))
            self.assertFalse(Path(temporary_directory).resolve().is_relative_to(ROOT))


if __name__ == "__main__":
    unittest.main()
