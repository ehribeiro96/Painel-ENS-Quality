from __future__ import annotations

import base64
import os
from pathlib import Path

import jinja2

from src.config.settings import data_dir, load_env_files, static_dir, templates_dir
from .assets_base64 import ASSETS as BASE64_ASSETS

load_env_files()

TEMPLATE_DIR = Path(os.environ.get("PORTAL_TEMPLATE_DIR", templates_dir()))
ICONS_DIR = Path(os.environ.get("PORTAL_ICONS_DIR", static_dir() / "icons"))
OUTPUT_PATH = Path(os.environ.get("PORTAL_OUTPUT_PATH", data_dir() / "public_icones.html"))

env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


def url_for(endpoint: str, filename: str | None = None, **kwargs) -> str:
    if endpoint == "static" and filename:
        return f"static/{filename}"
    if endpoint.startswith("public."):
        return f"/{endpoint.split('.', 1)[1]}"
    if endpoint.startswith("admin."):
        return f"/admin/{endpoint.split('.', 1)[1]}"
    return f"/{endpoint}"


def load_icon(name: str) -> str:
    for fname in (f"{name}.png", f"{name.capitalize()}.png"):
        file_path = ICONS_DIR / fname
        if file_path.exists():
            data = file_path.read_bytes()
            encoded = base64.b64encode(data).decode("ascii")
            return f"data:image/png;base64,{encoded}"
    return BASE64_ASSETS.get(name.lower(), "")


def build_preview() -> str:
    logo_uri = load_icon("Logo") or BASE64_ASSETS.get("logo", "")
    icons = {n: load_icon(n) for n in ["facebook", "instagram", "linkedin", "tiktok", "youtube"]}
    name = "Gislaine Soares"
    role = "Comercial"
    phone = "(21) 3380-1536"
    address_line = "Rua Senador Dantas, 74 - 3\u00ba andar | Centro - Rio de Janeiro - RJ - 20031-205"

    rows: list[str] = []
    rows.append(
        "<table role='presentation' cellpadding='0' cellspacing='0' border='0' "
        "style='border-collapse:collapse;width:768px;font-family:Verdana,Arial,sans-serif;color:#009DB7;'>"
    )
    rows.append("<tr style='height:127.6pt'>")
    if logo_uri:
        logo_html = (
            f"<a href='https://ens.edu.br' style='text-decoration:none;border:0;'>"
            f"<img src='{logo_uri}' width='117' height='167' style='display:block;border:0;width:117px;height:167px' alt='Logotipo ENS'></a>"
        )
    else:
        logo_html = "&nbsp;"
    rows.append(
        "<td valign='top' width='151' style='width:113.35pt;padding:0 5.4pt 0 5.4pt;height:127.6pt'>"
        f"{logo_html}"
        "</td>"
    )
    rows.append(
        "<td width='19' valign='top' style='width:14.2pt;padding:0;'>"
        "<div style='line-height:115%;font-family:Verdana,Arial,sans-serif;color:#009DB7'>&nbsp;</div>"
        "</td>"
    )
    rows.append("<td width='547' valign='top' style='width:410.55pt;padding:0 5.4pt 0 5.4pt;height:127.6pt'>")
    rows.append(f"<div style='font-weight:bold;font-size:11pt;line-height:1.15;margin:0;'>{name}</div>")
    rows.append(f"<div style='font-style:italic;font-size:10pt;line-height:1.15;margin:0;'>{role}</div>")
    rows.append(f"<div style='font-size:11pt;line-height:1.15;margin:0;'>{phone}</div>")
    rows.append("<div style='font-style:italic;font-size:10pt;line-height:1.15;margin:0;'>&nbsp;</div>")
    rows.append(f"<div style='font-size:9pt;line-height:1.15;margin:0;'>{address_line}</div>")
    rows.append(
        "<div style='font-size:14pt;line-height:1.15;margin:0;'>"
        "<a href='https://ens.edu.br' style='color:#009DB7;text-decoration:none;font-weight:bold;'>ens.edu.br</a>"
        "</div>"
    )
    icon_links = []
    icon_urls = {
        "facebook": "https://www.facebook.com/EscolaDeNegociosESeguros",
        "instagram": "https://www.instagram.com/oficial.ens/",
        "linkedin": "https://www.linkedin.com/school/5402791",
        "tiktok": "https://www.tiktok.com/@oficial.ens",
        "youtube": "https://www.youtube.com/channel/UCWKYHpO2GdJ7nfxuNx3XctQ",
    }
    for name, href in icon_urls.items():
        src = icons.get(name, "")
        if not src:
            continue
        icon_links.append(
            f"<a href='{href}'><img src='{src}' width='29' height='29' style='margin-right:8px;border:0;display:inline-block' alt='{name.title()}'></a>"
        )
    if icon_links:
        rows.append("<div style='margin-top:10px;'>" + "".join(icon_links) + "</div>")
    rows.append("</td>")
    rows.append("</tr>")
    rows.append(
        "<tr><td colspan='3' style='height:8.8pt;padding:0 5.4pt 0 5.4pt;'>"
        "<div style='line-height:115%;font-family:Verdana,Arial,sans-serif;color:#009DB7'>&nbsp;</div>"
        "</td></tr>"
    )
    disclaimer_pt = (
        "<b>IMPORTANTE</b>: Este e-mail e seus anexos podem conter informacoes confidenciais, "
        "de uso exclusivo do(s) destinatario(s) indicado(s). Se voce recebeu esta mensagem por engano, "
        "avise o remetente e apague o conteudo. Qualquer divulgacao, copia ou distribuicao "
        "nao autorizada e proibida e pode gerar responsabilizacao legal."
    )
    rows.append(
        "<tr><td colspan='3' style='border-top:0;padding:8px 5.4pt 0 5.4pt;font-size:6.5pt;line-height:105%;"
        "color:#767171;text-align:justify;'>"
        + disclaimer_pt
        + "</td></tr>"
    )
    rows.append("</table>")
    return "".join(rows)


def main() -> None:
    preview_html = build_preview()
    html = env.get_template("index.html").render(
        title="Gerador de Assinatura ENS",
        hero_image_url=None,
        colaborador=None,
        colaborador_token="",
        erro_busca="",
        termo_busca="",
        html_assinatura=preview_html,
        USE_SMTP_EMAIL=False,
        url_for=url_for,
    )
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Arquivo gerado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
