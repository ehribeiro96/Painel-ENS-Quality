from __future__ import annotations

import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace

from app.domains.macros.models import MacroGeneration
from app.domains.macros.service import MacroService
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[1]


class _NestedTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):  # noqa: ANN001
        return False


class _RaceSession:
    def __init__(self, winner) -> None:  # noqa: ANN001
        self.winner = winner
        self.scalar_calls = 0

    async def scalar(self, statement):  # noqa: ANN001, ARG002
        self.scalar_calls += 1
        return None if self.scalar_calls == 1 else self.winner

    def begin_nested(self):
        return _NestedTransaction()


class _RaceMacroService(MacroService):
    def __init__(self, session, template) -> None:  # noqa: ANN001
        super().__init__(session)
        self.template = template
        self.repository = SimpleNamespace(get_template=self._get_template)

    async def _get_template(self, template_id):  # noqa: ANN001, ARG002
        return self.template

    async def suggested_for_movement(self, movement_id):  # noqa: ANN001, ARG002
        return self.template, {"Patrimônio": "P-1"}, "macro", []

    async def generate(self, *args, **kwargs):  # noqa: ANN002, ANN003
        raise IntegrityError("insert macro", {}, Exception("uq_macro_generations_asset_movement"))


class MacroIdempotencyTest(unittest.IsolatedAsyncioTestCase):
    def test_model_has_partial_unique_index_for_asset_movement(self) -> None:
        index = next(index for index in MacroGeneration.__table__.indexes if index.name == "uq_macro_generations_asset_movement")

        self.assertTrue(index.unique)
        self.assertIn("asset_movement", str(index.dialect_options["postgresql"]["where"]))

    def test_migration_creates_the_asset_movement_unique_index(self) -> None:
        migration = (ROOT / "backend/alembic/versions/0007_macro_movement_unique.py").read_text(encoding="utf-8")

        self.assertIn('"uq_macro_generations_asset_movement"', migration)
        self.assertIn("unique=True", migration)
        self.assertIn("context_type = 'asset_movement' AND context_id IS NOT NULL", migration)

    async def test_concurrent_insert_loser_returns_the_single_persisted_generation(self) -> None:
        movement_id = uuid.uuid4()
        template = SimpleNamespace(id=uuid.uuid4())
        winner = SimpleNamespace(id=uuid.uuid4(), template_id=template.id, input_values={"Patrimônio": "P-1"})
        service = _RaceMacroService(_RaceSession(winner), template)

        generation, returned_template, values, pending = await service.generate_for_movement(movement_id, uuid.uuid4())

        self.assertIs(winner, generation)
        self.assertIs(template, returned_template)
        self.assertEqual(winner.input_values, values)
        self.assertEqual([], pending)


if __name__ == "__main__":
    unittest.main()
