from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.api.v1.routes import users
from app.shared.enums import Role
from fastapi import HTTPException


def authorization_dependency(path: str, method: str):
    route = next(
        route
        for route in users.router.routes
        if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
    )
    return next(dependency.call for dependency in route.dependant.dependencies if dependency.name == "current_user")


class UserPermissionBoundariesTest(unittest.IsolatedAsyncioTestCase):
    async def test_technician_cannot_create_or_update_users(self) -> None:
        technician = SimpleNamespace(role=Role.TECHNICIAN)

        for path, method in (("/users", "POST"), ("/users/{user_id}", "PUT")):
            with self.subTest(path=path, method=method):
                with self.assertRaises(HTTPException) as raised:
                    await authorization_dependency(path, method)(technician)
                self.assertEqual(403, raised.exception.status_code)

    async def test_admin_can_create_update_and_delete_users(self) -> None:
        admin = SimpleNamespace(role=Role.ADMIN)

        for path, method in (("/users", "POST"), ("/users/{user_id}", "PUT"), ("/users/{user_id}", "DELETE")):
            with self.subTest(path=path, method=method):
                self.assertIs(admin, await authorization_dependency(path, method)(admin))


if __name__ == "__main__":
    unittest.main()
