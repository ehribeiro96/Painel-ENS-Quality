from __future__ import annotations

from tests.operational_http import OperationalTestCase


class AssetsRegressionTest(OperationalTestCase):
    def test_user_asset_crud_search_filters_and_current_user_regression(self) -> None:
        user = self.create_user(prefix="colaborador.teste")
        asset = self.create_asset(
            hostname="RJMTEST001",
            patrimony=f"PAT-TEST-{user['id'][:8]}",
            serial=f"SN-TEST-{user['id'][:8]}",
            current_user_id=user["id"],
            status="IN_USE",
            location="Matriz",
        )
        self.assertEqual(asset["hostname"], "RJMTEST001")
        self.assertEqual(asset["current_user"]["email"], user["email"])

        by_hostname = self.client.get("/assets", params={"search": "RJMTEST001"})
        self.assertEqual(by_hostname.status_code, 200)
        self.assertGreaterEqual(by_hostname.json()["total"], 1)

        by_serial = self.client.get("/assets", params={"search": asset["serial"]})
        self.assertEqual(by_serial.status_code, 200)
        self.assertGreaterEqual(by_serial.json()["total"], 1)

        by_patrimony = self.client.get("/assets", params={"search": asset["patrimony"]})
        self.assertEqual(by_patrimony.status_code, 200)
        self.assertGreaterEqual(by_patrimony.json()["total"], 1)

        by_status = self.client.get("/assets", params={"status": "IN_USE"})
        self.assertEqual(by_status.status_code, 200)
        self.assertGreaterEqual(by_status.json()["total"], 1)

        by_location = self.client.get("/assets", params={"location": "Matriz"})
        self.assertEqual(by_location.status_code, 200)
        self.assertGreaterEqual(by_location.json()["total"], 1)

        updated = self.client.put(f"/assets/{asset['id']}", {"location": "Matriz - QA", "notes": "updated by regression"})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["location"], "Matriz - QA")

        linked = self.client.get(f"/users/{user['id']}/assets")
        self.assertEqual(linked.status_code, 200)
        self.assertGreaterEqual(len(linked.json()), 1)

    def test_rbac_viewer_cannot_create_asset(self) -> None:
        password = "ViewerPass123!"
        viewer = self.create_user(role="VIEWER", password=password, prefix="viewer.teste")
        viewer_session = self.client.session.__class__()
        login = viewer_session.post(
            f"{self.client.api}/auth/login",
            json={"email": viewer["email"], "password": password},
            timeout=20,
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]
        blocked = viewer_session.post(
            f"{self.client.api}/assets",
            json={"hostname": "VIEWERBLOCK", "asset_type": "NOTEBOOK", "status": "STOCK"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        self.assertEqual(blocked.status_code, 403)

    def test_asset_movement_history_and_audit(self) -> None:
        user = self.create_user(prefix="movimento.usuario")
        asset = self.create_asset(status="STOCK", location="Estoque")

        steps = [
            {"new_user_id": user["id"], "new_status": "IN_USE", "new_location": "Matriz", "justification": "Entrega regression"},
            {"new_user_id": None, "new_status": "MAINTENANCE", "new_location": "Assistencia", "justification": "Manutencao regression"},
            {"new_user_id": None, "new_status": "STOCK", "new_location": "Estoque", "justification": "Retorno regression"},
            {"new_user_id": None, "new_status": "DEFECTIVE", "new_location": "Estoque", "justification": "Defeito regression"},
        ]
        for step in steps:
            response = self.client.post(f"/assets/{asset['id']}/move", step)
            self.assertEqual(response.status_code, 200)

        history = self.client.get(f"/assets/{asset['id']}/history")
        self.assertEqual(history.status_code, 200)
        history_items = history.json()
        self.assertEqual(len(history_items), 4)
        self.assertEqual(history_items[0]["new_status"], "DEFECTIVE")
        first_assignment = history_items[-1]
        self.assertEqual(first_assignment["new_user_name"], user["name"])
        self.assertIsNotNone(first_assignment["responsible_name"])
        self.assertEqual(first_assignment["asset_label"], asset["hostname"])
        self.assertIn("macro_generation_id", first_assignment)

        invalid = self.client.post(
            f"/assets/{asset['id']}/move",
            {"new_status": "IN_USE", "new_location": "Matriz", "justification": "Sem usuario deve falhar"},
        )
        self.assertEqual(invalid.status_code, 422)

        audit = self.client.get("/audit-logs", params={"page": 1, "page_size": 100})
        self.assertEqual(audit.status_code, 200)
        actions = {item["action"] for item in audit.json()["items"]}
        self.assertIn("MOVE", actions)
        self.assertIn("CREATE", actions)

    def test_soft_delete_asset(self) -> None:
        asset = self.create_asset()
        deleted = self.client.delete(f"/assets/{asset['id']}")
        self.assertEqual(deleted.status_code, 204)
        fetched = self.client.get(f"/assets/{asset['id']}")
        self.assertEqual(fetched.status_code, 404)

    def test_soft_delete_user_preserves_contract(self) -> None:
        user = self.create_user(prefix="delete.usuario")
        deleted = self.client.delete(f"/users/{user['id']}")
        self.assertEqual(deleted.status_code, 204)
        fetched = self.client.get(f"/users/{user['id']}")
        self.assertEqual(fetched.status_code, 404)

    def test_duplicate_asset_identity_returns_409(self) -> None:
        asset = self.create_asset()
        duplicate = self.client.post(
            "/assets",
            {
                "hostname": "DUPLICATE-IDENTITY",
                "serial": asset["serial"],
                "asset_type": "NOTEBOOK",
                "status": "STOCK",
            },
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["detail"]["code"], "unique_constraint_violation")

    def test_without_user_filter_returns_only_unassigned_assets(self) -> None:
        user = self.create_user(prefix="assigned.filter")
        assigned = self.create_asset(current_user_id=user["id"], status="IN_USE")
        unassigned = self.create_asset(hostname=f"UNASSIGNED-{user['id'][:8]}", status="STOCK")

        response = self.client.get("/assets", params={"without_user": "true", "page_size": 200})
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()["items"]}
        self.assertIn(unassigned["id"], ids)
        self.assertNotIn(assigned["id"], ids)
