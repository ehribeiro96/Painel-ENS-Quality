from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from app.domains.macros.renderer import MacroRenderError, extract_placeholders, render_macro
from app.domains.macros.repository import normalize_query
from app.domains.macros.service import category_from_name, slugify

ROOT = Path(__file__).resolve().parents[1]
MACROS_IMPORTER = ROOT / "scripts" / "import_macros_json_to_postgres.py"
HINTS_IMPORTER = ROOT / "scripts" / "import_colaboradores_json_to_macro_hints.py"


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class MacrosModuleTest(unittest.TestCase):
    def test_slug_category_and_placeholders_for_asset_inventory_macro(self) -> None:
        name = "[Ativos] Atualizar inventário"
        template = "Patrimônio: {Patrimônio}\nUsuário Atual: {Usuário Atual}\nStatus: {Status}"

        self.assertEqual("ativos-atualizar-inventario", slugify(name))
        self.assertEqual("Ativos", category_from_name(name))
        self.assertEqual(["Patrimônio", "Usuário Atual", "Status"], extract_placeholders(template))

    def test_renderer_substitutes_placeholders_and_blocks_missing_required(self) -> None:
        rendered, pending = render_macro("Olá {Nome}. Status: {Status}", {"Nome": "Ana", "Status": "Resolvido"})

        self.assertEqual("Olá Ana. Status: Resolvido", rendered)
        self.assertEqual([], pending)
        with self.assertRaises(MacroRenderError) as ctx:
            render_macro("Olá {Nome}", {}, ["Nome"])
        self.assertEqual(["Nome"], ctx.exception.missing_fields)

    def test_renderer_can_preserve_missing_fields_when_required_list_is_empty(self) -> None:
        rendered, pending = render_macro("Patrimônio: {Patrimônio}\nLocal: {Local}", {"Patrimônio": "PAT-UAT-001"}, [])

        self.assertEqual("Patrimônio: PAT-UAT-001\nLocal: {Local}", rendered)
        self.assertEqual(["Local"], pending)

    def test_macros_json_analyze_maps_real_shape(self) -> None:
        importer = load_script(MACROS_IMPORTER, "macros_importer_test")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "macros.json"
            path.write_text(
                json.dumps(
                    {
                        "macros": [
                            {
                                "name": "[Ativos] Atualizar inventário",
                                "template_text": "Patrimônio: {Patrimônio}\nStatus: {Status}",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            candidates = importer.read_candidates(path)

        self.assertEqual(1, len(candidates))
        self.assertTrue(candidates[0].valid)
        self.assertEqual("ativos-atualizar-inventario", candidates[0].slug)
        self.assertEqual("Ativos", candidates[0].category)
        self.assertEqual(["Patrimônio", "Status"], candidates[0].required_fields)

    def test_macros_json_dict_shape_preserves_all_official_templates_and_diagnostics(self) -> None:
        importer = load_script(MACROS_IMPORTER, "macros_importer_dict_diagnostics_test")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "macros.json"
            path.write_text(
                json.dumps(
                    {
                        "[Suporte] Contato inicial": {"campos": ["Nome"], "texto": "Olá {Nome}"},
                        "[Suporte] Resolvido": {"campos": ["Nome"], "texto": "Resolvido {Nome}"},
                        "[Suporte] Continuar atendimento": {"campos": ["Nome"], "texto": "Continuando {Nome}"},
                        "[Suporte] Agendamento de Prova 0800": {"campos": ["Nome"], "texto": "Agendado {Nome}"},
                        "[Suporte] Tentativa de contato": {"campos": ["Nome"], "texto": "Tentativa {Nome}"},
                        "[Ativos] Atualizar inventário": {"campos": ["Patrimônio"], "texto": "Patrimônio {Patrimônio}"},
                        "[Infraestrutura] Encaminhamento": {"campos": ["Nome"], "texto": "Encaminhado {Nome}"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            candidates = importer.read_candidates(path)
            diagnostics = importer.build_candidate_diagnostics(candidates)

        self.assertEqual(7, len(candidates))
        self.assertEqual(7, diagnostics["total_candidates"])
        self.assertEqual(7, diagnostics["valid_candidates"])
        self.assertEqual(0, diagnostics["invalid_candidates"])
        self.assertEqual([], diagnostics["duplicate_slugs"])
        self.assertEqual([], diagnostics["invalid_macros"])
        self.assertIn("[Ativos] Atualizar inventário", diagnostics["names"])
        self.assertIn("[Infraestrutura] Encaminhamento", diagnostics["names"])
        self.assertIn("ativos-atualizar-inventario", diagnostics["slugs"])
        self.assertIn("infraestrutura-encaminhamento", diagnostics["slugs"])

    def test_colaboradores_json_loads_as_hints_only(self) -> None:
        importer = load_script(HINTS_IMPORTER, "macro_hints_importer_test")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "colaboradores.json"
            path.write_text(json.dumps(["Ana Teste", {"nome": "Bruno Teste"}]), encoding="utf-8")

            labels = importer.load_labels(path)

        self.assertEqual(["Ana Teste", "Bruno Teste"], labels)

    def test_macro_autocomplete_query_is_accent_insensitive(self) -> None:
        self.assertEqual("jose silva", normalize_query("José  Silva"))

    def test_macro_apply_requires_confirmation(self) -> None:
        importer = load_script(MACROS_IMPORTER, "macros_importer_confirm_test")
        with self.assertRaisesRegex(RuntimeError, "APPLY_MACROS_JSON"):
            import asyncio

            asyncio.run(importer.run(Path("missing.json"), "Apply", None, False))


if __name__ == "__main__":
    unittest.main()
