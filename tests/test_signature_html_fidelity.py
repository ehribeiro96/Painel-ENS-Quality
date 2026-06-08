import unittest

from src.legacy.flask_app import (
    _assert_html_assinatura_canonica,
    assinatura_html_outlook_new,
    assinatura_html_precisa,
)
from src.legacy.signature_model_spec import CANONICAL_HTML_REQUIRED_MARKERS


class SignatureHtmlFidelityTests(unittest.TestCase):
    def _sample_person(self) -> dict[str, str]:
        return {
            "name": "Fulano de Tal",
            "nome_exibicao": "Fulano de Tal",
            "department": "Diretoria",
            "role": "Presidente",
            "phone": "(21) 3380-1001",
            "endereco": "Rua Senador Dantas, 74 - 3o andar | Centro - Rio de Janeiro - RJ - 20031-205",
            "address_type": "rio",
        }

    def test_canonical_html_contains_required_markers(self):
        html = assinatura_html_precisa(self._sample_person())
        for marker in CANONICAL_HTML_REQUIRED_MARKERS:
            self.assertIn(marker, html, f"Token canonico ausente: {marker}")
        self.assertIn("font-size:14pt", html)
        self.assertIn("https://ens.edu.br", html)
        _assert_html_assinatura_canonica(html)

    def test_outlook_new_generates_dedicated_compatible_html(self):
        sample = self._sample_person()
        html_classico = assinatura_html_precisa(sample)
        html_new = assinatura_html_outlook_new(sample)
        self.assertNotEqual(html_classico, html_new)
        self.assertTrue(html_new.strip().startswith("<table"))
        self.assertIn("https://ens.edu.br", html_new)
        self.assertIn("color:#009DB7", html_new)
        self.assertIn("color:#767171", html_new)
        self.assertIn("font-size:14.67px", html_new)
        self.assertIn("IMPORTANTE", html_new)
        self.assertIn("IMPORTANT", html_new)
        self.assertNotIn("<font ", html_new.lower())


if __name__ == "__main__":
    unittest.main()
