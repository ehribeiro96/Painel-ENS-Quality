from __future__ import annotations

import base64
from html import escape
from pathlib import Path

from app.domains.users.models import User
from fastapi import HTTPException

DISCLAIMER_PT = (
    "Esta mensagem e seus anexos podem conter informacoes confidenciais ou "
    "privilegiadas. Caso voce nao seja o destinatario, nao divulgue, copie ou "
    "utilize seu conteudo."
)
DISCLAIMER_EN = (
    "This message and its attachments may contain confidential or privileged "
    "information. If you are not the intended recipient, do not disclose, copy "
    "or use its contents."
)

PRIMARY_COLOR = "#009DB7"
TEXT_COLOR = "#17324D"
DISCLAIMER_COLOR = "#767171"


def _asset_root() -> Path:
    return Path(__file__).resolve().parents[4] / "assets" / "static"


def _image_data_uri(*relative_candidates: str) -> str | None:
    root = _asset_root()
    for relative in relative_candidates:
        candidate = root / relative
        if not candidate.exists() or not candidate.is_file():
            continue
        suffix = candidate.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg" if suffix in {".jpg", ".jpeg"} else None
        if not mime:
            continue
        return f"data:{mime};base64,{base64.b64encode(candidate.read_bytes()).decode('ascii')}"
    return None


def _line(value: str | None, *, size: int, bold: bool = False, italic: bool = False) -> str:
    text = escape((value or "").strip()) or "&nbsp;"
    weight = "font-weight:700;" if bold else ""
    style = "font-style:italic;" if italic else ""
    return (
        "<tr>"
        f"<td style='padding:0 0 2px 0;font-family:Verdana,Arial,sans-serif;"
        f"font-size:{size}px;line-height:1.18;color:{TEXT_COLOR};{weight}{style}'>"
        f"{text}</td>"
        "</tr>"
    )


def _social_icon(name: str, href: str) -> str:
    src = _image_data_uri(f"icons/{name}.png", f"icons/{name.capitalize()}.png")
    if not src:
        return ""
    return (
        f"<a href='{href}' style='text-decoration:none;border:0;display:inline-block;margin-right:8px'>"
        f"<img src='{src}' width='24' height='24' alt='{escape(name)}' "
        "style='display:block;border:0;width:24px;height:24px'></a>"
    )


class SignatureService:
    def render_html(self, user: User) -> str:
        if not user.email:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "signature_user_missing_email",
                    "message": "O colaborador precisa ter e-mail para gerar assinatura.",
                },
            )

        logo_src = _image_data_uri("icons/Logo.png", "icons/logo.png")
        logo_html = (
            f"<img src='{logo_src}' width='136' height='64' alt='ENS' "
            "style='display:block;border:0;width:136px;height:auto'>"
            if logo_src
            else "<strong style='font-family:Verdana,Arial,sans-serif;color:#009DB7'>ENS</strong>"
        )
        title = user.job_title or user.department or ""
        department = user.department or ""
        unit = user.business_unit or ""
        phone = user.phone or ""
        social = "".join(
            [
                _social_icon("linkedin", "https://www.linkedin.com/school/ens/"),
                _social_icon("instagram", "https://www.instagram.com/ens.edu.br/"),
                _social_icon("youtube", "https://www.youtube.com/@ens"),
            ]
        )
        location_line = "ENS"
        if unit:
            location_line = f"ENS - {unit}"

        return f"""<!doctype html>
<html>
<body style="margin:0;padding:0;background:#ffffff">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="718" style="border-collapse:collapse;width:718px;max-width:718px;background:#ffffff">
  <tr>
    <td width="151" valign="middle" style="width:151px;padding:0 14px 0 0;vertical-align:middle">
      <a href="https://ens.edu.br" style="text-decoration:none;border:0">{logo_html}</a>
    </td>
    <td width="19" style="width:19px;font-size:1px;line-height:1">&nbsp;</td>
    <td width="548" valign="top" style="width:548px;padding:0 0 0 14px;border-left:2px solid {PRIMARY_COLOR};vertical-align:top">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-collapse:collapse;width:100%">
        {_line(user.name, size=16, bold=True)}
        {_line(title, size=13, italic=True)}
        {_line(department, size=12)}
        {_line(phone, size=12)}
        <tr>
          <td style="padding:6px 0 2px 0;font-family:Verdana,Arial,sans-serif;font-size:12px;line-height:1.2;color:{TEXT_COLOR}">
            <a href="mailto:{escape(user.email)}" style="color:{PRIMARY_COLOR};text-decoration:none">{escape(user.email)}</a>
          </td>
        </tr>
        {_line(location_line, size=11)}
        <tr><td style="padding:6px 0 0 0">{social}</td></tr>
        <tr>
          <td style="padding:2px 0 0 0;font-family:Verdana,Arial,sans-serif;font-size:12px;font-weight:700;line-height:1.2">
            <a href="https://ens.edu.br" style="color:{PRIMARY_COLOR};text-decoration:none">ens.edu.br</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td colspan="3" style="padding:12px 0 0 0;font-family:Verdana,Arial,sans-serif;font-size:9px;line-height:1.15;color:{DISCLAIMER_COLOR};text-align:justify">
      <strong>IMPORTANTE:</strong> {escape(DISCLAIMER_PT)}
      <br><br>
      <strong>IMPORTANT:</strong> {escape(DISCLAIMER_EN)}
    </td>
  </tr>
</table>
</body>
</html>"""
