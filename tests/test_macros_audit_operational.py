from __future__ import annotations

import requests

from tests.operational_http import OperationalTestCase


class MacrosAuditOperationalTest(OperationalTestCase):
    def test_macro_generate_copy_and_movement_audit_flow(self) -> None:
        templates = self.client.get("/macros/templates")
        self.assertEqual(templates.status_code, 200)
        support_template = next(item for item in templates.json() if item["slug"] == "suporte-contato-inicial")

        generated = self.client.post(
            "/macros/generate",
            {"template_id": support_template["id"], "values": {"Nome": "QA Operacional"}},
        )
        self.assertEqual(generated.status_code, 201)
        generation = generated.json()
        self.assertFalse(generation["copied"])
        self.assertIn("QA Operacional", generation["rendered_text"])

        copied = self.client.post(f"/macros/generations/{generation['id']}/copied")
        self.assertEqual(copied.status_code, 200)
        self.assertTrue(copied.json()["copied"])
        self.assertIsNotNone(copied.json()["copied_at"])

        no_token = requests.post(f"{self.client.api}/macros/generations/{generation['id']}/copied", timeout=20)
        self.assertEqual(no_token.status_code, 401)

        asset = self.create_asset(status="STOCK", location="Estoque")
        moved = self.client.post(
            f"/assets/{asset['id']}/move",
            {"new_status": "STOCK", "new_location": "Mesa QA", "justification": "Macro audit regression"},
        )
        self.assertEqual(moved.status_code, 200)

        suggested = self.client.get(f"/movements/{moved.json()['id']}/suggested-macro")
        self.assertEqual(suggested.status_code, 200)
        suggested_payload = suggested.json()
        self.assertEqual(suggested_payload["movement_id"], moved.json()["id"])
        self.assertIsNotNone(suggested_payload["generation_id"])
        self.assertGreaterEqual(len(suggested_payload["pending_fields"]), 1)

        audit = self.client.get("/audit-logs", params={"page": 1, "page_size": 200})
        self.assertEqual(audit.status_code, 200)
        events = {
            item["after"].get("event")
            for item in audit.json()["items"]
            if isinstance(item.get("after"), dict)
        }
        self.assertIn("macro_generated", events)
        self.assertIn("macro_copied", events)
        self.assertIn("asset_movement_macro_generated", events)
