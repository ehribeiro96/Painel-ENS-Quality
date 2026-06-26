# ENS Unified Migration M3 — RAG MCP Resource Contract

## Status
M3A_CONTRACT_ONLY

## Result of the external inventory
No MCP resources were registered in the external rag-mcp service.
search_files("registerResource|server.resource|mcp.resource") returned zero matches under src/.

## Contract decision
- Do not publish documents as public MCP resources in M3.
- Do not leak internal filesystem paths or collection directories through resource URIs.
- Treat document access as a backend-owned tool/HTTP concern only.
- Any future resource surface would need the same auth/RBAC/audit controls as the route contract.
