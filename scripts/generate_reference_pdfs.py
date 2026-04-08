"""
M2 Community Node — Reference PDF Generator
Produces one PDF from the docs/ markdown source files:

  M2_Community_Node_Troubleshooting.pdf
    Troubleshooting guide (standalone — useful at events)

Run: python scripts/generate_reference_pdfs.py
"""

import os
import re
import sys

_os = os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)
DOCS_DIR   = os.path.join(ROOT_DIR, "docs")
FONTS      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame,
        Paragraph, Spacer, HRFlowable, KeepTogether,
        Table, TableStyle, Preformatted, PageBreak, NextPageTemplate
    )
    from reportlab.platypus.flowables import Flowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("ERROR: pip install reportlab")
    sys.exit(1)


# ── Colors ───────────────────────────────────────────────────────────────────

ACCENT     = HexColor("#921212")
BG         = HexColor("#ffffff")
TEXT       = HexColor("#0f0f0f")
MUTED      = HexColor("#4a4a4a")
RULE       = HexColor("#dcc8c8")
CARD_BG    = HexColor("#faf6f6")
HDR_BAR    = HexColor("#921212")
H2_BG      = HexColor("#faf6f6")
CODE_BG    = HexColor("#faf6f6")
CODE_TEXT  = HexColor("#0f0f0f")
TABLE_HEAD = HexColor("#921212")
TABLE_ALT  = HexColor("#faf6f6")

PAGE_W, PAGE_H = letter
MARGIN = 0.7 * inch


# ── Font registration ────────────────────────────────────────────────────────

def _reg(name, filename):
    path = os.path.join(FONTS, filename)
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont(name, path))
        return True
    return False

_reg("BigShoulders", "BigShoulders-Bold.ttf")
_reg("Sans",         "InstrumentSans-Regular.ttf")
_reg("SansBold",     "InstrumentSans-Bold.ttf")
_reg("SansIt",       "InstrumentSans-Italic.ttf")
_reg("JuraMed",      "Jura-Medium.ttf")
_reg("Mono",         "IBMPlexMono-Regular.ttf")
_reg("MonoBold",     "IBMPlexMono-Bold.ttf")


# ── Section tracking ─────────────────────────────────────────────────────────

section_registry = {}


class SectionMark(Flowable):
    """Zero-height marker that records the current section for the footer."""
    def __init__(self, name):
        super().__init__()
        self.name  = name
        self.width = 0
        self.height = 0

    def draw(self):
        page = self.canv._doctemplate.page
        section_registry[page] = self.name


# ── Page callbacks ────────────────────────────────────────────────────────────

