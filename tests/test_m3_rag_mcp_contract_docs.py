from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M3_ROOT = ROOT / 'docs' / 'audit' / 'external-ens-unified-migration-m3-rag-mcp'

REQUIRED_DOCS = [
    M3_ROOT / 'ENS_UNIFIED_MIGRATION_M3_RAG_MCP_20260625.md',
    M3_ROOT / 'contracts' / 'rag-mcp-api-contract.md',
    M3_ROOT / 'contracts' / 'rag-mcp-tool-contract.md',
    M3_ROOT / 'contracts' / 'rag-mcp-resource-contract.md',
    M3_ROOT / 'contracts' / 'rag-mcp-ingestion-contract.md',
    M3_ROOT / 'contracts' / 'rag-mcp-chat-bridge-integration-contract.md',
    M3_ROOT / 'maps' / 'rag-mcp-external-tools.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-external-resources.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-collections-map.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-env-map.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-security-controls.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-target-contract.tsv',
    M3_ROOT / 'maps' / 'rag-mcp-chat-bridge-dependencies.tsv',
    M3_ROOT / 'ens-unified-migration-m3-rag-mcp-findings.json',
]

REQUIRED_STRINGS = [
    'ens_rag_search',
    'ens_rag_get_document',
    'ens_rag_get_course_context',
    'ens_rag_ingest_courses',
    'ens_rag_ingest_institutional',
    'ens_rag_ingest_marketing',
    'ens_rag_ingest_insights',
    'ens_rag_save_insight',
    'ens_rag_save_marketing_memory',
    'ens_rag_list_collections',
    'ens_rag_audit_recent',
    'GET /api/v1/rag/collections',
    'POST /api/v1/rag/search',
    'GET /api/v1/rag/documents/{document_id}',
    'AUTH_REQUIRED',
    'TOOL_ALLOWLIST',
    'COLLECTION_ALLOWLIST',
    'NO_DIRECT_FRONTEND_MCP_CALL',
    'SERVER_SIDE_PROVIDER_KEYS_ONLY',
    'INGESTION_ADMIN_ONLY',
]


class M3RagMcpContractDocsTest(unittest.TestCase):
    def test_required_docs_exist(self) -> None:
        for path in REQUIRED_DOCS:
            self.assertTrue(path.exists(), f'missing required doc: {path}')

    def test_contract_strings_are_present(self) -> None:
        corpus = "\n".join(
            path.read_text(encoding='utf-8') for path in REQUIRED_DOCS if path.suffix in {'.md', '.tsv', '.json'}
        )
        for needle in REQUIRED_STRINGS:
            self.assertIn(needle, corpus, f'missing contract string: {needle}')

    def test_tool_allowlist_is_exactly_ens_first(self) -> None:
        tool_contract = (M3_ROOT / 'contracts' / 'rag-mcp-tool-contract.md').read_text(encoding='utf-8')
        for needle in REQUIRED_STRINGS[:11]:
            self.assertIn(needle, tool_contract)
        self.assertNotIn('legacy', tool_contract.lower())
        self.assertNotIn('multi-tenant', tool_contract.lower())


if __name__ == '__main__':
    unittest.main()
