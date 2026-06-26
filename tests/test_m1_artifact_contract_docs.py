from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "audit" / "external-ens-unified-migration-m1-artifact-server"
REQUIRED_ENDPOINTS = [
    "POST /api/v1/artifacts",
    "GET /api/v1/artifacts",
    "GET /api/v1/artifacts/{artifact_id}",
    "GET /api/v1/artifacts/{artifact_id}/download-url",
    "GET /api/v1/artifacts/download/{signed_token}",
    "DELETE /api/v1/artifacts/{artifact_id}",
]
REQUIRED_TERMS = [
    "AUTH_REQUIRED",
    "PRIVATE_STORAGE",
    "SIGNED_URL_EXPIRATION",
    "HMAC_SIGNATURE",
]


def test_m1_artifact_contract_docs_exist_and_cover_required_terms() -> None:
    report = DOC_ROOT / "ENS_UNIFIED_MIGRATION_M1_ARTIFACT_SERVER_20260625.md"
    findings = DOC_ROOT / "ens-unified-migration-m1-artifact-findings.json"
    api_contract = DOC_ROOT / "contracts" / "artifact-api-contract.md"
    data_model = DOC_ROOT / "contracts" / "artifact-data-model.md"
    storage_policy = DOC_ROOT / "contracts" / "artifact-storage-policy.md"
    target_contract = DOC_ROOT / "maps" / "artifact-target-contract.tsv"
    security_controls = DOC_ROOT / "maps" / "artifact-security-controls.tsv"

    for path in [report, findings, api_contract, data_model, storage_policy, target_contract, security_controls]:
        assert path.is_file(), f"missing required M1 artifact file: {path}"

    report_text = report.read_text(encoding="utf-8")
    api_text = api_contract.read_text(encoding="utf-8")
    data_text = data_model.read_text(encoding="utf-8")
    storage_text = storage_policy.read_text(encoding="utf-8")
    target_text = target_contract.read_text(encoding="utf-8")
    security_text = security_controls.read_text(encoding="utf-8")
    findings_data = json.loads(findings.read_text(encoding="utf-8"))

    for endpoint in REQUIRED_ENDPOINTS:
        method, path = endpoint.split(" ", 1)
        assert endpoint in api_text
        assert path in target_text
        assert endpoint in report_text

    for term in REQUIRED_TERMS:
        assert term in api_text or term in storage_text or term in security_text or term in report_text

    assert "metadata" in data_text
    assert "blob" in storage_text
    assert findings_data["mode"] == "M1A_CONTRACT_ONLY"
    assert findings_data["external_module"] == "services/artifact-server"
    assert findings_data["target_endpoints"] == REQUIRED_ENDPOINTS
