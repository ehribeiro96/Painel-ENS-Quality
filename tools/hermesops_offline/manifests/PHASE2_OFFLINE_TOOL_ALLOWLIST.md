# Phase 2 Offline Tool Allowlist

## Criteria
- No network required.
- No external action.
- No Docker.
- No Composio execute.
- No secret file required.
- Dry-run safe or inspection-only.

## Active offline tool groups
- `validators/memory/`
- `validators/coderos/`
- `validators/office/`
- `validators/localization/`
- `validators/ingest/`
- `validators/plugins/`
- `auditors/memory/`
- `auditors/coderos/`
- `auditors/office/`
- `auditors/localization/`
- `auditors/ingest/`
- `auditors/plugins/`

## Safe command shape
- `python3 <tool>.py --dry-run` where supported.
- `python3 -m py_compile <tool>.py`
- `python3 -m json.tool <file>.json`

## Status
- Active for offline review and validation only.
