from __future__ import annotations

from uuid import uuid4

from tests.operational_http import ROOT, OperationalTestCase

FIXTURES = ROOT / "tests" / "fixtures" / "imports"


class ImportsRegressionTest(OperationalTestCase):
    def upload_fixture(self, filename: str, endpoint: str = "/imports/spreadsheet/upload", import_mode: str = "INITIAL_LOAD") -> dict:
        path = FIXTURES / filename
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if filename.endswith(".xlsx") else "text/csv"
        with path.open("rb") as file_obj:
            response = self.client.session.post(
                f"{self.client.api}{endpoint}",
                headers=self.client.headers(),
                files={"file": (filename, file_obj, content_type)},
                data={"import_mode": import_mode},
                timeout=30,
            )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def upload_csv_content(self, filename: str, content: str) -> dict:
        response = self.client.session.post(
            f"{self.client.api}/imports/spreadsheet/upload",
            headers=self.client.headers(),
            files={"file": (filename, content.encode("utf-8"), "text/csv")},
            data={"import_mode": "INITIAL_LOAD"},
            timeout=30,
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_valid_duplicate_and_malicious_csv_imports(self) -> None:
        valid = self.upload_fixture("lansweeper_valid.csv")
        self.assertEqual(valid["total_rows"], 2)
        staging = self.client.get(f"/imports/{valid['id']}/staging")
        self.assertEqual(staging.status_code, 200)
        self.assertEqual(staging.json()["total"], 2)
        self.assertEqual(valid["created_rows"], 0, "upload must not apply assets before confirmation")

        duplicate = self.upload_fixture("itam_duplicate.csv")
        self.assertFalse(duplicate["report"]["can_apply"])
        self.assertGreaterEqual(duplicate["report"]["blocking_conflicts_count"], 1)
        conflicts = self.client.get(f"/imports/{duplicate['id']}/conflicts")
        self.assertEqual(conflicts.status_code, 200)
        self.assertGreaterEqual(len(conflicts.json()), 1)

        malicious = self.upload_fixture("lansweeper_formula_injection.csv")
        errors = self.client.get(f"/imports/{malicious['id']}/validation-errors")
        self.assertEqual(errors.status_code, 200)
        self.assertGreaterEqual(len(errors.json()), 1)

        imports = self.client.get("/imports")
        self.assertEqual(imports.status_code, 200)
        self.assertGreaterEqual(imports.json()["total"], 3)

        audit = self.client.get("/audit-logs", params={"page": 1, "page_size": 100})
        self.assertIn("IMPORT", {item["action"] for item in audit.json()["items"]})

    def test_spreadsheet_upload_preview_apply_and_xlsx(self) -> None:
        suffix = uuid4().hex[:8].upper()
        csv_job = self.upload_csv_content(
            f"itam_valid_{suffix}.csv",
            "\n".join(
                [
                    "Hostname,Usuário,E-mail do usuário,Fabricante,Modelo,Serial,Sistema operacional,IP,Último login,Localização,Patrimônio,Tipo de equipamento",
                    f"RJMIMP{suffix},Colaborador Import,colaborador.import@ens.edu.br,Dell,Latitude 5440,SN-IMP-{suffix},Windows 11,10.20.30.21,2026-06-01,Matriz,PAT-IMP-{suffix},Notebook",
                ]
            ),
        )
        self.assertEqual(csv_job["status"], "READY_TO_APPLY")
        preview = self.client.get(f"/imports/{csv_job['id']}/preview")
        self.assertEqual(preview.status_code, 200)
        self.assertGreaterEqual(len(preview.json()["items"]), 1)
        mapping_response = self.client.post(
            f"/imports/{csv_job['id']}/mapping",
            json={"mapping": csv_job["report"]["mapping_json"]},
        )
        self.assertEqual(mapping_response.status_code, 200, mapping_response.text)
        mapped_job = mapping_response.json()
        self.assertTrue(mapped_job["report"]["mapping_updated"])
        self.assertEqual(mapped_job["valid_rows"], csv_job["valid_rows"])
        self.assertEqual(mapped_job["invalid_rows"], csv_job["invalid_rows"])
        self.assertEqual(mapped_job["conflict_rows"], csv_job["conflict_rows"])

        apply_response = self.client.post(f"/imports/{csv_job['id']}/apply")
        self.assertEqual(apply_response.status_code, 200, apply_response.text)
        applied = apply_response.json()["job"]
        self.assertGreaterEqual(applied["created_rows"] + applied["updated_rows"], 1)

        assets = self.client.get("/assets", params={"search": f"RJMIMP{suffix}", "page_size": 10})
        self.assertEqual(assets.status_code, 200)
        self.assertGreaterEqual(assets.json()["total"], 1)

        xlsx_job = self.upload_fixture("itam_valid.xlsx")
        self.assertEqual(xlsx_job["total_rows"], 1)
        self.assertIn("detected_mapping", xlsx_job["report"])

        invalid_job = self.upload_fixture("itam_formula_injection.csv")
        errors = self.client.get(f"/imports/{invalid_job['id']}/validation-errors")
        self.assertEqual(errors.status_code, 200)
        self.assertGreaterEqual(len(errors.json()), 1)

    def test_lansweeper_real_shape_preview_and_safe_reimport(self) -> None:
        job = self.upload_fixture("lansweeper_real_shape.xlsx")
        report = job["report"]
        self.assertEqual(report["preset_name"], "Lansweeper Assets Export")
        self.assertEqual(report["preset_version"], "2026.06.ENS.1")
        self.assertIn("Coluna de patrimônio vazia", " ".join(report["warnings"]))
        self.assertIn("quality", report)
        self.assertIn("state", report["distributions"])
        self.assertEqual(report["detected_sheet"], "report")
        self.assertEqual(report["summary"]["rows_without_patrimony"], job["total_rows"])
        staging = self.client.get(f"/imports/{job['id']}/staging")
        self.assertEqual(staging.status_code, 200)
        first = staging.json()["items"][0]
        self.assertEqual(first["identity_confidence"], "HIGH")
        self.assertEqual(first["normalized_payload"]["source_metadata"]["imported_user_hint"], "ENS\\joao.silva")

        suffix = uuid4().hex[:8].upper()
        initial = self.upload_csv_content(
            f"lansweeper_initial_{suffix}.csv",
            "\n".join(
                [
                    "Name,Type,Custom1,Manufacturer,Model,Serialnumber,State,Location,Building,IP Address,OS,lastuser,Scanserver",
                    f"RJMSAFE{suffix},Windows,NOTEBOOK,Dell,Latitude,SN-SAFE-{suffix},Active,Matriz,RJ,10.40.1.10,Windows 11,ENS\\\\usuario,lansweeper",
                ]
            ),
        )
        applied = self.client.post(f"/imports/{initial['id']}/apply")
        self.assertEqual(applied.status_code, 200, applied.text)
        assets = self.client.get("/assets", params={"search": f"RJMSAFE{suffix}", "page_size": 1})
        asset = assets.json()["items"][0]
        self.assertEqual(asset["status"], "IN_USE")
        self.assertEqual(asset["location"], "MATRIZ")
        self.assertIsNone(asset["current_user_id"])

        reimport = self.client.session.post(
            f"{self.client.api}/imports/spreadsheet/upload",
            headers=self.client.headers(),
            files={
                "file": (
                    f"lansweeper_reimport_{suffix}.csv",
                    "\n".join(
                        [
                            "Name,Type,Custom1,Manufacturer,Model,Serialnumber,State,Location,Building,IP Address,OS,lastuser,Scanserver",
                            f"RJMSAFE{suffix},Windows,NOTEBOOK,Dell,Latitude 2,SN-SAFE-{suffix},Broken,Outra Sala,SP,10.40.1.20,Windows 11,Outro,lansweeper",
                        ]
                    ).encode("utf-8"),
                    "text/csv",
                )
            },
            data={"import_mode": "SAFE_REIMPORT"},
            timeout=30,
        )
        self.assertEqual(reimport.status_code, 201, reimport.text)
        reapplied = self.client.post(f"/imports/{reimport.json()['id']}/apply")
        self.assertEqual(reapplied.status_code, 200, reapplied.text)
        after = self.client.get(f"/assets/{asset['id']}").json()
        self.assertEqual(after["status"], "IN_USE")
        self.assertEqual(after["location"], "MATRIZ")
        self.assertIsNone(after["current_user_id"])
        self.assertEqual(after["model"], "LATITUDE 2")

        duplicate_apply = self.client.post(f"/imports/{reimport.json()['id']}/apply")
        self.assertEqual(duplicate_apply.status_code, 400)

    def test_preview_only_and_xlsm_are_blocked(self) -> None:
        preview = self.upload_fixture("lansweeper_real_shape.xlsx", import_mode="PREVIEW_ONLY")
        apply_response = self.client.post(f"/imports/{preview['id']}/apply")
        self.assertEqual(apply_response.status_code, 400)

        response = self.client.session.post(
            f"{self.client.api}/imports/spreadsheet/upload",
            headers=self.client.headers(),
            files={"file": ("blocked.xlsm", b"PK\x03\x04fake", "application/vnd.ms-excel.sheet.macroEnabled.12")},
            data={"import_mode": "INITIAL_LOAD"},
            timeout=30,
        )
        self.assertEqual(response.status_code, 400)

    def test_partial_apply_ignores_invalid_and_equivalent_duplicates(self) -> None:
        suffix = uuid4().hex[:8].upper()
        content = "\n".join(
            [
                "Hostname,Serial,Modelo,Tipo de equipamento,Último login",
                f"RJMPART{suffix},SN-PART-{suffix},Latitude,Notebook,2026-01-01",
                f"RJMPART{suffix},SN-PART-{suffix},Latitude,Notebook,2026-06-01",
                ",,,Notebook,2026-06-01",
            ]
        )
        job = self.upload_csv_content(f"partial_apply_{suffix}.csv", content)
        self.assertTrue(job["report"]["can_apply"])
        self.assertEqual(job["report"]["duplicate_rows_skipped"], 1)
        self.assertEqual(job["invalid_rows"], 1)
        staging = self.client.get(f"/imports/{job['id']}/staging")
        decisions = {item["decision"] for item in staging.json()["items"]}
        self.assertIn("SKIPPED_DUPLICATE_IN_FILE", decisions)
        self.assertIn("INVALID", decisions)
        errors = self.client.get(f"/imports/{job['id']}/validation-errors")
        error_keys = {(item["row_number"], item["field_name"], item["error_code"]) for item in errors.json()}
        self.assertEqual(len(error_keys), len(errors.json()))

        apply_response = self.client.post(f"/imports/{job['id']}/apply")
        self.assertEqual(apply_response.status_code, 200, apply_response.text)
        applied = apply_response.json()["job"]
        self.assertEqual(applied["created_rows"], 1)
        self.assertEqual(applied["skipped_rows"], 2)
        assets = self.client.get("/assets", params={"search": f"RJMPART{suffix}", "page_size": 5})
        self.assertEqual(assets.json()["total"], 1)
