from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "audit" / "external-ens-unified-migration-m2-chat-bridge"
REQUIRED_ENDPOINTS = [
    "POST /api/v1/ai-chat/runs",
    "GET /api/v1/ai-chat/runs/{run_id}/events",
    "POST /api/v1/ai-chat/runs/{run_id}/cancel",
    "GET /api/v1/ai-chat/providers",
]
REQUIRED_TERMS = [
    "run.created",
    "message.delta",
    "artifact.created",
    "run.completed",
    "run.failed",
    "AUTH_REQUIRED",
    "NO_DIRECT_FRONTEND_PROVIDER_CALL",
    "SERVER_SIDE_PROVIDER_KEYS_ONLY",
    "STREAM_TIMEOUT",
    "HEARTBEAT",
]


def test_m2_chat_bridge_contract_docs_exist_and_cover_required_terms() -> None:
    report = DOC_ROOT / "ENS_UNIFIED_MIGRATION_M2_CHAT_BRIDGE_20260625.md"
    findings = DOC_ROOT / "ens-unified-migration-m2-chat-bridge-findings.json"
    gates = DOC_ROOT / "ens-unified-migration-m2-chat-bridge-gates.log"
    api_contract = DOC_ROOT / "contracts" / "chat-bridge-api-contract.md"
    event_contract = DOC_ROOT / "contracts" / "chat-bridge-event-contract.md"
    state_contract = DOC_ROOT / "contracts" / "chat-bridge-state-contract.md"
    artifact_contract = DOC_ROOT / "contracts" / "chat-bridge-artifact-integration-contract.md"
    endpoints = DOC_ROOT / "maps" / "chat-bridge-target-contract.tsv"
    event_map = DOC_ROOT / "maps" / "chat-bridge-event-map.tsv"
    security_controls = DOC_ROOT / "maps" / "chat-bridge-security-controls.tsv"

    for path in [report, findings, gates, api_contract, event_contract, state_contract, artifact_contract, endpoints, event_map, security_controls]:
        assert path.is_file(), f"missing required M2 chat bridge file: {path}"

    report_text = report.read_text(encoding="utf-8")
    api_text = api_contract.read_text(encoding="utf-8")
    event_text = event_contract.read_text(encoding="utf-8")
    state_text = state_contract.read_text(encoding="utf-8")
    artifact_text = artifact_contract.read_text(encoding="utf-8")
    endpoint_text = endpoints.read_text(encoding="utf-8")
    event_map_text = event_map.read_text(encoding="utf-8")
    security_text = security_controls.read_text(encoding="utf-8")
    findings_data = json.loads(findings.read_text(encoding="utf-8"))

    for endpoint in REQUIRED_ENDPOINTS:
        _method, path = endpoint.split(" ", 1)
        assert endpoint in api_text
        assert path in endpoint_text
        assert endpoint in report_text

    for term in REQUIRED_TERMS:
        assert (
            term in report_text
            or term in api_text
            or term in event_text
            or term in state_text
            or term in artifact_text
            or term in event_map_text
            or term in security_text
        ), term

    assert findings_data["mode"] == "M2A_CONTRACT_ONLY"
    assert findings_data["external_module"] == "services/chat-bridge"
    assert findings_data["artifact_dependency_status"] == "M1A_CONTRACT_ONLY"
    assert findings_data["push_executed"] is False
