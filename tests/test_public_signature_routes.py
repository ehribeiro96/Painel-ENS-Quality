import unittest

from src.legacy.flask_app import criar_aplicativo


class PublicSignatureRoutesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = criar_aplicativo("publico")
        self.client = self.app.test_client()

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

    def test_routes_require_generated_signature(self):
        res_old = self.client.get("/assinatura/outlook-classico.html")
        res_new = self.client.get("/assinatura/outlook-new.html")
        self.assertEqual(400, res_old.status_code)
        self.assertEqual(400, res_new.status_code)

    def test_outlook_new_and_classic_return_expected_html(self):
        with self.client.session_transaction() as sess:
            sess["ultima_assinatura"] = self._sample_person()
            sess.pop("ultima_assinatura_token", None)

        res_old = self.client.get("/assinatura/outlook-classico.html")
        res_new = self.client.get("/assinatura/outlook-new.html")
        self.assertEqual(200, res_old.status_code)
        self.assertEqual(200, res_new.status_code)

        html_old = res_old.get_data(as_text=True)
        html_new = res_new.get_data(as_text=True)
        self.assertNotEqual(html_old, html_new)
        self.assertIn("width:718px", html_old)
        self.assertIn("https://ens.edu.br", html_old)
        self.assertIn("https://ens.edu.br", html_new)
        self.assertIn("font-size:14.67px", html_new)
        self.assertIn("IMPORTANTE", html_new)
        self.assertIn("IMPORTANT", html_new)
        self.assertNotIn("<font ", html_new.lower())


if __name__ == "__main__":
    unittest.main()
