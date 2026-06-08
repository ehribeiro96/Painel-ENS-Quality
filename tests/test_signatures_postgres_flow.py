from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
BACKEND = str(ROOT / "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

import app.core.database.base  # noqa: E402,F401
from app.domains.signatures.service import SignatureService  # noqa: E402
from app.domains.users.models import User  # noqa: E402


class SignaturePostgresFlowTest(unittest.TestCase):
    def test_renderer_uses_canonical_user_fields_without_sqlite_dependency(self) -> None:
        user = User(
            name="Colaborador Teste",
            email="colaborador.teste@ens.edu.br",
            job_title="Analista de Suporte",
            department="Tecnologia da Informacao",
            business_unit="RJ",
            phone="+55 21 0000-0000",
        )

        html = SignatureService().render_html(user)

        self.assertIn("Colaborador Teste", html)
        self.assertIn("colaborador.teste@ens.edu.br", html)
        self.assertIn("Analista de Suporte", html)
        self.assertIn("Tecnologia da Informacao", html)
        self.assertIn("ens.edu.br", html)
        self.assertIn("IMPORTANTE", html)
        self.assertIn("IMPORTANT", html)

        source = inspect.getsource(SignatureService)
        self.assertNotIn("sqlite", source.lower())
        self.assertNotIn("ens.db", source.lower())

    def test_renderer_rejects_user_without_email(self) -> None:
        user = User(
            name="Colaborador Sem Email",
            email="",
            job_title="Analista",
            department="Tecnologia",
        )

        with self.assertRaises(HTTPException) as exc:
            SignatureService().render_html(user)

        self.assertEqual(422, exc.exception.status_code)
        self.assertEqual("signature_user_missing_email", exc.exception.detail["code"])


if __name__ == "__main__":
    unittest.main()