def on_page(canvas, doc):
    """Header + footer for all content pages."""
    page_num = doc.page
    section  = section_registry.get(page_num, "")
    canvas.saveState()

    # ACCENT header bar (skip title page)
    if page_num > 1:
        canvas.setFillColor(HDR_BAR)
        canvas.rect(0, PAGE_H - 0.45 * inch, PAGE_W, 0.45 * inch, fill=1, stroke=0)
        canvas.setFillColor(BG)
        canvas.setFont("SansBold", 8)
        canvas.drawString(MARGIN, PAGE_H - 0.28 * inch, doc._pdf_title)

    # Footer rule
    y_ftr = MARGIN - 0.16 * inch
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    if section:
        canvas.drawString(MARGIN, y_ftr, section)
    canvas.drawCentredString(PAGE_W / 2, y_ftr,
                             "M2 Community Node Troubleshooting Guide v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, f"Page {page_num}")

    canvas.restoreState()


def on_title_page(canvas, doc):
    """Title page — footer only, no header."""
    canvas.saveState()
    y_ftr = MARGIN - 0.16 * inch
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, y_ftr,
                             "M2 Community Node Troubleshooting Guide v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, "Page 1")
    canvas.restoreState()


# ── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    cw = PAGE_W - 2 * MARGIN

    return {
        # ── Title page ──
        "title_main": ParagraphStyle(
            "title_main",
            fontName="BigShoulders", fontSize=38, leading=44,
            textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6,
        ),
        "title_sub": ParagraphStyle(
            "title_sub",
            fontName="Sans", fontSize=18, leading=24,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
        ),
        "title_version": ParagraphStyle(
            "title_version",
            fontName="JuraMed", fontSize=11, leading=16,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
        ),
        "title_tagline": ParagraphStyle(
            "title_tagline",
            fontName="SansIt", fontSize=10, leading=14,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
        ),
        "title_license": ParagraphStyle(
            "title_license",
            fontName="Sans", fontSize=9, leading=13,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=2,
        ),
        # ── Content ──
        "h1": ParagraphStyle(
            "h1",
            fontName="BigShoulders", fontSize=20, leading=24,
            textColor=white, spaceBefore=0, spaceAfter=0,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="SansBold", fontSize=13, leading=16,
            textColor=ACCENT, spaceBefore=0, spaceAfter=0,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="SansBold", fontSize=11, leading=14,
            textColor=ACCENT, spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Sans", fontSize=9.5, leading=14,
            textColor=TEXT, spaceBefore=0, spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Sans", fontSize=9.5, leading=13,
            textColor=TEXT, leftIndent=14, bulletIndent=4,
            spaceBefore=1, spaceAfter=1,
        ),
        "bullet2": ParagraphStyle(
            "bullet2",
            fontName="Sans", fontSize=9, leading=12,
            textColor=TEXT, leftIndent=26, bulletIndent=16,
            spaceBefore=0, spaceAfter=0,
        ),
        "num": ParagraphStyle(
            "num",
            fontName="Sans", fontSize=9.5, leading=13,
            textColor=TEXT, leftIndent=18, bulletIndent=4,
            spaceBefore=1, spaceAfter=1,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Mono", fontSize=8, leading=11,
            textColor=CODE_TEXT, leftIndent=6, rightIndent=6,
            spaceBefore=0, spaceAfter=0,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Sans", fontSize=7.5, leading=10,
            textColor=MUTED,
        ),
        "table_head": ParagraphStyle(
            "table_head",
            fontName="SansBold", fontSize=8.5, leading=11,
            textColor=white,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Sans", fontSize=8.5, leading=11,
            textColor=TEXT,
        ),
        "table_code": ParagraphStyle(
            "table_code",
            fontName="Mono", fontSize=7.5, leading=10,
            textColor=CODE_TEXT,
        ),
    }


# ── Title page flowables ──────────────────────────────────────────────────────

def page_title_flowables(styles):
    """Cover page matching the Runbook and Build Book."""
    S = styles
    story = []
    story.append(NextPageTemplate("title"))
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("M2 COMMUNITY NODE", S["title_main"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Troubleshooting Guide", S["title_sub"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph("v1.0  |  April 2026", S["title_version"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Symptom-based field reference \u2014 "
        "WiFi \u00b7 ATAK \u00b7 Matrix \u00b7 Mesh \u00b7 Monero \u00b7 Tor",
        S["title_tagline"]
    ))
    story.append(Spacer(1, 32))
    story.append(HRFlowable(width="100%", thickness=0.5, color=RULE,
                            spaceAfter=8, spaceBefore=0))
    story.append(Paragraph("CC BY-NC-SA 4.0", S["title_license"]))
    story.append(Paragraph("yourdomain.com", S["title_license"]))
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    return story


# ── Markdown parser → flowables ───────────────────────────────────────────────

def _esc(text):
    """Escape ReportLab XML special chars and apply inline formatting."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`',
                  r'<font name="Mono" color="#0f0f0f">\1</font>', text)
    return text


def parse_md(md_text, styles):
    """Convert markdown to flowables. Each H3 entry is wrapped in KeepTogether."""
    S = styles
    lines = md_text.splitlines()
    flowables = []

    # H3 entry buffering — each troubleshooting entry stays together
    entry_buf = None   # None = not in entry; list = collecting entry flowables

    def emit(item):
        if entry_buf is not None:
            entry_buf.append(item)
        else:
            flowables.append(item)

    def flush_entry():
        nonlocal entry_buf
        if entry_buf:
            flowables.append(KeepTogether(entry_buf))
        entry_buf = None

    cw = PAGE_W - 2 * MARGIN

    pending_h2 = []  # H2 banner held until first H3 entry so they stay together

    in_code = False
    code_lines = []
    in_table = False
    table_rows = []
    table_sep_seen = False

    def flush_code():
        nonlocal code_lines
        if not code_lines:
            return
        code_text = "\n".join(code_lines)
        t = Table(
            [[Preformatted(code_text, S["code"])]],
            colWidths=[cw],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
            ("BOX",        (0, 0), (-1, -1), 0.5, RULE),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))
        emit(Spacer(1, 4))
        emit(t)
        emit(Spacer(1, 6))
        code_lines.clear()

    def flush_table():
        nonlocal table_rows, table_sep_seen
        if not table_rows:
            return
        ncols = max(len(r) for r in table_rows)
        col_w = cw / ncols
        data = []
        for ri, row in enumerate(table_rows):
            cells = []
            for cell in row:
                style = S["table_head"] if ri == 0 else S["table_cell"]
                cells.append(Paragraph(_esc(cell.strip()), style))
            while len(cells) < ncols:
                cells.append(Paragraph("", S["table_cell"]))
            data.append(cells)
        t = Table(data, colWidths=[col_w] * ncols, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0),  TABLE_HEAD),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TABLE_ALT]),
            ("FONTNAME",       (0, 0), (-1, 0),  "SansBold"),
            ("FONTSIZE",       (0, 0), (-1, -1), 8.5),
            ("TOPPADDING",     (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
            ("LEFTPADDING",    (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
            ("GRID",           (0, 0), (-1, -1), 0.4, RULE),
            ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ]))
        emit(Spacer(1, 4))
        emit(t)
        emit(Spacer(1, 8))
        table_rows.clear()
        table_sep_seen = False

    num_counter = [0]
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block toggle
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                if in_table:
                    flush_table()
                    in_table = False
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Table rows
        if line.startswith("|"):
            in_table = True
            if re.match(r'^\|[\s\-:|]+\|', line):
                table_sep_seen = True
                i += 1
                continue
            cells = [c for c in line.split("|") if c != ""]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            flush_table()
            in_table = False

        # Blank line
        if not line.strip():
            num_counter[0] = 0
            emit(Spacer(1, 4))
            i += 1
            continue

        # Horizontal rule — end of entry, goes to flowables directly
        if re.match(r'^---+\s*$', line):
            flush_entry()
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.5,
                                        color=RULE, spaceAfter=6))
            i += 1
            continue

        # H1 — goes to flowables directly (section title banner)
        if line.startswith("# ") and not line.startswith("## "):
            flush_entry()
            text = line[2:].strip()
            cell = Paragraph(_esc(text), S["h1"])
            t = Table([[cell]], colWidths=[cw])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), HDR_BAR),
                ("TOPPADDING",    (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ]))
            flowables.append(Spacer(1, 4))
            flowables.append(t)
            flowables.append(Spacer(1, 10))
            i += 1
            continue

        # H2 — hold in pending_h2 so it travels with the first H3 entry
        if line.startswith("## "):
            flush_entry()
            text = line[3:].strip()
            cell = Paragraph(_esc(text), S["h2"])
            t = Table([[cell]], colWidths=[cw])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), H2_BG),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ]))
            flowables.append(SectionMark(text))
            pending_h2 = [Spacer(1, 10), t, Spacer(1, 6)]
            i += 1
            continue

        # H3 — start a new entry buffer, prepend any pending H2 banner
        if line.startswith("### "):
            flush_entry()
            entry_buf = list(pending_h2)
            pending_h2.clear()
            text = line[4:].strip()
            entry_buf.append(Paragraph(_esc(text), S["h3"]))
            i += 1
            continue

        # H4 (bold body)
        if line.startswith("#### "):
            text = line[5:].strip()
            emit(Paragraph(f"<b>{_esc(text)}</b>", S["body"]))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            num_counter[0] += 1
            text = m.group(2)
            emit(Paragraph(f'{num_counter[0]}.&nbsp;&nbsp;{_esc(text)}', S["num"]))
            i += 1
            continue

        # Sub-bullet
        if re.match(r'^\s{3,}[-*]\s', line):
            text = re.sub(r'^\s+[-*]\s+', '', line)
            emit(Paragraph(f'&#x2013;&nbsp;&nbsp;{_esc(text)}', S["bullet2"]))
            i += 1
            continue

        # Bullet
        if re.match(r'^[-*]\s', line):
            text = line[2:].strip()
            num_counter[0] = 0
            emit(Paragraph(f'&#x2022;&nbsp;&nbsp;{_esc(text)}', S["bullet"]))
            i += 1
            continue

        # Regular paragraph
        num_counter[0] = 0
        emit(Paragraph(_esc(line.strip()), S["body"]))
        i += 1

    # Flush any open blocks
    if in_code:
        flush_code()
    if in_table:
        flush_table()
    flush_entry()
    for item in pending_h2:
        flowables.append(item)

    return flowables


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(output_path, pdf_title, pdf_sub, source_files):
    """Build a PDF with cover page, consistent header/footer, KeepTogether entries."""
    styles = make_styles()
    cw = PAGE_W - 2 * MARGIN

    # Cover page
    flowables = page_title_flowables(styles)

    # Content from markdown files
    for md_path in source_files:
        if not os.path.exists(md_path):
            print(f"  WARNING: not found — {md_path}")
            continue
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        flowables.extend(parse_md(content, styles))
        flowables.append(Spacer(1, 0.3 * inch))

    doc = BaseDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN + 12,
        title=pdf_title,
        author="Community Node Project",
        subject=pdf_sub,
    )
    doc._pdf_title = pdf_title

    title_frame = Frame(
        MARGIN, MARGIN + 12,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 2 * MARGIN - 24,
        id="title_frame",
    )
    body_frame = Frame(
        MARGIN, MARGIN + 12,
        PAGE_W - 2 * MARGIN,
        PAGE_H - 2 * MARGIN + 4,
        id="body_frame",
    )

    title_template = PageTemplate(id="title", frames=[title_frame],
                                  onPage=on_title_page)
    body_template  = PageTemplate(id="body",  frames=[body_frame],
                                  onPage=on_page)
    doc.addPageTemplates([title_template, body_template])

    doc.build(flowables)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"  {os.path.basename(output_path)}  ({size_kb:.0f} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Generating M2 Community Node reference PDFs...\n")

    build_pdf(
        output_path=os.path.join(ROOT_DIR, "operational-pdfs", "M2_Community_Node_Troubleshooting.pdf"),
        pdf_title="M2 Community Node — Troubleshooting Guide",
        pdf_sub="Symptom-based field reference · WiFi · ATAK · Matrix · Monero · Tor",
        source_files=[
            os.path.join(DOCS_DIR, "TROUBLESHOOTING.md"),
        ],
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
