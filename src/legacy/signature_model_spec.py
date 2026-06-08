from __future__ import annotations

import math
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

# Fonte unica de verdade para a assinatura canônica.
# Esses valores sao derivados do arquivo:
# assets/static/ASSINATURAS DE E-MAIL (ENS_LOGO_AZUL_LGPD_semTWITTER)_v21.23.docx
SIGNATURE_MODEL_SPEC: dict[str, object] = {
    "primary_color_hex": "009DB7",
    "primary_color_rgb": "rgb(0,157,183)",
    "disclaimer_color_hex": "767171",
    "disclaimer_color_rgb": "rgb(118,113,113)",
    "table_width_px": 718,
    "cell_widths_px": (151, 19, 547),
    "row_main_height_pt": 127.6,
    "row_spacer_height_pt": 8.8,
    "content_padding_pt": 5.4,
    "logo_size_px": (117, 167),
    "social_icon_size_px": (29, 29),
    "font_sizes_pt": {
        "name": 11.0,
        "title": 10.0,
        "phone": 11.0,
        "address": 9.0,
        "site": 14.0,
        "disclaimer": 6.5,
    },
}

AVISO_TEXTO_PT = (
    "Este e-mail, bem como os documentos e arquivos anexados a ele, contêm informações que podem ser confidenciais. "
    "Estas informações são para uso exclusivo do (s) destinatário(s) específico (s) cujo nome (s) aparece (em) na seção de cabeçalho do e-mail. "
    "Se você recebeu esta mensagem por engano, por favor, notifique o remetente imediatamente pelo retorno da mensagem e delete o arquivo e seus anexos. "
    "Você está sendo notificado que qualquer divulgação, cópia, distribuição ou adoção de qualquer ação decorrente da informação confidencial contida neste documento é estritamente proibida. "
    "Qualquer violação poderá ser penalizada por lei."
)

AVISO_TEXTO_EN = (
    "This e-mail, including the documents and files attached to it, contains confidential information that must be kept secret by law. "
    "This information is for the exclusive use of the specified recipient whose name appears in this transmission. "
    "If you have received this message by mistake, please notify us immediately by return e-mail and delete the file and its attachments. "
    "You are hereby notified that any dissemination, copying, distribution or adoption of any action arising from the confidential information contained herein is strictly prohibited. "
    "Any violation will be penalized by law."
)

CANONICAL_HTML_REQUIRED_MARKERS: tuple[str, ...] = (
    "width:718px",
    "height:127.6pt",
    "height:8.8pt",
    "font-size:11pt",
    "font-size:10pt",
    "font-size:9pt",
    "font-size:14pt",
    "font-size:6.5pt",
    "color:#009DB7",
    "color:rgb(0,157,183)",
    "color:#767171",
    "color:rgb(118,113,113)",
    "https://ens.edu.br",
    "IMPORTANTE",
    "IMPORTANT",
)


def map_pt_to_html_font_size(pt_value: float) -> str:
    if pt_value <= 8.5:
        return "1"
    if pt_value <= 10.5:
        return "2"
    if pt_value <= 12.5:
        return "3"
    if pt_value <= 14.5:
        return "4"
    if pt_value <= 18.0:
        return "5"
    if pt_value <= 24.0:
        return "6"
    return "7"


def _dxa_to_pt(value: int | str | None) -> float | None:
    if value is None:
        return None
    try:
        return round(int(value) / 20.0, 1)
    except Exception:
        return None


