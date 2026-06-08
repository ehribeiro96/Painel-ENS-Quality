from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_legacy_ens_db_to_postgres.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("legacy_importer", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["legacy_importer"] = module
    spec.loader.exec_module(module)
    return module


class LegacyEnsDbImporterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = load_importer()

    def test_analyze_reads_sqlite_without_creating_users(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "ens.db"
            self._create_fixture_db(db_path)

            candidates, inventory = self.importer.read_candidates(db_path)

            self.assertEqual(4, len(candidates))
            self.assertEqual("LEGACY_SQLITE_SEED_SOURCE", "LEGACY_SQLITE_SEED_SOURCE")
            self.assertIn("colaboradores", inventory["columns"])
            self.assertEqual(4, inventory["quality"]["total_rows"])
            self.assertIn("password_hash", inventory["sensitive_fields_discarded"])
            self.assertIn("eh_admin", inventory["sensitive_fields_discarded"])
            self.assertIn("must_change", inventory["sensitive_fields_discarded"])

    def test_candidate_mapping_and_validation(self) -> None:
        row = self._row(
            id=1,
            name="Nome Antigo",
            nome_exibicao="Nome Assinatura",
            email="Pessoa.Teste@ENS.EDU.BR",
            role="Cargo",
            campo_assinatura="Assinatura Cargo",
            department="TI",
            telefone_ad="21999999999",
            status="off",
            matricula="pessoa.teste",
        )

        candidate = self.importer.candidate_from_row(row)

        self.assertTrue(candidate.valid)
        self.assertEqual("Nome Assinatura", candidate.name)
        self.assertEqual("pessoa.teste@ens.edu.br", candidate.email)
        self.assertEqual("Assinatura Cargo", candidate.job_title)
        self.assertEqual("TI", candidate.department)
        self.assertEqual("21999999999", candidate.phone)
        self.assertEqual("INACTIVE", candidate.status.value)
        self.assertEqual(1, candidate.metadata["source_record_id"])
        self.assertEqual("ens.db", candidate.metadata["source_database"])
        self.assertEqual("legacy_seed", candidate.metadata["import_mode"])
        self.assertEqual("pessoa.teste", candidate.metadata["login"])
        self.assertEqual("off", candidate.metadata["status_legacy"])
        self.assertNotIn("password_hash", candidate.metadata)
        self.assertNotIn("eh_admin", candidate.metadata)
        self.assertNotIn("must_change", candidate.metadata)

    def test_missing_email_and_missing_name_are_invalid(self) -> None:
        missing_email = self.importer.candidate_from_row(self._row(id=1, name="Pessoa", email=""))
        missing_name = self.importer.candidate_from_row(self._row(id=2, name="", nome_exibicao="", email="p@ens.edu.br"))

        self.assertFalse(missing_email.valid)
        self.assertIn("missing_email", missing_email.errors)
        self.assertFalse(missing_name.valid)
        self.assertIn("missing_name", missing_name.errors)

    def test_merge_does_not_overwrite_existing_non_empty_fields_with_empty_values(self) -> None:
        from app.domains.users.models import User

        existing = User(
            name="Nome Atual",
            email="pessoa@ens.edu.br",
            job_title="Cargo Atual",
            department="Departamento Atual",
            phone="1111",
        )
        candidate = self.importer.LegacyCandidate(
            source_record_id=1,
            name="Nome Legado",
            email="pessoa@ens.edu.br",
            job_title=None,
            department="",
            business_unit="RJ",
            manager_name=None,
            phone=None,
            status=self.importer.UserStatus.ACTIVE,
            login_hint=None,
            metadata={},
            valid=True,
            errors=[],
        )

        changed = self.importer.merge_user(existing, candidate)

        self.assertEqual("Nome Atual", existing.name)
        self.assertEqual("Cargo Atual", existing.job_title)
        self.assertEqual("Departamento Atual", existing.department)
        self.assertEqual("1111", existing.phone)
        self.assertEqual("legacy_ens_db", existing.source)
        self.assertEqual({"business_unit": "RJ", "source": "legacy_ens_db"}, changed)

    def test_sensitive_admin_update_is_identified_for_skip(self) -> None:
        from app.domains.users.models import User
        from app.shared.enums import Role

        existing = User(
            name="Admin Atual",
            email="admin@ens.edu.br",
            role=Role.ADMIN,
        )
        candidate = self.importer.LegacyCandidate(
            source_record_id=1,
            name="Admin Legado",
            email="admin@ens.edu.br",
            job_title="Cargo",
            department="TI",
            business_unit="RJ",
            manager_name="Gestor",
            phone="1234",
            status=self.importer.UserStatus.ACTIVE,
            login_hint="admin",
            metadata={"source_record_id": 1},
            valid=True,
            errors=[],
        )
        policy = self.importer.ImportPolicy(skip_sensitive_existing_users=True)

        changed = self.importer.planned_user_changes(existing, candidate)
        record = self.importer.sensitive_skip_record(existing, candidate, changed)

        self.assertTrue(self.importer.is_sensitive_existing_user(existing, policy))
        self.assertIn("job_title", changed)
        self.assertEqual("SKIPPED_SENSITIVE_ACCOUNT_UPDATE", record["reason"])
        self.assertEqual("skipped", record["decision"])
        self.assertIn("job_title", record["fields_that_would_update"])

    def test_apply_requires_explicit_confirmation(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "Apply requires"):
            import asyncio

            asyncio.run(self.importer.run(Path("missing.db"), "Apply", None))

    def test_user_model_has_source_fields(self) -> None:
        from app.domains.users.models import User

        self.assertTrue(hasattr(User, "source"))
        self.assertTrue(hasattr(User, "source_metadata"))

    def test_migration_adds_source_fields(self) -> None:
        migration = ROOT / "backend" / "alembic" / "versions" / "0004_add_user_source_metadata.py"
        content = migration.read_text(encoding="utf-8")

        self.assertIn('"source"', content)
        self.assertIn('"source_metadata"', content)
        self.assertIn("JSONB", content)

    def _create_fixture_db(self, path: Path) -> None:
        conn = sqlite3.connect(path)
        conn.execute(
            """
            create table colaboradores (
              id integer primary key,
              name text,
              department text,
              role text,
              phone text,
              email text unique,
              status text default 'on',
              updated_at text,
              eh_admin text default 'no',
              password_hash text,
              must_change text default 'no',
              matricula text,
              posicao_organograma text,
              first_name text,
              last_name text,
              nome_exibicao text,
              diretoria text,
              campo_assinatura text,
              manager text,
              telefone_ad text,
              local_descricao text,
              endereco text,
              uf text
            )
            """
        )
        for row in [
            self._row(id=1, name="Pessoa Um", email="p1@ens.edu.br"),
            self._row(id=2, name="Pessoa Dois", email="p2@ens.edu.br"),
            self._row(id=3, name="Sem Email", email=""),
            self._row(id=4, name="", nome_exibicao="", email="sem.nome@ens.edu.br"),
        ]:
            keys = list(row.keys())
            conn.execute(
                f"insert into colaboradores ({','.join(keys)}) values ({','.join(['?'] * len(keys))})",
                [row[key] for key in keys],
            )
        conn.commit()
        conn.close()

    def _row(self, **overrides):
        values = {
            "id": None,
            "name": "Pessoa",
            "department": "TI",
            "role": "Analista",
            "phone": "0000",
            "email": "pessoa@ens.edu.br",
            "status": "on",
            "updated_at": None,
            "eh_admin": "no",
            "password_hash": None,
            "must_change": "no",
            "matricula": "pessoa",
            "posicao_organograma": None,
            "first_name": None,
            "last_name": None,
            "nome_exibicao": None,
            "diretoria": None,
            "campo_assinatura": None,
            "manager": None,
            "telefone_ad": None,
            "local_descricao": None,
            "endereco": None,
            "uf": "RJ",
        }
        values.update(overrides)
        return values


if __name__ == "__main__":
    unittest.main()
