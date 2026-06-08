"""Gera uma pagina publica simulada usando o template index.html.

Script opcional para gerar HTML estatico (ex.: demonstracao sem Flask).
"""
from __future__ import annotations

import os
from pathlib import Path

import jinja2

from src.config.settings import data_dir, load_env_files, templates_dir

load_env_files()

DEFAULT_TEMPLATE_DIR = templates_dir()
DEFAULT_OUTPUT = data_dir() / "public_simulado.html"


def _fake_url_for(endpoint: str, **kwargs) -> str:
    """Versao simplificada de url_for para renderizacao estatica."""
    if endpoint == "static":
        filename = kwargs.get("filename", "")
        return f"static/{filename}"
    return "#"


def main() -> None:
    template_dir = Path(os.environ.get("PORTAL_TEMPLATE_DIR", DEFAULT_TEMPLATE_DIR))
    output_path = Path(os.environ.get("PORTAL_OUTPUT_PATH", DEFAULT_OUTPUT))

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template("index.html")

    # Contexto minimo para o template publico
    context = {
        "title": "Gerador de Assinaturas ENS",
        "hero_image_url": None,
        "hero_enabled": True,
        "termo_busca": "",
        "erro_busca": None,
        "colaborador": None,
        "colaborador_token": "",
        "html_assinatura": None,
        "USE_SMTP_EMAIL": False,
        "url_for": _fake_url_for,
    }

    html = template.render(**context)
    output_path.write_text(html, encoding="utf-8")
    print(f"Arquivo gerado: {output_path}")


if __name__ == "__main__":
    main()