def _emu_to_px(value: int | str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(round(int(value) / 9525.0))
    except Exception:
        return None


def _first_run_text_props(paragraph: ET.Element, ns: dict[str, str]) -> tuple[str, str | None, str | None]:
    text = ""
    color = None
    sz = None
    for run in paragraph.findall("w:r", ns):
        run_text = "".join((t.text or "") for t in run.findall(".//w:t", ns))
        if not run_text.strip():
            continue
        text = run_text
        run_props = run.find("w:rPr", ns)
        if run_props is not None:
            node_color = run_props.find("w:color", ns)
            if node_color is not None:
                color = node_color.attrib.get(f"{{{ns['w']}}}val")
            node_sz = run_props.find("w:sz", ns)
            if node_sz is not None:
                sz = node_sz.attrib.get(f"{{{ns['w']}}}val")
        break
    return text, color, sz


def extract_docx_signature_tokens(docx_path: Path) -> dict[str, object]:
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))

    body = root.find("w:body", ns)
    if body is None:
        raise RuntimeError("Documento DOCX sem body.")
    table = body.find("w:tbl", ns)
    if table is None:
        raise RuntimeError("Documento DOCX sem tabela de assinatura.")

    rows = table.findall("w:tr", ns)
    if len(rows) < 2:
        raise RuntimeError("Estrutura inesperada de linhas no modelo DOCX.")

    row_main = rows[0]
    row_spacer = rows[1]
    row_disclaimer = rows[2] if len(rows) >= 3 else None

    row_main_height = None
    tr_pr = row_main.find("w:trPr", ns)
    if tr_pr is not None:
        tr_h = tr_pr.find("w:trHeight", ns)
        if tr_h is not None:
            row_main_height = _dxa_to_pt(tr_h.attrib.get(f"{{{ns['w']}}}val"))

    row_spacer_height = None
    tr_pr_2 = row_spacer.find("w:trPr", ns)
    if tr_pr_2 is not None:
        tr_h_2 = tr_pr_2.find("w:trHeight", ns)
        if tr_h_2 is not None:
            row_spacer_height = _dxa_to_pt(tr_h_2.attrib.get(f"{{{ns['w']}}}val"))

    row_main_cells = row_main.findall("w:tc", ns)
    if len(row_main_cells) < 3:
        raise RuntimeError("Estrutura inesperada de celulas no modelo DOCX.")

    cell_widths_dxa: list[int] = []
    for cell in row_main_cells[:3]:
        tc_pr = cell.find("w:tcPr", ns)
        tc_w = tc_pr.find("w:tcW", ns) if tc_pr is not None else None
        val = int(tc_w.attrib.get(f"{{{ns['w']}}}w", "0")) if tc_w is not None else 0
        cell_widths_dxa.append(val)

    text_cell = row_main_cells[2]
    paragraphs = text_cell.findall("w:p", ns)
    lines: list[tuple[str, str | None, str | None]] = []
    for paragraph in paragraphs:
        info = _first_run_text_props(paragraph, ns)
        if info[0].strip():
            lines.append(info)

    if len(lines) < 4:
        raise RuntimeError("Nao foi possivel extrair as linhas principais da assinatura no DOCX.")

    name_color = lines[0][1]
    title_size_hp = lines[1][2]
    phone_color = lines[2][1]
    address_size_hp = lines[3][2]

    # Link ens.edu.br
    site_font_hp = None
    for hyperlink in text_cell.findall(".//w:hyperlink", ns):
        txt = "".join((t.text or "") for t in hyperlink.findall(".//w:t", ns))
        if "ens.edu.br" in txt:
            run = hyperlink.find("w:r", ns)
            if run is not None:
                rpr = run.find("w:rPr", ns)
                if rpr is not None:
                    sz = rpr.find("w:sz", ns)
                    if sz is not None:
                        site_font_hp = sz.attrib.get(f"{{{ns['w']}}}val")
            break

    disclaimer_color = None
    disclaimer_hp = None
    if row_disclaimer is not None:
        first_disc_cell = row_disclaimer.find("w:tc", ns)
        if first_disc_cell is not None:
            for run in first_disc_cell.findall(".//w:r", ns):
                txt = "".join((t.text or "") for t in run.findall(".//w:t", ns)).strip()
                if not txt:
                    continue
                rpr = run.find("w:rPr", ns)
                if rpr is None:
                    continue
                node_color = rpr.find("w:color", ns)
                node_sz = rpr.find("w:sz", ns)
                if node_color is not None:
                    disclaimer_color = node_color.attrib.get(f"{{{ns['w']}}}val")
                if node_sz is not None:
                    disclaimer_hp = node_sz.attrib.get(f"{{{ns['w']}}}val")
                break

    extents = root.findall(".//wp:extent", ns)
    logo_px = (0, 0)
    icon_px = (0, 0)
    if extents:
        logo_px = (
            _emu_to_px(extents[0].attrib.get("cx")) or 0,
            _emu_to_px(extents[0].attrib.get("cy")) or 0,
        )
    if len(extents) > 1:
        icon_px = (
            _emu_to_px(extents[1].attrib.get("cx")) or 0,
            _emu_to_px(extents[1].attrib.get("cy")) or 0,
        )

    return {
        "primary_color_hex": (name_color or phone_color or "").upper(),
        "disclaimer_color_hex": (disclaimer_color or "").upper(),
        "title_font_pt": _dxa_to_pt(int(title_size_hp) * 10 if title_size_hp else None),
        "address_font_pt": _dxa_to_pt(int(address_size_hp) * 10 if address_size_hp else None),
        "site_font_pt": _dxa_to_pt(int(site_font_hp) * 10 if site_font_hp else None),
        "disclaimer_font_pt": _dxa_to_pt(int(disclaimer_hp) * 10 if disclaimer_hp else None),
        "table_width_px": int(math.ceil(sum(cell_widths_dxa) * 96.0 / 1440.0)),
        "cell_widths_px": tuple(int(round(v * 96.0 / 1440.0)) for v in cell_widths_dxa),
        "row_main_height_pt": row_main_height,
        "row_spacer_height_pt": row_spacer_height,
        "logo_size_px": logo_px,
        "social_icon_size_px": icon_px,
    }


def validate_docx_signature_baseline(docx_path: Path) -> list[str]:
    tokens = extract_docx_signature_tokens(docx_path)
    baseline = SIGNATURE_MODEL_SPEC
    issues: list[str] = []

    def _check_equal(key: str, expected: object, actual: object) -> None:
        if expected != actual:
            issues.append(f"{key}: esperado={expected!r} atual={actual!r}")

    _check_equal("primary_color_hex", baseline["primary_color_hex"], tokens.get("primary_color_hex"))
    _check_equal("disclaimer_color_hex", baseline["disclaimer_color_hex"], tokens.get("disclaimer_color_hex"))
    _check_equal("table_width_px", baseline["table_width_px"], tokens.get("table_width_px"))
    _check_equal("cell_widths_px", baseline["cell_widths_px"], tokens.get("cell_widths_px"))
    _check_equal("row_main_height_pt", baseline["row_main_height_pt"], tokens.get("row_main_height_pt"))
    _check_equal("row_spacer_height_pt", baseline["row_spacer_height_pt"], tokens.get("row_spacer_height_pt"))
    _check_equal("logo_size_px", baseline["logo_size_px"], tokens.get("logo_size_px"))
    _check_equal("social_icon_size_px", baseline["social_icon_size_px"], tokens.get("social_icon_size_px"))

    font_sizes = baseline.get("font_sizes_pt", {})
    _check_equal("title_font_pt", font_sizes.get("title"), tokens.get("title_font_pt"))
    _check_equal("address_font_pt", font_sizes.get("address"), tokens.get("address_font_pt"))
    _check_equal("site_font_pt", font_sizes.get("site"), tokens.get("site_font_pt"))
    _check_equal("disclaimer_font_pt", font_sizes.get("disclaimer"), tokens.get("disclaimer_font_pt"))
    return issues
