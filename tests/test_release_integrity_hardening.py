from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTEGRITY_SCRIPT = ROOT / "scripts" / "release_integrity.sh"
DEPLOYMENT_RUNBOOK = ROOT / "docs" / "operations" / "deployment.md"
ROLLBACK_RUNBOOK = ROOT / "docs" / "operations" / "rollback.md"


class ReleaseIntegrityShellTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(dir="/tmp")
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.repository = self.base / "repository"
        self.evidence = self.base / "evidence"
        self.repository.mkdir()
        subprocess.run(["git", "init", str(self.repository)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.repository), "config", "user.name", "Release Test"], check=True)
        subprocess.run(
            ["git", "-C", str(self.repository), "config", "user.email", "release-test@example.test"],
            check=True,
        )
        (self.repository / "backend").mkdir()
        (self.repository / "backend" / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        (self.repository / "docker-compose.yml").write_text(
            "services:\n  app:\n    image: test\n",
            encoding="utf-8",
        )
        (self.repository / "tracked.txt").write_text("commit-a\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repository), "add", "--", "."], check=True)
        subprocess.run(
            ["git", "-C", str(self.repository), "commit", "-m", "commit a"],
            check=True,
            capture_output=True,
        )
        self.commit_a = self.rev_parse("HEAD")

    def rev_parse(self, revision: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repository), "rev-parse", revision],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def run_integrity(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(INTEGRITY_SCRIPT), *arguments],
            cwd=self.repository,
            env=environment,
            capture_output=True,
            text=True,
        )

    def make_failing_git_wrapper(self, partial_output: bool) -> dict[str, str]:
        wrapper_directory = self.base / ("git-wrapper-partial" if partial_output else "git-wrapper-empty")
        wrapper_directory.mkdir()
        wrapper = wrapper_directory / "git"
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "for argument in \"$@\"; do\n"
            "  if [[ \"${argument}\" = status ]]; then\n"
            f"    {'printf \" M partial.txt\\\\n\"' if partial_output else ':'}\n"
            "    exit 17\n"
            "  fi\n"
            "done\n"
            "exec \"${REAL_GIT}\" \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{wrapper_directory}:{environment['PATH']}"
        environment["REAL_GIT"] = shutil.which("git") or "git"
        return environment

    def make_failing_release_resolution_wrapper(self) -> dict[str, str]:
        wrapper_directory = self.base / "git-wrapper-release-resolution"
        wrapper_directory.mkdir()
        wrapper = wrapper_directory / "git"
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "for argument in \"$@\"; do\n"
            "  if [[ \"${argument}\" = --show-toplevel ]]; then\n"
            "    exit 19\n"
            "  fi\n"
            "done\n"
            "exec \"${REAL_GIT}\" \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{wrapper_directory}:{environment['PATH']}"
        environment["REAL_GIT"] = shutil.which("git") or "git"
        return environment

    def create_commit_b(self, remove_compose: bool = False) -> str:
        (self.repository / "tracked.txt").write_text("commit-b\n", encoding="utf-8")
        if remove_compose:
            (self.repository / "docker-compose.yml").unlink()
            subprocess.run(
                ["git", "-C", str(self.repository), "add", "--update", "--", "docker-compose.yml"],
                check=True,
            )
        subprocess.run(["git", "-C", str(self.repository), "add", "--", "tracked.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(self.repository), "commit", "-m", "commit b"],
            check=True,
            capture_output=True,
        )
        return self.rev_parse("HEAD")

    def test_clean_status_is_accepted_and_status_file_is_external(self) -> None:
        result = self.run_integrity("assert-clean", str(self.repository), str(self.evidence))

        self.assertEqual(0, result.returncode, result.stderr)
        status_file = Path(result.stdout.strip())
        self.assertTrue(status_file.is_file())
        self.assertTrue(status_file.is_relative_to(self.evidence))
        self.assertFalse(status_file.is_relative_to(self.repository))
        self.assertEqual("", status_file.read_text(encoding="utf-8"))

    def test_successful_nonempty_status_is_rejected(self) -> None:
        (self.repository / "untracked-drift.txt").write_text("drift\n", encoding="utf-8")

        result = self.run_integrity("assert-clean", str(self.repository), str(self.evidence))

        self.assertNotEqual(0, result.returncode)
        self.assertIn("release source is not clean", result.stderr)

    def test_failed_status_with_empty_output_is_rejected(self) -> None:
        result = self.run_integrity(
            "assert-clean",
            str(self.repository),
            str(self.evidence),
            environment=self.make_failing_git_wrapper(partial_output=False),
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("git status failed for release source", result.stderr)

    def test_failed_status_with_partial_output_is_rejected(self) -> None:
        result = self.run_integrity(
            "assert-clean",
            str(self.repository),
            str(self.evidence),
            environment=self.make_failing_git_wrapper(partial_output=True),
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("git status failed for release source", result.stderr)

    def test_invalid_evidence_root_creates_no_artifact(self) -> None:
        forbidden_evidence = self.repository / "forbidden-evidence"

        result = self.run_integrity("assert-clean", str(self.repository), str(forbidden_evidence))

        self.assertNotEqual(0, result.returncode)
        self.assertFalse(forbidden_evidence.exists())

    def test_failed_release_resolution_creates_no_evidence(self) -> None:
        result = self.run_integrity(
            "assert-clean",
            str(self.repository),
            str(self.evidence),
            environment=self.make_failing_release_resolution_wrapper(),
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unable to resolve release source", result.stderr)
        self.assertFalse(self.evidence.exists())

    def test_archive_is_pinned_to_commit_and_ignores_later_worktree_change(self) -> None:
        (self.repository / "tracked.txt").write_text("later-worktree-change\n", encoding="utf-8")

        result = self.run_integrity(
            "create-build-context",
            str(self.repository),
            str(self.evidence),
            self.commit_a,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        archive = Path(result.stdout.strip())
        with tarfile.open(archive) as tar:
            archived_text = tar.extractfile("tracked.txt")
            self.assertIsNotNone(archived_text)
            self.assertEqual("commit-a\n", archived_text.read().decode())
            self.assertIn("backend/Dockerfile", tar.getnames())
        verified = self.run_integrity(
            "verify-build-context",
            str(self.repository),
            str(archive),
            self.commit_a,
        )
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assertEqual(self.commit_a, verified.stdout.strip())
        self.assertTrue(Path(f"{archive}.sha256").is_file())

    def test_archive_excludes_untracked_and_protected_filename(self) -> None:
        (self.repository / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        protected_directory = self.repository / "docs"
        protected_directory.mkdir()
        protected_name = "HERMES_LOCAL_OLLAMA_CONFIG_RECOMMENDATION.md"
        (protected_directory / protected_name).write_text("synthetic fixture\n", encoding="utf-8")

        result = self.run_integrity(
            "create-build-context",
            str(self.repository),
            str(self.evidence),
            self.commit_a,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        with tarfile.open(result.stdout.strip()) as tar:
            names = set(tar.getnames())
        self.assertNotIn("untracked.txt", names)
        self.assertNotIn(f"docs/{protected_name}", names)

    def test_divergent_pax_commit_is_rejected(self) -> None:
        archive_result = self.run_integrity(
            "create-build-context",
            str(self.repository),
            str(self.evidence),
            self.commit_a,
        )
        self.assertEqual(0, archive_result.returncode, archive_result.stderr)
        commit_b = self.create_commit_b()

        result = self.run_integrity(
            "verify-build-context",
            str(self.repository),
            archive_result.stdout.strip(),
            commit_b,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("build context commit mismatch", result.stderr)

    def test_empty_and_unreadable_archives_are_rejected(self) -> None:
        empty_archive = self.base / "empty.tar"
        empty_archive.touch()
        unreadable_archive = self.base / "unreadable.tar"
        unreadable_archive.write_bytes(b"not-a-tar")
        unreadable_archive.chmod(0)

        for archive in (empty_archive, unreadable_archive):
            with self.subTest(archive=archive.name):
                result = self.run_integrity(
                    "verify-build-context",
                    str(self.repository),
                    str(archive),
                    self.commit_a,
                )
                self.assertNotEqual(0, result.returncode)

    def test_same_revision_rollback_source_is_accepted(self) -> None:
        rollback_source = self.base / "rollback-source-a"
        subprocess.run(
            ["git", "-C", str(self.repository), "worktree", "add", "--detach", str(rollback_source), self.commit_a],
            check=True,
            capture_output=True,
        )

        result = self.run_integrity(
            "validate-rollback-source",
            str(rollback_source),
            str(self.evidence),
            self.commit_a,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(str(rollback_source / "docker-compose.yml"), result.stdout.strip())

    def test_current_compose_with_previous_revision_is_rejected(self) -> None:
        self.create_commit_b()

        result = self.run_integrity(
            "validate-rollback-source",
            str(self.repository),
            str(self.evidence),
            self.commit_a,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("rollback source revision mismatch", result.stderr)

    def test_invalid_or_missing_certified_revisions_are_rejected(self) -> None:
        revisions = ("", "unknown", f"worktree-{'a' * 40}-dirty", "a" * 39, "f" * 40)

        for revision in revisions:
            with self.subTest(revision=revision):
                result = self.run_integrity("validate-revision", str(self.repository), revision)
                self.assertNotEqual(0, result.returncode)

    def test_missing_historical_compose_is_rejected(self) -> None:
        commit_without_compose = self.create_commit_b(remove_compose=True)
        rollback_source = self.base / "rollback-source-without-compose"
        subprocess.run(
            [
                "git",
                "-C",
                str(self.repository),
                "worktree",
                "add",
                "--detach",
                str(rollback_source),
                commit_without_compose,
            ],
            check=True,
            capture_output=True,
        )

        result = self.run_integrity(
            "validate-rollback-source",
            str(rollback_source),
            str(self.evidence),
            commit_without_compose,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("historical Compose file is missing", result.stderr)

    def test_rollback_override_accepts_only_app_with_auto_migrate_false(self) -> None:
        valid = self.base / "valid-override.yml"
        valid.write_text(
            "services:\n"
            "  app:\n"
            "    image: ${APP_IMAGE:?APP_IMAGE is required}\n"
            "    environment:\n"
            '      APP_AUTO_MIGRATE: "false"\n',
            encoding="utf-8",
        )
        additional_service = self.base / "additional-service.yml"
        additional_service.write_text(
            valid.read_text(encoding="utf-8") + "  redis:\n    image: redis\n",
            encoding="utf-8",
        )
        auto_migrate_true = self.base / "auto-migrate-true.yml"
        auto_migrate_true.write_text(
            valid.read_text(encoding="utf-8").replace('"false"', '"true"'),
            encoding="utf-8",
        )

        accepted = self.run_integrity("validate-rollback-override", str(valid))
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        for invalid in (additional_service, auto_migrate_true):
            with self.subTest(invalid=invalid.name):
                rejected = self.run_integrity("validate-rollback-override", str(invalid))
                self.assertNotEqual(0, rejected.returncode)

    def test_image_reference_and_container_must_resolve_to_expected_id(self) -> None:
        wrapper_directory = self.base / "docker-wrapper"
        wrapper_directory.mkdir()
        docker_wrapper = wrapper_directory / "docker"
        docker_wrapper.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ \"${1:-}\" = image ]]; then\n"
            "  printf '%s\\n' \"${FAKE_IMAGE_ID}\"\n"
            "else\n"
            "  printf '%s\\n' \"${FAKE_CONTAINER_IMAGE_ID}\"\n"
            "fi\n",
            encoding="utf-8",
        )
        docker_wrapper.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{wrapper_directory}:{environment['PATH']}"
        environment["FAKE_IMAGE_ID"] = "sha256:image-a"
        environment["FAKE_CONTAINER_IMAGE_ID"] = "sha256:image-a"

        image_ok = self.run_integrity(
            "assert-image-reference",
            "rollback-ref",
            "sha256:image-a",
            environment=environment,
        )
        container_ok = self.run_integrity(
            "assert-container-image",
            "container-id",
            "sha256:image-a",
            environment=environment,
        )
        self.assertEqual(0, image_ok.returncode, image_ok.stderr)
        self.assertEqual(0, container_ok.returncode, container_ok.stderr)

        image_bad = self.run_integrity(
            "assert-image-reference",
            "rollback-ref",
            "sha256:image-b",
            environment=environment,
        )
        container_bad = self.run_integrity(
            "assert-container-image",
            "container-id",
            "sha256:image-b",
            environment=environment,
        )
        self.assertNotEqual(0, image_bad.returncode)
        self.assertNotEqual(0, container_bad.returncode)


class ReleaseRunbookContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.deployment = DEPLOYMENT_RUNBOOK.read_text(encoding="utf-8")
        cls.rollback = ROLLBACK_RUNBOOK.read_text(encoding="utf-8")

    def test_deployment_preserves_git_status_failures(self) -> None:
        self.assertNotIn('test -z "$(git status', self.deployment)
        self.assertNotIn('if [[ -n "$(git status', self.deployment)
        self.assertIn("release_integrity.sh", self.deployment)
        helper = INTEGRITY_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('if ! git -C "${release_source}"', helper)
        self.assertIn('>"${status_file}"', helper)
        self.assertIn('if [[ -s "${status_file}" ]]', helper)
        self.assertNotIn("|| true", helper)

    def test_build_uses_verified_archive_stdin_and_certified_identity(self) -> None:
        required = (
            "create-build-context",
            'get-tar-commit-id <"${BUILD_CONTEXT_TAR}"',
            'test "${ARCHIVED_COMMIT}" = "${TARGET_COMMIT}"',
            'sha256sum "${BUILD_CONTEXT_TAR}"',
            "--iidfile",
            "--file backend/Dockerfile",
            '--build-arg "OCI_REVISION=${TARGET_COMMIT}"',
            '- <"${BUILD_CONTEXT_TAR}"',
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.deployment)
        self.assertNotIn('--build-arg "OCI_SOURCE=${OCI_SOURCE}" .', self.deployment)

    def test_rollback_uses_historical_compose_minimal_override_and_no_build(self) -> None:
        required = (
            "ROLLBACK_REVISION",
            "validate-revision",
            "git worktree add",
            'test "${TARGET_COMMIT}" = "${ROLLBACK_REVISION}"',
            '--project-directory "${ROLLBACK_SOURCE}"',
            '-f "${ROLLBACK_SOURCE}/docker-compose.yml"',
            '-f "${ROLLBACK_OVERRIDE}"',
            'APP_AUTO_MIGRATE=false',
            "--no-build",
            "assert-image-reference",
            "assert-container-image",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.rollback)
        self.assertNotIn("docker compose config", self.rollback)
        rollout_command = self.rollback.split(
            'APP_IMAGE="${ROLLBACK_IMAGE_REF}" \\\n'
            "   APP_AUTO_MIGRATE=false \\\n"
            "   docker compose",
            1,
        )[1].split("ROLLED_BACK_CONTAINER_ID=", 1)[0]
        self.assertIn("--no-build", rollout_command)
        self.assertIn("up \\", rollout_command)

    def test_documented_override_is_minimal_and_affects_only_app(self) -> None:
        marker = "cat >\"${ROLLBACK_OVERRIDE}\" <<'YAML'"
        override_text = self.rollback.split(marker, 1)[1].split("YAML", 1)[0]
        override = yaml.safe_load(override_text)
        self.assertEqual(
            {
                "services": {
                    "app": {
                        "image": "${APP_IMAGE:?APP_IMAGE is required}",
                        "environment": {"APP_AUTO_MIGRATE": "false"},
                    }
                }
            },
            override,
        )


if __name__ == "__main__":
    unittest.main()
