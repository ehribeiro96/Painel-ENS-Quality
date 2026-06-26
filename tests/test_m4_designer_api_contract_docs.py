from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "audit" / "external-ens-unified-migration-m4-designer-api"
REQUIRED_DOCS = [
    DOC_ROOT / "ENS_UNIFIED_MIGRATION_M4_DESIGNER_API_20260625.md",
    DOC_ROOT / "ens-unified-migration-m4-designer-api-findings.json",
    DOC_ROOT / "ens-unified-migration-m4-designer-api-gates.log",
    DOC_ROOT / "contracts" / "designer-api-contract.md",
    DOC_ROOT / "contracts" / "designer-job-contract.md",
    DOC_ROOT / "contracts" / "designer-template-contract.md",
    DOC_ROOT / "contracts" / "designer-output-artifact-contract.md",
    DOC_ROOT / "contracts" / "designer-provider-isolation-contract.md",
    DOC_ROOT / "maps" / "designer-api-external-endpoints.tsv",
    DOC_ROOT / "maps" / "designer-api-job-map.tsv",
    DOC_ROOT / "maps" / "designer-api-template-map.tsv",
    DOC_ROOT / "maps" / "designer-api-env-map.tsv",
    DOC_ROOT / "maps" / "designer-api-security-controls.tsv",
    DOC_ROOT / "maps" / "designer-api-target-contract.tsv",
    DOC_ROOT / "maps" / "designer-api-artifact-dependencies.tsv",
    DOC_ROOT / "maps" / "designer-api-chat-rag-dependencies.tsv",
]
REQUIRED_ENDPOINTS = [
    "GET /api/v1/designer/templates",
    "GET /api/v1/designer/form-options",
    "POST /api/v1/designer/banners",
    "POST /api/v1/designer/banners/json",
    "GET /api/v1/designer/jobs/{job_id}",
    "GET /api/v1/designer/jobs/{job_id}/download-url",
    "POST /api/v1/designer/jobs/{job_id}/items/{item_id}/adjust",
    "POST /api/v1/designer/jobs/{job_id}/items/{item_id}/refresh-url",
    "POST /api/v1/designer/jobs/{job_id}/cancel",
]
REQUIRED_TERMS = [
    "AUTH_REQUIRED",
    "RBAC_REQUIRED",
    "JOB_OWNERSHIP_CHECK",
    "SERVER_SIDE_PROVIDER_KEYS_ONLY",
    "NO_DIRECT_FRONTEND_PROVIDER_CALL",
    "TEMPLATE_ALLOWLIST",
    "PROMPT_INPUT_VALIDATION",
    "PRIVATE_OUTPUT_STORAGE",
    "SIGNED_DOWNLOAD_URL",
    "M4A_CONTRACT_ONLY",
]


class M4DesignerApiContractDocsTest(unittest.TestCase):
    def test_required_docs_exist(self) -> None:
        for path in REQUIRED_DOCS:
            self.assertTrue(path.is_file(), f"missing required M4 designer file: {path}")

    def test_contract_strings_are_present(self) -> None:
        corpus = "\n".join(
            path.read_text(encoding='utf-8') for path in REQUIRED_DOCS if path.suffix in {'.md', '.tsv', '.json'}
        )
        for endpoint in REQUIRED_ENDPOINTS:
            self.assertIn(endpoint, corpus, f"missing target endpoint: {endpoint}")
        for term in REQUIRED_TERMS:
            self.assertIn(term, corpus, f"missing contract term: {term}")

    def test_findings_json_matches_contract_only_mode(self) -> None:
        findings = json.loads((DOC_ROOT / 'ens-unified-migration-m4-designer-api-findings.json').read_text(encoding='utf-8'))
        self.assertEqual(findings['status'], 'PARTIAL_GO')
        self.assertEqual(findings['mode'], 'M4A_CONTRACT_ONLY')
        self.assertEqual(findings['external_module'], 'apps/designer-api')
        self.assertFalse(findings['backend_changed'])
        self.assertFalse(findings['frontend_changed'])
        self.assertFalse(findings['docker_changed'])
        self.assertFalse(findings['zip_committed'])
        self.assertFalse(findings['external_code_committed'])
        self.assertFalse(findings['push_executed'])
        self.assertEqual(findings['artifact_dependency_status'], 'M1A_CONTRACT_ONLY')
        self.assertEqual(findings['chat_bridge_dependency_status'], 'M2A_CONTRACT_ONLY')
        self.assertEqual(findings['rag_dependency_status'], 'M3A_CONTRACT_ONLY')


if __name__ == '__main__':
    unittest.main()
