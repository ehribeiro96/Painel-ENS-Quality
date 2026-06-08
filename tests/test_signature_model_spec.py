import unittest
from pathlib import Path

from src.legacy.signature_model_spec import (
    SIGNATURE_MODEL_SPEC,
    validate_docx_signature_baseline,
)


class SignatureModelSpecTests(unittest.TestCase):
    def test_docx_baseline_matches_frozen_spec(self):
        docx_path = Path("assets/static/ASSINATURAS DE E-MAIL (ENS_LOGO_AZUL_LGPD_semTWITTER)_v21.23.docx")
        self.assertTrue(docx_path.exists(), "Arquivo base de assinatura nao encontrado.")
        issues = validate_docx_signature_baseline(docx_path)
        self.assertEqual([], issues, f"Modelo DOCX divergiu do spec congelado: {issues}")

    def test_spec_has_expected_critical_tokens(self):
        self.assertEqual("009DB7", SIGNATURE_MODEL_SPEC["primary_color_hex"])
        self.assertEqual("767171", SIGNATURE_MODEL_SPEC["disclaimer_color_hex"])
        self.assertEqual(718, SIGNATURE_MODEL_SPEC["table_width_px"])
        self.assertEqual((151, 19, 547), SIGNATURE_MODEL_SPEC["cell_widths_px"])


if __name__ == "__main__":
    unittest.main()
