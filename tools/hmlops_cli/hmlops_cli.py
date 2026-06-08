#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = PROJECT_ROOT / "tools" / "hmlops_cli"
OFFLINE_ROOT = PROJECT_ROOT / "tools" / "hermesops_offline"
DOCS_ROOT = PROJECT_ROOT / "docs" / "hermesops"
REPORTS_ROOT = PROJECT_ROOT / "reports" / "hml_selective_migration_phase3"
PHASE2_REPORTS_ROOT = PROJECT_ROOT / "reports" / "hml_selective_migration_phase2"
PHASE2_REPORT = PHASE2_REPORTS_ROOT / "09_PHASE2_MIGRATION_EXECUTION_REPORT.md"
PHASE2_MANIFESTS = OFFLINE_ROOT / "manifests"
ALLOWLIST_PATH = TOOL_ROOT / "command_allowlist.json"
DENYLIST_PATH = TOOL_ROOT / "command_denylist.json"
REGISTRY_PATH = TOOL_ROOT / "command_registry.json"

FORBIDDEN_NAME_FRAGMENTS = (
    ".env",
    ".pem",
    ".p12",
    ".pfx",
    ".key",
    ".jsonl",
    "__pycache__",
    ".pyc",
    "node_modules",
    "venv",
    ".venv",
)

SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:OPENAI|COMPOSIO)_API_KEY\s*[:=]"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"(?i)\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"(?i)\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)

DRY_RUN_PRESETS: dict[str, list[str]] = {
    "validators/coderos/validation_runner.py": [
        "--dry-run",
        "--command",
        "python3 -m py_compile tools/hmlops_cli/hmlops_cli.py",
    ],
    "validators/office/office_safety_validator.py": [
        "--dry-run",
        "--path",
        "tools/hermesops_offline/office",
        "--sensitivity",
        "low",
    ],
    "validators/ingest/sanitize_document.py": [
        "--dry-run",
        "--input",
        "tools/hermesops_offline/prompts",
        "--output",
        "reports/hml_selective_migration_phase3/evidence/sanitize_output",
        "--report",
        "reports/hml_selective_migration_phase3/evidence/sanitize_report.json",
    ],
    "auditors/localization/ptbr_prompt_audit.py": [
        "--dry-run",
        "--path",
        "reports/hml_selective_migration_phase3/evidence/ptbr_prompt_sample",
    ],
    "auditors/coderos/code_review_checker.py": [
        "--dry-run",
        "--path",
        "tools/hermesops_offline/coderos",
    ],
    "validators/memory/memory_conflict_check.py": [
        "--dry-run",
        "--memory-id",
        "PHASE3-TEST",
    ],
}


