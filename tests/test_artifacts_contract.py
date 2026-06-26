from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ArtifactContractTest(unittest.TestCase):
    def test_artifact_router_is_registered_and_auth_protected(self) -> None:
        import sys

        backend_path = str(ROOT / 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.api.v1.dependencies.auth import get_current_user, get_optional_current_user
        from app.main import app

        routes = {getattr(route, 'path', ''): route for route in app.routes}
        self.assertIn('/api/v1/artifacts', routes)
        self.assertIn('/api/v1/artifacts/{artifact_id}', routes)
        self.assertIn('/api/v1/artifacts/{artifact_id}/download-url', routes)
        self.assertIn('/api/v1/artifacts/download/{signed_token}', routes)

        def dependency_calls(path: str, method: str) -> set[object]:
            route = next(r for r in app.routes if getattr(r, 'path', '') == path and method in getattr(r, 'methods', set()))
            return {dep.call for dep in route.dependant.dependencies}

        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts', 'POST'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}/download-url', 'GET'))
        self.assertIn(get_current_user, dependency_calls('/api/v1/artifacts/{artifact_id}', 'DELETE'))
        self.assertIn(get_optional_current_user, dependency_calls('/api/v1/artifacts/download/{signed_token}', 'GET'))

    def test_artifact_storage_is_not_public_static(self) -> None:
        import sys

        backend_path = str(ROOT / 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from app.main import app

        route_paths = {getattr(route, 'path', '') for route in app.routes}
        self.assertNotIn('/data/artifacts/private', route_paths)
        self.assertNotIn('/data/artifacts/metadata.json', route_paths)
        self.assertNotIn('/files', route_paths)


if __name__ == '__main__':
    unittest.main()
