"""
Composio MCP-like integration for Hermes.
Uses the Composio SDK to call any of the 2000+ toolkits via API.

Usage from Hermes:
    execute_code with:
    from composio_client import ComposioClient
    client = ComposioClient()
    result = client.call_action("GMAIL_FETCH_EMAILS", {})
"""

from __future__ import annotations

import os

import requests

COMPOSIO_BASE_URL = "https://backend.composio.dev/api/v3"


def _require_composio_api_key() -> str:
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        raise RuntimeError("COMPOSIO_API_KEY não configurada no ambiente.")
    return api_key


class ComposioClient:
    """Lightweight Composio client for calling actions via REST API v3."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or _require_composio_api_key()
        self.base_url = COMPOSIO_BASE_URL
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def list_toolkits(self, page: int = 1, page_size: int = 100) -> dict:
        """List all available toolkits."""
        response = requests.get(
            f"{self.base_url}/toolkits",
            params={"page": page, "page_size": page_size},
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def search_toolkits(self, query: str) -> list[dict]:
        """Search toolkits by name."""
        all_results = []
        page = 1
        while True:
            data = self.list_toolkits(page=page, page_size=100)
            items = data.get("items", [])
            for item in items:
                name = item.get("name", "").lower()
                slug = item.get("slug", "").lower()
                if query.lower() in name or query.lower() in slug:
                    all_results.append(item)
            if page >= data.get("total_pages", 1):
                break
            page += 1
        return all_results

    def list_actions(self, toolkit_slug: str) -> list[dict]:
        """List all actions for a specific toolkit."""
        response = requests.get(
            f"{self.base_url}/toolkits/{toolkit_slug}/actions",
            headers=self.headers,
            timeout=30,
        )
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        return data.get("items", data) if isinstance(data, dict) else data

    def call_action(self, toolkit_slug: str, action_slug: str, params: dict | None = None) -> dict:
        """Execute a specific action from a toolkit."""
        body = params or {}
        response = requests.post(
            f"{self.base_url}/toolkits/{toolkit_slug}/actions/{action_slug}/execute",
            json=body,
            headers=self.headers,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def get_toolkit_info(self, toolkit_slug: str) -> dict:
        """Get details about a specific toolkit."""
        response = requests.get(
            f"{self.base_url}/toolkits/{toolkit_slug}",
            headers=self.headers,
            timeout=30,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()


# Convenience functions for common toolkits
def gmail_search(query: str) -> dict:
    """Search Gmail."""
    client = ComposioClient()
    return client.call_action("gmail", "gmail_search_emails", {"query": query})


def outlook_search(query: str) -> dict:
    """Search Outlook."""
    client = ComposioClient()
    return client.call_action("outlook", "outlook_search_emails", {"query": query})


def excel_read(file_id: str) -> dict:
    """Read Excel file."""
    client = ComposioClient()
    return client.call_action("excel", "excel_read_file", {"file_id": file_id})


def github_list_repos() -> dict:
    """List GitHub repos."""
    client = ComposioClient()
    return client.call_action("github", "github_list_repositories", {})


def slack_list_channels() -> dict:
    """List Slack channels."""
    client = ComposioClient()
    return client.call_action("slack", "slack_list_channels", {})


def notion_search(query: str) -> dict:
    """Search Notion."""
    client = ComposioClient()
    return client.call_action("notion", "notion_search_pages", {"query": query})


if __name__ == "__main__":
    try:
        client = ComposioClient()
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1) from exc

    print("Testing Composio connection...")

    data = client.list_toolkits(page=1, page_size=10)
    print("\nFirst 10 toolkits:")
    for toolkit in data.get("items", []):
        print(f"  - {toolkit['name']} ({toolkit['slug']})")

    print(f"\nTotal: {data.get('total_items', '?')} toolkits available")