class CLIError(RuntimeError):
    def __init__(self, message: str, exit_code: int = 2):
        super().__init__(message)
        self.exit_code = exit_code


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_within(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
    except Exception:
        return False
    return True


def rel_path(candidate: Path) -> str:
    return str(candidate.relative_to(PROJECT_ROOT))


def read_markdown_bullets(path: Path) -> list[str]:
    if not path.exists():
        return []
    values: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            values.append(line[2:].strip("`"))
        elif line.startswith("`") and line.endswith("`"):
            values.append(line.strip("`"))
    return values


def count_files(root: Path, *, suffixes: Iterable[str] | None = None) -> int:
    suffix_set = {s.lower() for s in suffixes} if suffixes else None
    total = 0
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if suffix_set and item.suffix.lower() not in suffix_set:
            continue
        total += 1
    return total


def list_files(root: Path, *, limit: int = 200) -> list[str]:
    items = []
    for item in sorted(root.rglob("*")):
        if item.is_file():
            items.append(str(item.relative_to(PROJECT_ROOT)))
    return items[:limit]


def scan_forbidden(root: Path) -> list[str]:
    findings: list[str] = []
    for item in sorted(root.rglob("*")):
        if any(fragment in item.name for fragment in FORBIDDEN_NAME_FRAGMENTS):
            findings.append(str(item.relative_to(PROJECT_ROOT)))
    return findings


def scan_secrets(root: Path) -> list[str]:
    findings: list[str] = []
    for item in sorted(root.rglob("*")):
        if not item.is_file():
            continue
        if item.suffix.lower() not in {".py", ".md", ".json", ".yaml", ".yml", ".sh"}:
            continue
        text = item.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(str(item.relative_to(PROJECT_ROOT)))
    return findings


def phase2_manifest_summary() -> dict[str, Any]:
    allow = read_markdown_bullets(PHASE2_MANIFESTS / "PHASE2_OFFLINE_TOOL_ALLOWLIST.md")
    deny = read_markdown_bullets(PHASE2_MANIFESTS / "PHASE2_TOOL_DENYLIST.md")
    risky = [
        line.strip("- ").strip()
        for line in (PHASE2_MANIFESTS / "PHASE2_RISKY_TOOLS_REVIEW_REQUIRED.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if (PHASE2_MANIFESTS / "PHASE2_RISKY_TOOLS_REVIEW_REQUIRED.txt").exists() else []
    return {
        "allowlist_groups": allow,
        "denylist_entries": deny,
        "risky_tools": risky,
        "python_tools_manifest": PHASE2_MANIFESTS / "PHASE2_PYTHON_TOOLS.txt",
        "json_files_manifest": PHASE2_MANIFESTS / "PHASE2_JSON_FILES.txt",
        "file_manifest": PHASE2_MANIFESTS / "PHASE2_FILE_MANIFEST.txt",
    }


def validate_registry() -> dict[str, Any]:
    allow = load_json(ALLOWLIST_PATH)
    deny = load_json(DENYLIST_PATH)
    registry = load_json(REGISTRY_PATH)
    return {
        "allowlist": allow,
        "denylist": deny,
        "registry": registry,
    }


def ensure_reports_dir() -> None:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    (REPORTS_ROOT / "evidence").mkdir(parents=True, exist_ok=True)


def run_python_tool(tool_rel: str, extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    tool_path = (OFFLINE_ROOT / tool_rel).resolve()
    if not is_within(OFFLINE_ROOT, tool_path):
        raise CLIError(f"tool path escapes offline root: {tool_rel}")
    if not tool_path.exists():
        raise CLIError(f"tool not found: {tool_rel}", exit_code=1)
    if not any(tool_rel == allowed for allowed in load_json(ALLOWLIST_PATH)["offline_dry_run_tools"]):
        raise CLIError(f"tool not allowlisted for dry-run: {tool_rel}", exit_code=1)
    cmd = [sys.executable, str(tool_path), *extra_args]
    return subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def cmd_status(_: argparse.Namespace) -> int:
    allow = load_json(ALLOWLIST_PATH)
    registry = load_json(REGISTRY_PATH)
    payload = {
        "project_root": str(PROJECT_ROOT),
        "docs_root_exists": DOCS_ROOT.exists(),
        "offline_root_exists": OFFLINE_ROOT.exists(),
        "phase2_report_exists": PHASE2_REPORT.exists(),
        "phase3_reports_root": str(REPORTS_ROOT),
        "allowed_commands": allow["commands"],
        "registered_commands": [item["name"] for item in registry["commands"]],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_inventory(_: argparse.Namespace) -> int:
    payload = {
        "offline_root": str(OFFLINE_ROOT),
        "active_files": count_files(OFFLINE_ROOT),
        "python_files": count_files(OFFLINE_ROOT, suffixes={".py"}),
        "json_files": count_files(OFFLINE_ROOT, suffixes={".json"}),
        "yaml_files": count_files(OFFLINE_ROOT, suffixes={".yaml", ".yml"}),
        "markdown_files": count_files(OFFLINE_ROOT, suffixes={".md"}),
        "sample_paths": list_files(OFFLINE_ROOT, limit=40),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_docs_status(_: argparse.Namespace) -> int:
    docs_files = [
        DOCS_ROOT / "README.md",
        DOCS_ROOT / "INDEX.md",
        DOCS_ROOT / "MIGRATION_SOURCE.md",
    ]
    payload = {
        "docs_root_exists": DOCS_ROOT.exists(),
        "docs_files_present": [str(path.relative_to(PROJECT_ROOT)) for path in docs_files if path.exists()],
        "docs_file_count": count_files(DOCS_ROOT) if DOCS_ROOT.exists() else 0,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_offline_list(_: argparse.Namespace) -> int:
    manifest = load_json(ALLOWLIST_PATH)
    payload = {
        "allowlisted_commands": manifest["commands"],
        "dry_run_tools": manifest["offline_dry_run_tools"],
        "risk_review_tools": phase2_manifest_summary()["risky_tools"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_offline_validate(_: argparse.Namespace) -> int:
    data = validate_registry()
    allow = data["allowlist"]
    deny = data["denylist"]
    registry = data["registry"]
    registry_names = {item["name"] for item in registry["commands"]}
    missing = [name for name in allow["commands"] if name not in registry_names]
    required_deny_commands = {
        "shell",
        "exec",
        "network",
        "docker-up",
        "docker-down",
        "composio-exec",
        "desktop-launch",
        "global-install",
        "path-traversal",
    }
    deny_commands = set(deny["blocked_commands"])
    missing_deny_commands = sorted(required_deny_commands - deny_commands)
    required_review_only = {
        "tools/hermesops_offline/auditors/localization/ptbr_localization_audit.py",
        "tools/hermesops_offline/validators/coderos/powershell_static_checker.py",
        "tools/hermesops_offline/validators/coderos/stack_detector.py",
    }
    review_only = set(deny["review_only_tools"])
    missing_review_only = sorted(required_review_only - review_only)
    payload = {
        "missing_registry_commands": missing,
        "missing_deny_commands": missing_deny_commands,
        "missing_review_only_tools": missing_review_only,
        "denylist_paths": deny["blocked_paths"],
        "phase2_risky_tools": phase2_manifest_summary()["risky_tools"],
        "status": "ok" if not (missing or missing_deny_commands or missing_review_only) else "needs_review",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if missing or missing_deny_commands or missing_review_only:
        return 1
    return 0


def cmd_offline_dry_run(args: argparse.Namespace) -> int:
    tool_rel = args.tool
    if Path(tool_rel).is_absolute() or ".." in Path(tool_rel).parts:
        raise CLIError(f"invalid tool path: {tool_rel}", exit_code=1)
    preset = DRY_RUN_PRESETS.get(tool_rel)
    if preset is None:
        raise CLIError(f"no dry-run preset for tool: {tool_rel}", exit_code=1)
    result = run_python_tool(tool_rel, preset)
    payload = {
        "tool": tool_rel,
        "returncode": result.returncode,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
        "status": "ok" if result.returncode == 0 else "failed",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if result.returncode == 0 else result.returncode


def cmd_schemas_validate(_: argparse.Namespace) -> int:
    paths = [ALLOWLIST_PATH, DENYLIST_PATH, REGISTRY_PATH]
    loaded = []
    for path in paths:
        loaded.append({"path": str(path.relative_to(PROJECT_ROOT)), "ok": True, "keys": list(load_json(path).keys())})
    print(json.dumps({"validated": loaded, "status": "ok"}, indent=2, ensure_ascii=False))
    return 0


def cmd_python_validate(_: argparse.Namespace) -> int:
    cmd = [
        sys.executable,
        "-m",
        "py_compile",
        str(TOOL_ROOT / "hmlops_cli.py"),
    ]
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=False)
    payload = {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip().splitlines(),
        "stderr": result.stderr.strip().splitlines(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return result.returncode


def cmd_security_scan(_: argparse.Namespace) -> int:
    roots = [TOOL_ROOT / "hmlops_cli.py", PROJECT_ROOT / "scripts" / "hmlops"]
    findings = []
    secret_hits = []
    for root in roots:
        if root.is_file():
            path_list = [root]
        else:
            path_list = [p for p in sorted(root.rglob("*")) if p.is_file()]
        for path in path_list:
            rel = str(path.relative_to(PROJECT_ROOT))
            if any(fragment in path.name for fragment in FORBIDDEN_NAME_FRAGMENTS):
                findings.append(rel)
            if path.suffix.lower() in {".py", ".sh"} and any(pattern.search(path.read_text(encoding="utf-8", errors="ignore")) for pattern in SECRET_PATTERNS):
                secret_hits.append(rel)
    payload = {
        "forbidden_findings": findings,
        "secret_hits": secret_hits,
        "status": "ok" if not findings and not secret_hits else "needs_review",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not findings and not secret_hits else 1


def cmd_phase2_summary(_: argparse.Namespace) -> int:
    summary = phase2_manifest_summary()
    payload = {
        "phase2_report": str(PHASE2_REPORT.relative_to(PROJECT_ROOT)) if PHASE2_REPORT.exists() else None,
        "phase2_final_status": "GO COM RESSALVAS" if PHASE2_REPORT.exists() else "unknown",
        "allowlist_groups": summary["allowlist_groups"],
        "risky_tools": summary["risky_tools"],
        "active_offline_files": count_files(OFFLINE_ROOT),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_migration_status(_: argparse.Namespace) -> int:
    payload = {
        "phase1_docs": DOCS_ROOT.exists(),
        "phase2_offline_tools": OFFLINE_ROOT.exists(),
        "phase3_cli": TOOL_ROOT.exists(),
        "phase1_report": str((PROJECT_ROOT / "reports" / "hml_selective_migration_phase1" / "04_PHASE1_MIGRATION_EXECUTION_REPORT.md").relative_to(PROJECT_ROOT)),
        "phase2_report": str(PHASE2_REPORT.relative_to(PROJECT_ROOT)) if PHASE2_REPORT.exists() else None,
        "phase3_report_dir": str(REPORTS_ROOT.relative_to(PROJECT_ROOT)),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_reports_list(_: argparse.Namespace) -> int:
    if not REPORTS_ROOT.exists():
        print(json.dumps({"reports": []}, indent=2, ensure_ascii=False))
        return 0
    reports = [str(path.relative_to(PROJECT_ROOT)) for path in sorted(REPORTS_ROOT.glob("*.md"))]
    print(json.dumps({"reports": reports}, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmlops", description="Offline HML CLI for controlled review and reporting")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show a high-level status snapshot").set_defaults(func=cmd_status)
    sub.add_parser("inventory", help="List the offline tree inventory").set_defaults(func=cmd_inventory)
    sub.add_parser("docs-status", help="Summarize the migrated docs tree").set_defaults(func=cmd_docs_status)
    sub.add_parser("offline-list", help="List allowlisted offline commands and tools").set_defaults(func=cmd_offline_list)
    sub.add_parser("offline-validate", help="Validate offline registry and policies").set_defaults(func=cmd_offline_validate)

    offline_dry_run = sub.add_parser("offline-dry-run", help="Run one allowlisted offline tool in dry-run mode")
    offline_dry_run.add_argument("--tool", required=True, help="Relative path under tools/hermesops_offline")
    offline_dry_run.set_defaults(func=cmd_offline_dry_run)

    sub.add_parser("schemas-validate", help="Validate the local JSON policy files").set_defaults(func=cmd_schemas_validate)
    sub.add_parser("python-validate", help="Run a local py_compile check on the CLI").set_defaults(func=cmd_python_validate)
    sub.add_parser("security-scan", help="Scan the CLI surface for forbidden files and secret-like text").set_defaults(func=cmd_security_scan)
    sub.add_parser("phase2-summary", help="Summarize Phase 2").set_defaults(func=cmd_phase2_summary)

    migration = sub.add_parser("migration", help="Migration status helpers")
    migration_sub = migration.add_subparsers(dest="migration_command", required=True)
    migration_sub.add_parser("status", help="Summarize migration state").set_defaults(func=cmd_migration_status)

    reports = sub.add_parser("reports", help="Report helpers")
    reports_sub = reports.add_subparsers(dest="reports_command", required=True)
    reports_sub.add_parser("list", help="List phase 3 reports").set_defaults(func=cmd_reports_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_reports_dir()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except CLIError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2, ensure_ascii=False), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
