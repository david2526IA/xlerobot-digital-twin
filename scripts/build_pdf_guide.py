"""Build the polished XLeRobot 0.4 operating guide as a PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "GUIA_PRUEBAS_COMPLETA.md"
OUTPUT = ROOT / "output" / "pdf" / "Guia_XLeRobot_v0.4_Simulacion.pdf"

NAVY = colors.HexColor("#071A2F")
BLUE = colors.HexColor("#146EF5")
CYAN = colors.HexColor("#26C6DA")
PALE = colors.HexColor("#EAF3FF")
INK = colors.HexColor("#17263A")
MUTED = colors.HexColor("#5D6B7A")
LINE = colors.HexColor("#D8E2EE")
GREEN = colors.HexColor("#0B8F66")
AMBER = colors.HexColor("#D97706")
WHITE = colors.white


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        Path("C:/Windows/Fonts/aptos.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/aptos-bold.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    ]
    mono_candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/cour.ttf"),
    ]
    regular = next((p for p in candidates if p.exists()), None)
    bold = next((p for p in bold_candidates if p.exists()), None)
    mono = next((p for p in mono_candidates if p.exists()), None)
    if regular and bold:
        pdfmetrics.registerFont(TTFont("GuideSans", str(regular)))
        pdfmetrics.registerFont(TTFont("GuideSansBold", str(bold)))
        pdfmetrics.registerFontFamily("GuideSans", normal="GuideSans", bold="GuideSansBold")
        regular_name, bold_name = "GuideSans", "GuideSansBold"
    else:
        regular_name, bold_name = "Helvetica", "Helvetica-Bold"
    if mono:
        pdfmetrics.registerFont(TTFont("GuideMono", str(mono)))
        mono_name = "GuideMono"
    else:
        mono_name = "Courier"
    return regular_name, bold_name, mono_name


REGULAR, BOLD, MONO = register_fonts()


def styles():
    s = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body", parent=s["BodyText"], fontName=REGULAR, fontSize=9.3,
            leading=13.4, textColor=INK, spaceAfter=3.2 * mm,
        ),
        "h1": ParagraphStyle(
            "H1", parent=s["Heading1"], fontName=BOLD, fontSize=20,
            leading=23, textColor=NAVY, spaceBefore=7 * mm, spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "H2", parent=s["Heading2"], fontName=BOLD, fontSize=13.2,
            leading=16, textColor=BLUE, spaceBefore=5 * mm, spaceAfter=2.5 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=s["BodyText"], fontName=REGULAR, fontSize=9.1,
            leading=12.8, textColor=INK, leftIndent=5 * mm, firstLineIndent=-3.5 * mm,
            bulletIndent=0, spaceAfter=1.5 * mm,
        ),
        "step": ParagraphStyle(
            "Step", parent=s["BodyText"], fontName=REGULAR, fontSize=9.1,
            leading=12.8, textColor=INK, leftIndent=7 * mm, firstLineIndent=-5 * mm,
            spaceAfter=1.7 * mm,
        ),
        "code": ParagraphStyle(
            "Code", parent=s["Code"], fontName=MONO, fontSize=7.4,
            leading=10.5, textColor=colors.HexColor("#DDF4FF"),
            backColor=NAVY, borderColor=NAVY, borderWidth=0.5,
            borderPadding=(3 * mm, 3 * mm, 3 * mm, 3 * mm),
            spaceBefore=1 * mm, spaceAfter=3.4 * mm,
        ),
        "small": ParagraphStyle(
            "Small", parent=s["BodyText"], fontName=REGULAR, fontSize=7.8,
            leading=10.5, textColor=MUTED,
        ),
        "toc": ParagraphStyle(
            "TOC", parent=s["BodyText"], fontName=REGULAR, fontSize=10.3,
            leading=15, textColor=INK, leftIndent=7 * mm,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=s["Title"], fontName=BOLD, fontSize=30,
            leading=34, textColor=WHITE, alignment=TA_LEFT,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub", parent=s["BodyText"], fontName=REGULAR, fontSize=13,
            leading=18, textColor=colors.HexColor("#CFE7FF"),
        ),
        "label": ParagraphStyle(
            "Label", parent=s["BodyText"], fontName=BOLD, fontSize=8,
            leading=10, textColor=BLUE, uppercase=True,
        ),
    }


ST = styles()


def inline_markup(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(r"`([^`]+)`", r'<font name="%s">\1</font>' % MONO, value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def code_box(lines: list[str]) -> Paragraph:
    content = "<br/>".join(html.escape(line).replace(" ", "&nbsp;") for line in lines)
    return Paragraph(content or "&nbsp;", ST["code"])


def make_table(rows: list[list[str]], widths=None) -> Table:
    data = []
    for r_index, row in enumerate(rows):
        data.append([
            Paragraph(inline_markup(cell), ParagraphStyle(
                f"cell{r_index}", parent=ST["small"], fontName=BOLD if r_index == 0 else REGULAR,
                textColor=WHITE if r_index == 0 else INK, leading=10.2,
            )) for cell in row
        ])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F4F8FC")]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8 * mm),
    ]))
    return table


def callout(title: str, text: str, color=BLUE) -> Table:
    content = Paragraph(f'<font name="{BOLD}" color="{color.hexval()}">{html.escape(title)}</font><br/>{inline_markup(text)}', ST["body"])
    t = Table([[content]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, color),
        ("LINEBEFORE", (0, 0), (0, -1), 4, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
    ]))
    return t


def parse_markdown(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph: list[str] = []
    table_rows: list[list[str]] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), ST["body"]))
            paragraph = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            if len(table_rows) > 1 and all(set(c.strip()) <= {"-", ":"} for c in table_rows[1]):
                table_rows.pop(1)
            cols = len(table_rows[0])
            widths = [170 * mm / cols] * cols
            story.extend([make_table(table_rows, widths), Spacer(1, 3 * mm)])
            table_rows = []

    for line in lines[1:]:
        if line.startswith("```"):
            flush_paragraph(); flush_table()
            if in_code:
                story.append(code_box(code_lines)); code_lines = []
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            table_rows.append([c.strip() for c in line.strip("|").split("|")])
            continue
        flush_table()
        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[3:]), ST["h1"]))
        elif line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), ST["h2"]))
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            number, text = line.split(". ", 1)
            story.append(Paragraph(f'<font name="{BOLD}" color="{BLUE.hexval()}">{number}.</font> {inline_markup(text)}', ST["step"]))
        elif line.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(f'<font color="{BLUE.hexval()}">-</font> {inline_markup(line[2:])}', ST["bullet"]))
        elif not line.strip():
            flush_paragraph()
        else:
            paragraph.append(line.strip())
    flush_paragraph(); flush_table()
    return story


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(filename, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
                         topMargin=19 * mm, bottomMargin=18 * mm,
                         title="Guia XLeRobot v0.4 - Simulacion, teleoperacion y entrenamiento",
                         author="Proyecto XLeRobot Digital Twin")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        if doc.page == 1:
            return
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 10 * mm, A4[0], 10 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#CFE7FF"))
        canvas.setFont(REGULAR, 7.5)
        canvas.drawString(20 * mm, A4[1] - 6.5 * mm, "XLEROBOT 0.4  /  GUIA DE PUESTA EN MARCHA")
        canvas.setStrokeColor(LINE)
        canvas.line(20 * mm, 12 * mm, A4[0] - 20 * mm, 12 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont(REGULAR, 7.5)
        canvas.drawString(20 * mm, 7.5 * mm, "MuJoCo + Isaac Sim | Simulacion segura")
        canvas.drawRightString(A4[0] - 20 * mm, 7.5 * mm, f"{doc.page}")
        canvas.restoreState()


def cover_story():
    overview = ROOT / "outputs" / "xlerobot_v04_overview.png"
    front = ROOT / "outputs" / "xlerobot_v04_front.png"
    head = ROOT / "outputs" / "xlerobot_v04_head.png"
    hero = Image(str(overview), width=91 * mm, height=91 * mm) if overview.exists() else Spacer(1, 80 * mm)
    title = [
        Paragraph("GEMELO DIGITAL", ST["label"]),
        Spacer(1, 4 * mm),
        Paragraph("XLeRobot 0.4", ST["cover_title"]),
        Spacer(1, 4 * mm),
        Paragraph("Guía completa de puesta en marcha, teleoperación, datasets y entrenamiento", ST["cover_sub"]),
        Spacer(1, 9 * mm),
        Paragraph("MUJOCO  /  ISAAC SIM  /  GAMEPAD  /  RL", ParagraphStyle(
            "cover_meta", parent=ST["small"], fontName=BOLD, fontSize=8.5,
            leading=11, textColor=CYAN,
        )),
    ]
    title_block = Table([[title, hero]], colWidths=[91 * mm, 91 * mm], rowHeights=[113 * mm])
    title_block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 9 * mm),
        ("RIGHTPADDING", (0, 0), (0, 0), 7 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story = [title_block, Spacer(1, 8 * mm)]
    if front.exists() and head.exists():
        thumbs = Table([
            [Image(str(front), width=80 * mm, height=53 * mm), Image(str(head), width=80 * mm, height=53 * mm)],
            [Paragraph("Base 0.4: ruedas motrices exteriores", ST["small"]), Paragraph("Cuello, cámara y manipuladores", ST["small"])],
        ], colWidths=[85 * mm, 85 * mm])
        thumbs.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 1 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
        ]))
        story.append(thumbs)
    story.extend([
        Spacer(1, 8 * mm),
        callout("ESTADO DEL PROYECTO", "Modelo funcional para simulación. La geometría y la cadena cinemática están integradas; la fidelidad física absoluta exige completar las mediciones del robot real.", GREEN),
        PageBreak(),
    ])
    return story


def quick_start():
    items = [
        ["01", "Preparar", "Ejecuta bootstrap.ps1 sólo si no existe .venv."],
        ["02", "Verificar", "Ejecuta verify.ps1. No entrenes si alguna prueba falla."],
        ["03", "Ver", "Genera las tres capturas y revisa ruedas, cámara y brazos."],
        ["04", "Mover", "Teleopera MuJoCo con A como hombre muerto y B como E-stop."],
        ["05", "Repetir", "Regenera el USD y ejecuta el smoke test de Isaac Sim."],
        ["06", "Aprender", "Crea datasets; después prueba CEM y PPO."],
    ]
    rows = []
    for n, title, text in items:
        rows.append([
            Paragraph(f'<font name="{BOLD}" color="{BLUE.hexval()}" size="16">{n}</font>', ST["body"]),
            Paragraph(f'<font name="{BOLD}">{title}</font><br/>{text}', ST["body"]),
        ])
    t = Table(rows, colWidths=[16 * mm, 154 * mm])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, colors.HexColor("#F4F8FC")]),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
    ]))
    return [
        Paragraph("Ruta rápida", ST["h1"]),
        Paragraph("Si quieres comprobar hoy mismo que toda la cadena funciona, sigue estas seis fases en orden.", ST["body"]),
        t,
        Spacer(1, 5 * mm),
        callout("REGLA DE ORO", "Primero verifica y teleopera; después genera datos; sólo entonces entrena. El robot físico queda fuera de esta guía y no recibe órdenes.", AMBER),
    ]


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = GuideDoc(str(OUTPUT))
    story = cover_story()
    story += [
        Paragraph("Contenido", ST["h1"]),
        Paragraph("1  Preparación y verificación", ST["toc"]),
        Paragraph("2  Inspección del gemelo 0.4", ST["toc"]),
        Paragraph("3  Teleoperación en MuJoCo", ST["toc"]),
        Paragraph("4  Importación y teleoperación en Isaac Sim", ST["toc"]),
        Paragraph("5  Datasets y formato LeRobot", ST["toc"]),
        Paragraph("6  Entrenamiento CEM y PPO", ST["toc"]),
        Paragraph("7  Casos de uso, calibración y sim-to-real", ST["toc"]),
        Paragraph("8  Diagnóstico y seguridad", ST["toc"]),
        Spacer(1, 9 * mm),
    ]
    story += quick_start()
    story.append(PageBreak())
    story += parse_markdown(SOURCE)
    story += [
        Spacer(1, 5 * mm),
        callout("RESULTADO ESPERADO", "Al completar la ruta tendrás el mismo robot articulado en MuJoCo e Isaac Sim, teleoperación segura con gamepad, captura de observaciones y acciones, y dos rutas de entrenamiento reproducibles.", GREEN),
    ]
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
