from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / 'docs' / 'audit' / 'external-ens-unified-migration-m1b-artifact-implementation'
REQUIRED_DOCS = [
    DOC_ROOT / 'ENS_UNIFIED_MIGRATION_M1B_ARTIFACT_IMPLEMENTATION_20260625.md',
    DOC_ROOT / 'ens-unified-migration-m1b-artifact-findings.json',
    DOC_ROOT / 'artifact-security-checklist.tsv',
    DOC_ROOT / 'artifact-endpoint-smoke.tsv',
    ROOT / 'docs' / 'audit' / 'external-ens-unified-migration-m1b-artifact-gates.log',
]

REQUIRED_STRINGS = [
    'GO',
    'PATH_A_IMPLEMENT_ARTIFACT_FIRST',
    'POST /api/v1/artifacts',
    'GET /api/v1/artifacts/{artifact_id}/download-url',
    'GET /api/v1/artifacts/download/{signed_token}',
    'data/artifacts/private/',
    'HMAC-SHA256',
    'AUTH_REQUIRED',
    'ALLOWED_MIME_TYPES',
    'ALLOWED_EXTENSIONS',
    'tests/test_artifacts_contract.py',
    'tests/test_artifacts_security_contract.py',
    'M1C_ARTIFACT_UAT',
]


class M1BArtifactImplementationDocsTest(unittest.TestCase):
    def test_required_docs_exist(self) -> None:
        for path in REQUIRED_DOCS:
            self.assertTrue(path.exists(), f'missing required M1B doc: {path}')

    def test_contract_strings_are_present(self) -> None:
        corpus = '\n'.join(
            path.read_text(encoding='utf-8')
            for path in REQUIRED_DOCS
            if path.suffix in {'.md', '.tsv', '.json', '.log'}
        )
        for needle in REQUIRED_STRINGS:
            self.assertIn(needle, corpus, f'missing M1B contract string: {needle}')

    def test_findings_json_matches_implemented_contract(self) -> None:
        findings = json.loads((DOC_ROOT / 'ens-unified-migration-m1b-artifact-findings.json').read_text(encoding='utf-8'))
        self.assertEqual(findings['status'], 'GO')
        self.assertEqual(findings['phase'], 'm1b_artifact_implementation')
        self.assertTrue(findings['backend_changed'])
        self.assertFalse(findings['frontend_changed'])
        self.assertFalse(findings['docker_changed'])
        self.assertFalse(findings['migrations_changed'])
        self.assertTrue(findings['storage_private'])
        self.assertTrue(findings['signed_url_hmac'])
        self.assertTrue(findings['auth_required'])
        self.assertTrue(findings['rbac_or_ownership'])
        self.assertTrue(findings['upload_limits'])
        self.assertTrue(findings['allowlists'])
        self.assertTrue(findings['path_traversal_protection'])
        self.assertTrue(findings['metadata_no_internal_path'])
        self.assertEqual(findings['next_recommended_phase'], 'M1C_ARTIFACT_UAT')
        self.assertEqual(
            findings['tests_added'],
            ['tests/test_artifacts_contract.py', 'tests/test_artifacts_security_contract.py'],
        )


if __name__ == '__main__':
    unittest.main()
