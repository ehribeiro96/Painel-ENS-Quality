from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / 'docs' / 'audit' / 'external-ens-unified-migration-m5-consolidation'
REQUIRED_DOCS = [
    DOC_ROOT / 'ENS_UNIFIED_MIGRATION_M5_CONSOLIDATION_20260625.md',
    DOC_ROOT / 'ens-unified-migration-m5-findings.json',
    DOC_ROOT / 'maps' / 'phase-status-summary.tsv',
    DOC_ROOT / 'maps' / 'cross-module-dependency-matrix.tsv',
    DOC_ROOT / 'maps' / 'implementation-decision-scorecard.tsv',
    DOC_ROOT / 'maps' / 'security-blocker-register.tsv',
    DOC_ROOT / 'maps' / 'next-implementation-roadmap.tsv',
    DOC_ROOT / 'maps' / 'no-go-boundary.tsv',
    DOC_ROOT / 'prompts' / 'M1B_ARTIFACT_IMPLEMENTATION_PROMPT.md',
    DOC_ROOT / 'prompts' / 'M2B_CHAT_BRIDGE_MOCK_ADAPTER_PROMPT.md',
    DOC_ROOT / 'prompts' / 'M3B_RAG_MCP_MOCK_ADAPTER_PROMPT.md',
    DOC_ROOT / 'prompts' / 'M4B_DESIGNER_MOCK_ADAPTER_PROMPT.md',
    ROOT / 'docs' / 'audit' / 'external-ens-unified-migration-m5-gates.log',
]

REQUIRED_STRINGS = [
    'PATH_A_IMPLEMENT_ARTIFACT_FIRST',
    'M1B_ARTIFACT_IMPLEMENTATION',
    'direct_migration_allowed',
    'backend_changed',
    'frontend_changed',
    'docker_changed',
    'Artifact is the shared base for attachments, outputs, downloads and signed storage',
    'Chat Bridge',
    'Designer API',
    'RAG MCP',
    'apps/chat-web/**',
    'services/hermes-runtime/**',
    'services/artifact-server/**',
    'services/chat-bridge/**',
    'services/rag-mcp/**',
    'apps/designer-api/**',
]


class M5MigrationConsolidationDocsTest(unittest.TestCase):
    def test_required_docs_exist(self) -> None:
        for path in REQUIRED_DOCS:
            self.assertTrue(path.exists(), f'missing required M5 doc: {path}')

    def test_contract_strings_are_present(self) -> None:
        corpus = '\n'.join(
            path.read_text(encoding='utf-8')
            for path in REQUIRED_DOCS
            if path.suffix in {'.md', '.tsv', '.json', '.log'}
        )
        for needle in REQUIRED_STRINGS:
            self.assertIn(needle, corpus, f'missing M5 contract string: {needle}')

    def test_findings_json_matches_decision(self) -> None:
        findings = json.loads((DOC_ROOT / 'ens-unified-migration-m5-findings.json').read_text(encoding='utf-8'))
        self.assertEqual(findings['status'], 'GO')
        self.assertEqual(findings['phase'], 'm5_migration_consolidation_decision')
        self.assertEqual(findings['runtime_port'], 5175)
        self.assertFalse(findings['direct_migration_allowed'])
        self.assertEqual(findings['recommended_path'], 'PATH_A_IMPLEMENT_ARTIFACT_FIRST')
        self.assertEqual(findings['next_recommended_phase'], 'M1B_ARTIFACT_IMPLEMENTATION')
        self.assertFalse(findings['backend_changed'])
        self.assertFalse(findings['frontend_changed'])
        self.assertFalse(findings['docker_changed'])
        self.assertFalse(findings['external_code_committed'])
        self.assertFalse(findings['zip_committed'])
        self.assertFalse(findings['push_executed'])
        self.assertEqual(
            findings['prompts_generated'],
            [
                'M1B_ARTIFACT_IMPLEMENTATION_PROMPT.md',
                'M2B_CHAT_BRIDGE_MOCK_ADAPTER_PROMPT.md',
                'M3B_RAG_MCP_MOCK_ADAPTER_PROMPT.md',
                'M4B_DESIGNER_MOCK_ADAPTER_PROMPT.md',
            ],
        )


if __name__ == '__main__':
    unittest.main()
