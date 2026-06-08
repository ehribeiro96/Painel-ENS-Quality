# Phase 4.1 .gitignore Applied

## Result
- The root `.gitignore` was updated before staging.
- It now excludes:
  - secrets and certificates
  - Python caches and virtualenvs
  - Node build outputs
  - logs and `.jsonl`
  - exports and backups
  - imported release baselines

## Intent
- Prevent accidental versioning of local runtime data and imported release artifacts.

## Status
- Applied successfully before baseline staging.
