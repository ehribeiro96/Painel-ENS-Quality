# Hermes Desktop CLI Wrapper Plan

## Goals
- Provide a safe WSL launcher.
- Provide a Windows PowerShell launcher that invokes WSL safely.
- Allow explicit `--project HermesOps`.
- Allow controlled `--cwd` override.
- Support `--dry-run` for audit and debugging.

## Non-goals
- Do not patch the Desktop app binary.
- Do not write to Program Files.
- Do not manage credentials.
