"""
M2 Community Node — Field Operations Runbook Generator
Outputs: M2_Community_Node_Runbook.pdf (US Letter, ~20 pages)

Run: python generate_runbook.py
"""

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from instance_config import cfg as _cfg
_ATAK_PASS  = _cfg["ATAK_TRUSTSTORE_PASS"]
_ATAK_USER  = _cfg["ATAK_ENROLL_USER"]
_ATAK_PWORD = _cfg["ATAK_ENROLL_PASS"]

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, PageBreak, KeepTogether, Preformatted,
    HRFlowable, NextPageTemplate,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
import sys

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SansItalic",   f"{FONTS}/InstrumentSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{FONTS}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoBold",     f"{FONTS}/IBMPlexMono-Bold.ttf"))

# ── Color palette ────────────────────────────────────────────────────────────
ACCENT     = HexColor("#921212")
BG         = HexColor("#ffffff")
TEXT       = HexColor("#0f0f0f")
MUTED      = HexColor("#4a4a4a")
RULE_COLOR = HexColor("#dcc8c8")
CARD_BG    = HexColor("#faf6f6")
ROW_ALT    = HexColor("#faf6f6")
ROW_WHITE  = HexColor("#ffffff")
TABLE_HDR  = HexColor("#921212")
CHECK_BG   = HexColor("#faf6f6")

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

OUTPUT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "operational-pdfs", "M2_Community_Node_Runbook.pdf")
TITLE  = "M2 Community Node — Field Operations Runbook"
VERSION = "v1.0"

# ── Styles ───────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["title_main"] = ParagraphStyle(
        "title_main",
        fontName="BigShoulders",
        fontSize=38,
        leading=44,
        textColor=ACCENT,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["title_sub"] = ParagraphStyle(
        "title_sub",
        fontName="Sans",
        fontSize=18,
        leading=24,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["title_version"] = ParagraphStyle(
        "title_version",
        fontName="JuraMed",
        fontSize=11,
        leading=16,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["title_tagline"] = ParagraphStyle(
        "title_tagline",
        fontName="SansItalic",
        fontSize=10,
        leading=14,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["title_license"] = ParagraphStyle(
        "title_license",
        fontName="Sans",
        fontSize=9,
        leading=13,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    styles["h1"] = ParagraphStyle(
        "h1",
        fontName="BigShoulders",
        fontSize=18,
        leading=22,
        textColor=white,
        spaceBefore=0,
        spaceAfter=8,
    )
    styles["h2"] = ParagraphStyle(
        "h2",
        fontName="SansBold",
        fontSize=13,
        leading=17,
        textColor=ACCENT,
        spaceBefore=12,
        spaceAfter=4,
    )
    styles["h3"] = ParagraphStyle(
        "h3",
        fontName="SansBold",
        fontSize=10,
        leading=14,
        textColor=ACCENT,
        spaceBefore=8,
        spaceAfter=3,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Sans",
        fontSize=9,
        leading=13,
        textColor=TEXT,
        spaceBefore=2,
        spaceAfter=4,
    )
    styles["body_bold"] = ParagraphStyle(
        "body_bold",
        fontName="SansBold",
        fontSize=9,
        leading=13,
        textColor=TEXT,
        spaceBefore=2,
        spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Sans",
        fontSize=9,
        leading=13,
        textColor=TEXT,
        spaceBefore=1,
        spaceAfter=1,
        leftIndent=14,
        bulletIndent=0,
    )
    styles["numbered"] = ParagraphStyle(
        "numbered",
        fontName="Sans",
        fontSize=9,
        leading=13,
        textColor=TEXT,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=18,
    )
    styles["note"] = ParagraphStyle(
        "note",
        fontName="SansItalic",
        fontSize=8,
        leading=12,
        textColor=MUTED,
        spaceBefore=2,
        spaceAfter=4,
    )
    styles["caption"] = ParagraphStyle(
        "caption",
        fontName="Sans",
        fontSize=8,
        leading=11,
        textColor=MUTED,
        spaceBefore=2,
        spaceAfter=6,
    )
    styles["code"] = ParagraphStyle(
        "code",
        fontName="Mono",
        fontSize=8,
        leading=11,
        textColor=TEXT,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=6,
    )
    styles["tbl_hdr"] = ParagraphStyle(
        "tbl_hdr",
        fontName="SansBold",
        fontSize=8,
        leading=11,
        textColor=white,
    )
    styles["tbl_body"] = ParagraphStyle(
        "tbl_body",
        fontName="Sans",
        fontSize=8,
        leading=11,
        textColor=TEXT,
    )
    styles["tbl_body_bold"] = ParagraphStyle(
        "tbl_body_bold",
        fontName="SansBold",
        fontSize=8,
        leading=11,
        textColor=TEXT,
    )
    styles["tbl_note"] = ParagraphStyle(
        "tbl_note",
        fontName="SansItalic",
        fontSize=7.5,
        leading=10,
        textColor=MUTED,
    )
    styles["check_item"] = ParagraphStyle(
        "check_item",
        fontName="Sans",
        fontSize=9,
        leading=13,
        textColor=TEXT,
    )
    styles["path_label"] = ParagraphStyle(
        "path_label",
        fontName="SansBold",
        fontSize=10,
        leading=14,
        textColor=ACCENT,
        spaceBefore=6,
        spaceAfter=2,
    )

    return styles

# ── Header/Footer canvas callbacks ───────────────────────────────────────────
section_registry = {}  # page_num -> section_name

def on_page(canvas, doc):
    """Footer + header for all non-title pages."""
    page_num = doc.page
    section = section_registry.get(page_num, "")

    canvas.saveState()

    # ACCENT header bar (skip page 1)
    if page_num > 1:
        canvas.setFillColor(ACCENT)
        canvas.rect(0, PAGE_H - 0.45 * inch, PAGE_W, 0.45 * inch, fill=1, stroke=0)
        canvas.setFillColor(BG)
        canvas.setFont("SansBold", 8)
        canvas.drawString(MARGIN, PAGE_H - 0.28 * inch, TITLE)
        canvas.setFillColor(HexColor("#f5cccc"))
        canvas.setFont("Sans", 7.5)
        if section:
            canvas.drawString(MARGIN, PAGE_H - 0.38 * inch, section)

    # Footer
    y_ftr = MARGIN - 16
    canvas.setStrokeColor(RULE_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    if section:
        canvas.drawString(MARGIN, y_ftr, section)
    canvas.drawCentredString(PAGE_W / 2, y_ftr, "M2 Community Node Runbook v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, f"Page {page_num}")

    canvas.restoreState()


def on_title_page(canvas, doc):
    """Title page — footer only, no header rule."""
    canvas.saveState()
    y_ftr = MARGIN - 16
    canvas.setStrokeColor(RULE_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, y_ftr, "M2 Community Node Runbook v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, "Page 1")
    canvas.restoreState()


# ── Helper flowables ─────────────────────────────────────────────────────────
class SectionMark(Flowable):
    """Zero-height marker that records the section name for the current page."""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.width = 0
        self.height = 0

    def draw(self):
        page = self.canv._doctemplate.page
        section_registry[page] = self.name


class CodeBlock(Flowable):
    """Monospace code block with light gray background."""
    def __init__(self, text, width=None):
        super().__init__()
        self._text = text
        self._req_width = width
        self.hAlign = "LEFT"

    def wrap(self, availWidth, availHeight):
        self.width = self._req_width or availWidth
        lines = self._text.split("\n")
        self._lines = lines
        pad = 8
        self.height = len(lines) * 11 + pad * 2
        return self.width, self.height

    def draw(self):
        pad = 8
        h = self.height
        self.canv.setFillColor(CARD_BG)
        self.canv.setStrokeColor(RULE_COLOR)
        self.canv.setLineWidth(0.5)
        self.canv.roundRect(0, 0, self.width, h, 3, fill=1, stroke=1)
        self.canv.setFont("Mono", 8)
        self.canv.setFillColor(TEXT)
        y = h - pad - 9
        for line in self._lines:
            self.canv.drawString(pad, y, line)
            y -= 11


def sp(n=4):
    return Spacer(1, n)


def rule():
    return HRFlowable(width="100%", thickness=0.5, color=RULE_COLOR,
                      spaceAfter=4, spaceBefore=4)


def make_table(data, col_widths, style_cmds=None, repeat_header=True):
    """Build a styled table with alternating row shading."""
    n_rows = len(data)
    base_cmds = [
        ("BACKGROUND",  (0, 0), (-1, 0),  TABLE_HDR),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING",  (0, 0), (-1, 0),  5),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 8),
        ("TOPPADDING",  (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID",        (0, 0), (-1, -1), 0.3, RULE_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [ROW_ALT, ROW_WHITE]),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]
    if style_cmds:
        base_cmds.extend(style_cmds)
    tbl = Table(data, colWidths=col_widths, repeatRows=1 if repeat_header else 0)
    tbl.setStyle(TableStyle(base_cmds))
    return tbl


def h(text, style):
    return Paragraph(text, style)


def body(text, style):
    return Paragraph(text, style)


def bullet(text, style):
    return Paragraph(f"\u2022  {text}", style)


def numbered_item(num, text, style):
    return Paragraph(f"<b>{num}.</b>  {text}", style)


# ── Document sections ─────────────────────────────────────────────────────────

def page_title(styles):
    """Page 1: Title page."""
    S = styles
    story = []
    story.append(NextPageTemplate("title"))
    story.append(sp(2 * inch))
    story.append(h("M2 COMMUNITY NODE", S["title_main"]))
    story.append(sp(8))
    story.append(h("Field Operations Runbook", S["title_sub"]))
    story.append(sp(16))
    story.append(h("v1.0  |  April 2026", S["title_version"]))
    story.append(sp(8))
    story.append(h(
        "Field-deployable decentralized communications \u2014 "
        "ATAK \u00b7 Matrix \u00b7 Mesh \u00b7 Monero",
        S["title_tagline"]
    ))
    story.append(sp(32))
    story.append(rule())
    story.append(sp(8))
    story.append(h("CC BY-NC-SA 4.0", S["title_license"]))
    story.append(h("yourdomain.com", S["title_license"]))
    return story






def page_power_on(styles):
    """Page 6: Power-On & POST."""
    S = styles
    story = []
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    story.append(SectionMark("Power-On & POST"))
    _h1_cell = h("Power-On Sequence", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))

    steps = [
        "UPS (BC600R) \u2014 press power, confirm green LED.",
        "GL.iNet router \u2014 power on, wait 60 seconds.",
        "TP-Link switch \u2014 power on.",
        "Pi #1 (comms, 192.168.8.10) \u2014 power on.",
        "Pi #2 (tactical, 192.168.8.20) \u2014 power on.",
        "Wait 90 seconds for services to start.",
        "Kiosk touchscreen \u2014 power on last.",
    ]
    for i, s in enumerate(steps, 1):
        story.append(numbered_item(i, s, S["numbered"]))
    story.append(sp(4))
    story.append(body(
        "<b>Total boot time: ~3 minutes.</b>  Do not test connectivity during this window.",
        S["body"]
    ))
    story.append(sp(10))

    story.append(h("POST \u2014 Quick Check (30 seconds)", S["h2"]))
    post_data = [
        [h("URL", S["tbl_hdr"]), h("Expected", S["tbl_hdr"]), h("Service", S["tbl_hdr"])],
        [h("http://192.168.8.1",      S["tbl_body"]), h("GL.iNet admin panel",    S["tbl_body"]), h("Router",          S["tbl_body"])],
        [h("http://192.168.8.10:8081",S["tbl_body"]), h("Community info page",    S["tbl_body"]), h("Kiosk web",       S["tbl_body"])],
        [h("http://192.168.8.10:8080",S["tbl_body"]), h("Element Web login",      S["tbl_body"]), h("Matrix chat",     S["tbl_body"])],
        [h("http://192.168.8.20:8080",S["tbl_body"]), h("OTS web map",            S["tbl_body"]), h("OpenTAK Server",  S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.32, CONTENT_W * 0.36, CONTENT_W * 0.32]
    story.append(make_table(post_data, col_w))
    story.append(sp(4))
    story.append(body("<b>If all four load: node is GO.</b>", S["body"]))
    story.append(sp(10))

    story.append(h("Full POST (SSH)", S["h2"]))
    story.append(CodeBlock(
        "ssh pi@192.168.8.10\n"
        "docker ps --format \"table {{.Names}}\\t{{.Status}}\"\n"
        "# All containers should show \"Up\""
    ))
    story.append(sp(6))
    story.append(CodeBlock(
        "ssh pi@192.168.8.20\n"
        "systemctl is-active opentakserver cot_parser\n"
        "docker ps --format \"table {{.Names}}\\t{{.Status}}\"\n"
        "# Expected: active (twice), then all containers Up"
    ))
    return story


def page_pre_event(styles):
    """Pre-Event Checklist."""
    S = styles
    story = []
    story.append(SectionMark("Pre-Event Checklist"))
    _h1_cell = h("Pre-Event Checklist", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body("Complete 30 minutes before go-live.", S["note"]))
    story.append(sp(6))

    items = [
        "All POST checks pass (all four URLs load on test device).",
        "Update node GPS marker \u2014 OTS Web UI \u2192 map \u2192 right-click node location \u2192 set marker. Location may have changed from build to deployment.",
        "Node GPS marker visible and correct on OTS web map.",
        "Test phone connects to CommunityNode WiFi.",
        "Test phone ATAK connects and enrolls (192.168.8.20:8089 SSL).",
        "Test phone icon appears on OTS web map with correct callsign.",
        "GeoChat test: send a message, confirm it appears in OTS.",
        "Reporting Strategy set to Consistent on test phone.",
        "Mumla voice test: 192.168.8.20 port 64738 connects, voice audible.",
        "Element Web accessible at http://192.168.8.10:8080.",
        "Field cards printed and available (or QR codes on kiosk).",
        "WiFi password posted or available for incoming team members.",
        "Cloudflare Tunnel active \u2014 verify tak.yourdomain.com loads from external device.",
        "Path B: Pre-add expected remote viewer emails to Cloudflare Access approved list.",
        "If SAR: ExCheck checklist template built and ready to distribute.",
    ]

    check_data = [[h("\u2610", S["check_item"]), h(item, S["check_item"])] for item in items]
    # Use plain table for checklist — no header row
    tbl = Table(check_data, colWidths=[CONTENT_W * 0.06, CONTENT_W * 0.94])
    tbl.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [ROW_WHITE, ROW_ALT]),
        ("GRID",  (0, 0), (-1, -1), 0.3, RULE_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (0, -1), 16),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]))
    story.append(tbl)
    return story


def pages_onboarding(styles):
    """Operator Onboarding — 3 Paths."""
    S = styles
    story = []
    story.append(SectionMark("Operator Onboarding"))
    _h1_cell = h("Operator Onboarding \u2014 Three Paths", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))

    # Admin PC requirement note
    note_text = (
        "<b>[!]  OPERATOR / ADMIN REQUIREMENT:</b>  All administrative tasks in this section "
        "require a dedicated operations PC, laptop, or tablet \u2014 not a smartphone. "
        "The node admin must have their computer available and connected to "
        "<b>CommunityNode WiFi</b> (for OTS Web UI and SSH) or the <b>internet</b> "
        "(for Cloudflare dashboard and remote management). "
        "Ensure your admin machine is ready before onboarding begins."
    )
    note_para = Paragraph(note_text, S["body"])
    note_tbl = Table([[note_para]], colWidths=[CONTENT_W])
    note_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#faf6f6")),
        ("BOX",           (0, 0), (-1, -1), 1.0, ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(note_tbl)
    story.append(sp(8))

    # Decision tree text block
    tree = (
        "                    +---------------------+\n"
        "                    |   New team member   |\n"
        "                    |   needs map access  |\n"
        "                    +----------+----------+\n"
        "                               |\n"
        "                 +-------------+-------------+\n"
        "                 |  Are they physically here? |\n"
        "                 +-------------+-------------+\n"
        "                        +--yes-+--no--+\n"
        "                        |             |\n"
        "                 +------+------+ +----+--------------------+\n"
        "                 |  PATH A     | |  Do they need full ATAK |\n"
        "                 |  Local WiFi | |  (CoT, GeoChat, PLI)?   |\n"
        "                 |  Full ATAK  | +----+--------------------+\n"
        "                 +-------------+   +--no-+--yes--+\n"
        "                                   |             |\n"
        "                            +------+------+ +----+-------------+\n"
        "                            |  PATH B     | |  PATH C          |\n"
        "                            |  Clearnet   | |  VPN + ATAK      |\n"
        "                            |  Browser    | |  Operator only   |\n"
        "                            +-------------+ +-----------------+"
    )
    story.append(CodeBlock(tree))
    story.append(sp(10))

    # Quick comparison table
    story.append(h("Path Comparison", S["h2"]))
    comp_data = [
        [
            h("", S["tbl_hdr"]),
            h("Path A: Local WiFi", S["tbl_hdr"]),
            h("Path B: Clearnet Browser", S["tbl_hdr"]),
            h("Path C: VPN + ATAK", S["tbl_hdr"]),
        ],
        [h("Location", S["tbl_body_bold"]),       h("At the node", S["tbl_body"]),            h("Anywhere with internet", S["tbl_body"]),  h("Anywhere with internet", S["tbl_body"])],
        [h("App required", S["tbl_body_bold"]),    h("ATAK-CIV", S["tbl_body"]),               h("Browser only", S["tbl_body"]),            h("Tailscale + ATAK-CIV", S["tbl_body"])],
        [h("Appears on map", S["tbl_body_bold"]),  h("Yes", S["tbl_body"]),                    h("No", S["tbl_body"]),                      h("Yes", S["tbl_body"])],
        [h("GeoChat", S["tbl_body_bold"]),         h("Yes", S["tbl_body"]),                    h("No", S["tbl_body"]),                      h("Yes", S["tbl_body"])],
        [h("Voice (Mumble)", S["tbl_body_bold"]),  h("Yes", S["tbl_body"]),                    h("No", S["tbl_body"]),                      h("Yes (with Mumla)", S["tbl_body"])],
        [h("Onboard time", S["tbl_body_bold"]),    h("2\u20135 min", S["tbl_body"]),            h("Under 60 sec", S["tbl_body"]),            h("5\u201310 min", S["tbl_body"])],
        [h("Operator effort", S["tbl_body_bold"]), h("Hand them a QR code", S["tbl_body"]),    h("Add email to approved list", S["tbl_body"]), h("Generate key, send instructions", S["tbl_body"])],
        [h("Revoke access", S["tbl_body_bold"]),   h("They leave WiFi range", S["tbl_body"]),  h("Remove email from list", S["tbl_body"]),  h("Delete node from Headscale", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.18, CONTENT_W * 0.22, CONTENT_W * 0.28, CONTENT_W * 0.32]
    story.append(make_table(comp_data, col_w))

    # ---- Path A ----
    story.append(SectionMark("Operator Onboarding"))
    _h1_cell = h("Path A \u2014 Local WiFi (Primary)", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Who:</b>  Anyone physically at the node \u2014 SAR volunteers, community members, field teams.",
        S["body"]
    ))
    story.append(body(
        "<b>What they get:</b>  Full ATAK \u2014 live position sharing, GeoChat, markers, missions, "
        "voice (Mumble), mesh relay (Meshtastic).",
        S["body"]
    ))
    story.append(sp(6))

    story.append(h("Operator Walkthrough", S["h2"]))

    path_a_steps = [
        ("<b>Get the user on the WiFi.</b>  Tell them to connect to <b>CommunityNode</b> WiFi. "
         "Give them the password from the printed card or read it to them. "
         "They do NOT need the admin WiFi \u2014 CommunityNode has full access to the server."),

        ("<b>Confirm ATAK is installed.</b>  ATAK-CIV (Android/Play Store) or iTAK (iPhone/App Store). "
         "If they don't have it, point them at the community page QR codes (http://192.168.8.10:8081) "
         "or hand them the field card."),

        ("<b>Generate their enrollment QR code.</b>  Open OTS Web UI at http://192.168.8.20:8080. "
         "Log in with admin credentials. Navigate to <b>Certificates</b> (left sidebar) \u2192 "
         "<b>Generate Data Package</b> \u2192 enter callsign \u2192 <b>Generate</b> \u2192 "
         "click <b>Show QR Code</b> on the generated package."),

        ("<b>User scans the QR code.</b>  In ATAK: Menu (\u2261) \u2192 <b>Import</b> \u2192 "
         "<b>QR Code</b>. Scan the QR from your screen. "
         "ATAK auto-imports server connection, certificate, and truststore. Connects within seconds."),

        ("<b>User sets callsign.</b>  Settings \u2192 My Preferences \u2192 Callsign. "
         "Use their name or an assigned tactical callsign."),

        ("<b>Verify.</b>  Their icon appears on the shared map. Test GeoChat: have them send a message. "
         "If using Mumble: open Mumla, server 192.168.8.20, port 64738."),
    ]
    for i, s in enumerate(path_a_steps, 1):
        story.append(numbered_item(i, s, S["numbered"]))
        story.append(sp(2))

    story.append(sp(6))
    story.append(h("Fallback \u2014 Manual Server Entry", S["h3"]))
    story.append(body("If the QR scan fails (old phone, camera issues):", S["body"]))
    story.append(body("ATAK \u2192 Settings \u2192 Network \u2192 TAK Servers \u2192 Add", S["body"]))

    manual_data = [
        [h("Setting", S["tbl_hdr"]),         h("Value", S["tbl_hdr"])],
        [h("Server", S["tbl_body"]),          h("192.168.8.20", S["tbl_body"])],
        [h("Port", S["tbl_body"]),            h("8089", S["tbl_body"])],
        [h("Protocol", S["tbl_body"]),        h("SSL", S["tbl_body"])],
        [h("Enable authentication", S["tbl_body"]), h("Yes", S["tbl_body"])],
        [h("Enroll for client certificate", S["tbl_body"]), h("Yes", S["tbl_body"])],
        [h("Use default SSL/TLS certs", S["tbl_body"]), h("No \u2014 uncheck this", S["tbl_body"])],
        [h("Truststore password", S["tbl_body"]), h(_ATAK_PASS, S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.45, CONTENT_W * 0.55]
    story.append(make_table(manual_data, col_w))
    story.append(sp(4))
    story.append(body(
        "ATAK contacts the server on port 8446, downloads and installs the certificate automatically. "
        "OTS handles all PKI \u2014 it auto-generates a unique client certificate for each enrolling device.",
        S["body"]
    ))
    story.append(body("<b>Time to onboard:</b>  2\u20135 min with QR code. 5\u201310 min manual.", S["body"]))

    # ---- Path B ----
    story.append(SectionMark("Operator Onboarding"))
    _h1_cell = h("Path B \u2014 Clearnet Browser (Remote Viewers)", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Who:</b>  Remote team members, partner agencies, anyone with internet who needs "
        "situational awareness but does NOT need to be a CoT participant on the map.",
        S["body"]
    ))
    story.append(body(
        "<b>What they get:</b>  Full OTS web map in a browser \u2014 all team positions, markers, "
        "missions, live updates. View and monitor. No app install required.",
        S["body"]
    ))
    story.append(sp(6))

    story.append(body(
        "<b>\u26a0\ufe0f  Admin action required.</b>  Path B access is controlled by Cloudflare Zero Trust. "
        "Adding a user requires an admin with Cloudflare dashboard access and an internet connection. "
        "This <b>cannot</b> be done from the node itself. "
        "If possible, pre-add expected remote viewer emails <b>before the event</b>.",
        S["note"]
    ))
    story.append(sp(6))

    story.append(h("Operator Walkthrough", S["h2"]))

    path_b_steps = [
        ("<b>Contact the node admin</b> (or perform if you have Cloudflare access). "
         "The admin must log in to <b>dash.cloudflare.com</b> from any internet-connected computer."),

        ("<b>Add the email to the approved list:</b>  "
         "Zero Trust \u2192 Access \u2192 Applications \u2192 <b>OTS Web Map</b> \u2192 Edit Policy \u2192 "
         "Include rule (Email) \u2192 add address \u2192 Save. "
         "Access is granted immediately."),

        ("<b>Send them the link and login instructions:</b>"),
    ]
    for i, s in enumerate(path_b_steps, 1):
        story.append(numbered_item(i, s, S["numbered"]))
        story.append(sp(2))

    story.append(CodeBlock(
        "Web map: https://tak.yourdomain.com\n"
        "\n"
        "To log in:\n"
        "1. Open the link in any browser\n"
        "2. Enter your email address\n"
        "3. Check inbox for a 6-digit PIN\n"
        "4. Enter the PIN -- you're in\n"
        "(PIN expires in 10 minutes -- request a new one if needed)"
    ))
    story.append(sp(4))
    story.append(numbered_item(4,
        "<b>Revoke access when needed.</b>  Zero Trust \u2192 Access \u2192 Applications \u2192 Edit Policy \u2192 "
        "remove their email \u2192 Save. Access is cut immediately.",
        S["numbered"]
    ))
    story.append(sp(8))

    story.append(h("Automating Path B (Optional)", S["h3"]))
    story.append(body(
        "Adding emails one at a time through the dashboard is slow on site. "
        "A helper script using the Cloudflare API can automate this. "
        "If your admin has set up <b>cf-access.sh</b> on the comms Pi, "
        "the entire grant/revoke cycle becomes a single SSH command:",
        S["body"]
    ))
    story.append(CodeBlock(
        "# Grant access (run from admin laptop on NodeAdmin WiFi):\n"
        "ssh pi@192.168.8.10 sudo /usr/local/bin/cf-access.sh add user@example.com\n"
        "\n"
        "# Revoke access:\n"
        "ssh pi@192.168.8.10 sudo /usr/local/bin/cf-access.sh remove user@example.com"
    ))
    story.append(body(
        "Ask your node admin to set this up before CCC26. "
        "Script requires a Cloudflare API token stored on the comms Pi.",
        S["note"]
    ))
    story.append(sp(8))
    story.append(body("<b>Time to onboard:</b>  Under 60 seconds (add email, send link).", S["body"]))

    story.append(h("Limitations", S["h3"]))
    limitations_moved = [
        "They can see the map but do NOT appear as a position on it.",
        "No GeoChat, no marker creation, no mission participation from the browser.",
        "Requires internet access (the tunnel routes through Cloudflare).",
        "If you don't add their email, they can't get past the login screen.",
    ]
    for lim in limitations_moved:
        story.append(bullet(lim, S["bullet"]))
    story.append(sp(8))

    # ---- Path C ----
    _h1_cell = h("Path C \u2014 VPN + Full ATAK (Controlled Remote Access)", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body(
        "<b>Who:</b>  Specific, trusted operators who need full ATAK participation from outside "
        "the node WiFi. This is NOT for general users. The operator personally sets this up for "
        "each individual.",
        S["body"]
    ))
    story.append(body(
        "<b>What they get:</b>  Full ATAK over VPN \u2014 identical to being on local WiFi. "
        "Live position sharing, GeoChat, markers, missions, everything. "
        "They appear on the map as a full team member.",
        S["body"]
    ))
    story.append(sp(4))
    story.append(body(
        "<b>Remote user requirements:</b>  Tailscale (Play Store) + ATAK-CIV (Play Store).",
        S["body"]
    ))
    story.append(sp(6))

    story.append(h("Operator Steps", S["h2"]))
    story.append(body(
        "<b>Requires:</b>  Admin machine connected to CommunityNode WiFi or NodeAdmin WiFi. "
        "Run SSH commands from your admin laptop \u2014 not from the node itself.",
        S["note"]
    ))
    story.append(sp(4))
    story.append(numbered_item(1, "<b>Generate a VPN auth key (on tactical Pi):</b>", S["numbered"]))
    story.append(CodeBlock(
        "ssh pi@192.168.8.20\n"
        "sudo docker exec tactical-node-headscale-1 \\\n"
        "  headscale preauthkeys create --user community --expiration 24h\n"
        "# For standing team member (persistent):\n"
        "sudo docker exec tactical-node-headscale-1 \\\n"
        "  headscale preauthkeys create --user community --expiration 90d --reusable"
    ))
    story.append(sp(4))
    story.append(numbered_item(2, "<b>Send the user these instructions:</b>", S["numbered"]))
    story.append(CodeBlock(
        "1. Install Tailscale from the Play Store\n"
        "2. Open Tailscale > tap profile icon > Accounts > three-dot menu\n"
        "   > 'Use an alternate server'\n"
        "3. Enter: https://m2vpn.yourdomain.com\n"
        "4. Paste the auth key I sent you\n"
        "5. Tailscale connects -- you now have a VPN tunnel to the node\n"
        "\n"
        "6. Open ATAK > Settings > Network > TAK Servers > Add\n"
        "   Server: 192.168.8.20  |  Port: 8089  |  Protocol: SSL\n"
        "   Check: Enroll for Client Certificate\n"
        "   Uncheck: Use default SSL/TLS Certificates\n"
        f"   Truststore password: {_ATAK_PASS}\n"
        "\n"
        "7. Set callsign: Settings > My Preferences > Callsign\n"
        "8. You should appear on the shared map within seconds."
    ))
    story.append(sp(4))
    story.append(numbered_item(3, "<b>Verify their connection:</b>", S["numbered"]))
    story.append(CodeBlock(
        "ssh pi@192.168.8.20\n"
        "sudo docker exec tactical-node-headscale-1 headscale nodes list\n"
        "# Confirm their device has an assigned IP (100.64.x.x range)"
    ))
    story.append(sp(4))
    story.append(numbered_item(4, "<b>Revoke access when done:</b>", S["numbered"]))
    story.append(CodeBlock(
        "ssh pi@192.168.8.20\n"
        "sudo docker exec tactical-node-headscale-1 headscale nodes delete --identifier <id>\n"
        "# User's Tailscale immediately disconnects. No residual access."
    ))
    story.append(sp(6))
    story.append(h("Security Notes", S["h3"]))
    sec_notes = [
        "Each auth key is tied to an expiration \u2014 it cannot be reused after it expires.",
        "You control exactly who has access and can revoke instantly.",
        "VPN traffic is encrypted end-to-end (WireGuard).",
        "The Headscale server only accepts connections with valid pre-auth keys.",
        "Subnet routes (192.168.8.0/24) are already approved on both Pis \u2014 "
        "remote users reach LAN services as if local.",
    ]
    for sn in sec_notes:
        story.append(bullet(sn, S["bullet"]))

    return story


def page_during_event(styles):
    """During the Event."""
    S = styles
    story = []
    story.append(SectionMark("During the Event"))
    _h1_cell = h("During the Event", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))

    story.append(h("Monitoring", S["h2"]))
    story.append(bullet(
        "Kiosk touchscreen shows live service status. Green = healthy.", S["bullet"]))
    story.append(bullet(
        "OTS web map at http://192.168.8.20:8080 shows all connected EUDs.", S["bullet"]))
    story.append(sp(8))

    story.append(h("Positions Stop Updating", S["h2"]))
    story.append(body(
        "The CoT parser service processes incoming position reports. "
        "If positions freeze, restart it:", S["body"]
    ))
    story.append(CodeBlock(
        "ssh pi@192.168.8.20\n"
        "systemctl status cot_parser\n"
        "sudo systemctl restart cot_parser"
    ))
    story.append(sp(8))

    story.append(h("User Can't Connect to ATAK", S["h2"]))
    causes = [
        "<b>Wrong WiFi.</b>  Must be on CommunityNode, not NodeAdmin or a hotspot.",
        "<b>SSL checkbox.</b>  In ATAK TAK Servers, must have 'Enroll for Client Certificate' "
        "checked and 'Use default SSL/TLS Certificates' unchecked.",
        "<b>Old server entry.</b>  Delete the server entry in ATAK and re-add from scratch. "
        "Stale certificates cause repeated connection failures.",
        "<b>Private DNS / VPN on phone.</b>  Disable any system-level VPN or Private DNS "
        "setting before connecting. These interfere with local resolution.",
        "<b>Certificate enrollment already done.</b>  If the user previously enrolled, "
        "ATAK may have cached a bad cert. Delete the server and re-add.",
    ]
    for c in causes:
        story.append(bullet(c, S["bullet"]))
    story.append(sp(8))

    story.append(KeepTogether([
        h("Element / Matrix Down", S["h2"]),
        CodeBlock(
            "ssh pi@192.168.8.10\n"
            "docker restart community-node-conduit-1\n"
            "docker restart community-node-nginx-1"
        ),
    ]))
    story.append(sp(8))

    story.append(KeepTogether([
        h("User Not on Map", S["h2"]),
        bullet("In ATAK: Settings \u2192 Reporting \u2192 Reporting Strategy \u2192 set to <b>Consistent</b>.", S["bullet"]),
        bullet("Or: toggle server off/on in TAK Servers to force a reconnect.", S["bullet"]),
        bullet("Confirm GPS is active on their phone and location permission is granted to ATAK.", S["bullet"]),
        bullet("Check OTS is showing their callsign in the Clients list (http://192.168.8.20:8080).", S["bullet"]),
    ]))
    return story


def page_teardown(styles):
    """Teardown & Emergency."""
    S = styles
    story = []
    story.append(SectionMark("Teardown & Emergency"))
    _h1_cell = h("Teardown", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body("Shut down in reverse power-on order:", S["body"]))

    shutdown_steps = [
        "Notify all active ATAK users: 'Server going offline in 2 minutes.'",
        "Export any mission data from OTS Web UI if needed (Missions \u2192 Export).",
        "SSH to Pi #1: <b>sudo shutdown -h now</b>",
        "SSH to Pi #2: <b>sudo shutdown -h now</b>",
        "Wait 30 seconds for both Pis to power off (LEDs go dark).",
        "Power off the GL.iNet router.",
        "Power off the TP-Link switch.",
        "Power off the Anker charger.",
        "Power off the Tupavco PDU.",
        "UPS last: hold power button until it beeps off.",
    ]
    for i, s in enumerate(shutdown_steps, 1):
        story.append(numbered_item(i, s, S["numbered"]))
        story.append(sp(1))

    story.append(sp(6))
    story.append(h("Pack-Up Notes", S["h3"]))
    pack = [
        "Disconnect LoRa antennas before coiling USB cables \u2014 the SMA connectors are fragile.",
        "USB-C cables for the Pis go in the accessory pouch, not loose in the rack.",
        "Monero blockchain state is on NVMe \u2014 no action needed; it persists across reboots.",
        "Tor hidden service keys are in /var/lib/tor/ \u2014 backed up with the full config backup.",
    ]
    for p in pack:
        story.append(bullet(p, S["bullet"]))
    story.append(sp(12))

    story.append(h("Emergency: Internet Lost", S["h2"]))
    story.append(body(
        "All local services continue. ATAK, voice, mesh, and Element all work with no internet. "
        "The Cloudflare Tunnel and Headscale VPN will drop \u2014 remote viewers lose access. "
        "Everyone on the local WiFi is unaffected.",
        S["body"]
    ))
    story.append(sp(4))
    story.append(body("To air-gap intentionally (stop all clearnet egress):", S["body"]))
    story.append(CodeBlock(
        "ssh pi@192.168.8.10\n"
        "docker stop community-node-cloudflared-1\n"
        "\n"
        "ssh pi@192.168.8.20\n"
        "docker stop tactical-node-headscale-1"
    ))
    story.append(sp(12))

    story.append(h("Emergency: Pi Won't Boot", S["h2"]))
    story.append(body("Diagnostic steps:", S["body"]))
    diag = [
        "Confirm USB-C power cable is seated (Pis use USB-C PD \u2014 not all cables work).",
        "Check Anker charger output LED \u2014 should be solid, not blinking.",
        "Connect a monitor via micro-HDMI to see boot output.",
        "If kernel panic / filesystem error: boot from microSD with rescue image.",
        "If NVMe not found: check M.2 seating in the GeeekPi bracket.",
    ]
    for i, d in enumerate(diag, 1):
        story.append(numbered_item(i, d, S["numbered"]))
        story.append(sp(1))

    story.append(sp(8))
    story.append(h("What Still Works If a Pi Goes Down", S["h3"]))
    down_data = [
        [h("Pi Down", S["tbl_hdr"]), h("Services Lost", S["tbl_hdr"]), h("Services Still Available", S["tbl_hdr"])],
        [
            h("Pi #1 (comms)", S["tbl_body"]),
            h("Matrix/Element, Tor, I2P, Cloudflare Tunnel, AdGuard DNS", S["tbl_body"]),
            h("ATAK (Pi #2), Mumble, Meshtastic, Reticulum, Monerod, Headscale", S["tbl_body"]),
        ],
        [
            h("Pi #2 (tactical)", S["tbl_body"]),
            h("ATAK/OTS, Mumble, Meshtastic, Reticulum, Monerod, Headscale", S["tbl_body"]),
            h("Matrix/Element, community kiosk, Tor hidden services, AdGuard DNS", S["tbl_body"]),
        ],
    ]
    col_w = [CONTENT_W * 0.18, CONTENT_W * 0.41, CONTENT_W * 0.41]
    story.append(make_table(down_data, col_w))
    return story


def page_atak(styles):
    """ATAK Configuration."""
    S = styles
    story = []
    story.append(SectionMark("ATAK Configuration"))
    _h1_cell = h("ATAK Configuration", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))

    story.append(h("What's Built In \u2014 No Plugins Needed", S["h2"]))
    builtin = [
        "Position sharing (PLI) \u2014 live team positions on shared map",
        "GeoChat \u2014 group and private messaging within ATAK",
        "Markers and drawing tools",
        "Route planning",
        "CASEVAC reports (9-line)",
        "ExCheck checklists",
        "Track logging",
        "Offline maps (with pre-cached tiles served by OTS)",
        "Terrain analysis",
        "Geofencing",
    ]
    for b in builtin:
        story.append(bullet(b, S["bullet"]))
    story.append(sp(10))

    story.append(h("Recommended Plugins (2 Only)", S["h2"]))
    plugin_data = [
        [
            h("Plugin", S["tbl_hdr"]),
            h("Purpose", S["tbl_hdr"]),
            h("Install", S["tbl_hdr"]),
            h("Who Needs It", S["tbl_hdr"]),
        ],
        [
            h("Meshtastic ATAK Plugin", S["tbl_body"]),
            h("Direct radio-to-phone bridge for LoRa mesh", S["tbl_body"]),
            h("GitHub APK sideload", S["tbl_note"]),
            h("Operators with their own Meshtastic radio only", S["tbl_note"]),
        ],
        [
            h("VNS (Vehicle Navigation System)", S["tbl_body"]),
            h("In-ATAK turn-by-turn navigation", S["tbl_body"]),
            h("Google Play Store", S["tbl_note"]),
            h("Team leads running vehicle ops", S["tbl_note"]),
        ],
    ]
    col_w = [CONTENT_W * 0.25, CONTENT_W * 0.30, CONTENT_W * 0.20, CONTENT_W * 0.25]
    story.append(make_table(plugin_data, col_w))
    story.append(sp(10))

    story.append(h("Data Packages Pre-Loaded", S["h2"]))
    dp_data = [
        [
            h("Package", S["tbl_hdr"]),
            h("Contents", S["tbl_hdr"]),
            h("Auto-push", S["tbl_hdr"]),
        ],
        [
            h("DTED2 Florida", S["tbl_body"]),
            h("30m elevation data", S["tbl_body"]),
            h("Via enrollment data package", S["tbl_note"]),
        ],
        [
            h("PMTiles FL (578MB)", S["tbl_body"]),
            h("Offline vector maps z0\u201314", S["tbl_body"]),
            h("Served at 192.168.8.20:8080", S["tbl_note"]),
        ],
        [
            h("Community Node marker", S["tbl_body"]),
            h("M2 HQ position", S["tbl_body"]),
            h("Cron push every 4 hours", S["tbl_note"]),
        ],
    ]
    col_w = [CONTENT_W * 0.25, CONTENT_W * 0.45, CONTENT_W * 0.30]
    story.append(make_table(dp_data, col_w))
    story.append(sp(6))
    story.append(body(
        "<i>Offline map tiles are already cached \u2014 no internet needed for map display.</i>",
        S["note"]
    ))
    return story


def page_matrix(styles):
    """Matrix / Element."""
    S = styles
    story = []
    story.append(SectionMark("Matrix / Element Chat"))
    _h1_cell = h("Matrix / Element Chat", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))
    story.append(body(
        "M2 Conduit server \u2014 standalone field node. Independent of clearnet Matrix.",
        S["note"]
    ))
    story.append(sp(6))

    story.append(h("Access", S["h2"]))
    access_data = [
        [h("Method", S["tbl_hdr"]), h("URL", S["tbl_hdr"])],
        [h("On node WiFi", S["tbl_body"]),    h("http://192.168.8.10:8080", S["tbl_body"])],
        [h("Clearnet", S["tbl_body"]),        h("https://element.yourdomain.com", S["tbl_body"])],
        [h("Matrix server name", S["tbl_body"]), h("m2.yourdomain.com", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.30, CONTENT_W * 0.70]
    story.append(make_table(access_data, col_w))
    story.append(sp(10))

    story.append(h("Room Structure", S["h2"]))
    story.append(body("<b>Community Space \u2014 standing rooms:</b>", S["body"]))
    room_data = [
        [h("Room", S["tbl_hdr"]), h("Purpose", S["tbl_hdr"])],
        [h("#comms", S["tbl_body"]),      h("Radio, mesh, Reticulum, Meshtastic", S["tbl_body"])],
        [h("#medical", S["tbl_body"]),    h("First aid, trauma, community health", S["tbl_body"])],
        [h("#agriculture", S["tbl_body"]),h("Food production, permaculture", S["tbl_body"])],
        [h("#security", S["tbl_body"]),   h("Physical security, situational awareness", S["tbl_body"])],
        [h("#logistics", S["tbl_body"]),  h("Supply chain, transportation", S["tbl_body"])],
        [h("#general", S["tbl_body"]),    h("Social, announcements", S["tbl_body"])],
        [h("#onboarding", S["tbl_body"]), h("Encryption setup help, welcome resources", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.25, CONTENT_W * 0.75]
    story.append(make_table(room_data, col_w))
    story.append(sp(4))
    story.append(body(
        "Dynamic rooms are spun up as needed (mission-specific, event, emergency).",
        S["note"]
    ))
    story.append(sp(10))

    story.append(h("Encryption", S["h2"]))
    story.append(bullet("All rooms encrypted by default (E2EE enforced).", S["bullet"]))
    story.append(bullet(
        "Once encryption is on, it cannot be disabled (protocol enforced).", S["bullet"]))
    story.append(bullet(
        "New users: set up key backup before joining rooms to prevent message loss.", S["bullet"]))
    story.append(sp(10))

    roles_data = [
        [h("Role", S["tbl_hdr"]), h("Power Level", S["tbl_hdr"]), h("Who", S["tbl_hdr"])],
        [h("Admin",     S["tbl_body"]), h("100", S["tbl_body"]), h("Operator + trusted family (1\u20132 people)", S["tbl_body"])],
        [h("Moderator", S["tbl_body"]), h("50",  S["tbl_body"]), h("Promoted community members", S["tbl_body"])],
        [h("Member",    S["tbl_body"]), h("0",   S["tbl_body"]), h("Standard users", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.20, CONTENT_W * 0.20, CONTENT_W * 0.60]
    story.append(KeepTogether([h("Roles", S["h2"]), make_table(roles_data, col_w)]))
    return story


def page_quick_ref(styles):
    """Quick Reference."""
    S = styles
    story = []
    story.append(SectionMark("Quick Reference"))
    _h1_cell = h("Quick Reference \u2014 URLs & Ports", S["h1"])
    _h1_tbl = Table([[_h1_cell]], colWidths=[CONTENT_W])
    _h1_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(_h1_tbl)
    story.append(Spacer(1, 6))

    url_data = [
        [
            h("Service", S["tbl_hdr"]),
            h("LAN URL", S["tbl_hdr"]),
            h("Port", S["tbl_hdr"]),
            h("Notes", S["tbl_hdr"]),
        ],
        [h("Router admin", S["tbl_body"]),     h("http://192.168.8.1", S["tbl_body"]),       h("80", S["tbl_body"]),          h("GL.iNet admin panel", S["tbl_note"])],
        [h("Community page", S["tbl_body"]),   h("http://192.168.8.10:8081", S["tbl_body"]), h("8081", S["tbl_body"]),        h("Operator onboarding kiosk", S["tbl_note"])],
        [h("Element Web", S["tbl_body"]),      h("http://192.168.8.10:8080", S["tbl_body"]), h("8080", S["tbl_body"]),        h("Also: element.yourdomain.com", S["tbl_note"])],
        [h("OTS web map (LAN)", S["tbl_body"]),h("http://192.168.8.20:8080", S["tbl_body"]), h("8080", S["tbl_body"]),        h("Admin login required", S["tbl_note"])],
        [h("OTS web map (clearnet)", S["tbl_body"]), h("tak.yourdomain.com", S["tbl_body"]), h("443", S["tbl_body"]),      h("Cloudflare Access \u2014 OTP email login", S["tbl_note"])],
        [h("ATAK server (SSL)", S["tbl_body"]),h("192.168.8.20", S["tbl_body"]),             h("8089", S["tbl_body"]),        h("After cert enrollment", S["tbl_note"])],
        [h("ATAK enrollment", S["tbl_body"]),  h("192.168.8.20", S["tbl_body"]),             h("8446", S["tbl_body"]),        h("Auto-used during first connect", S["tbl_note"])],
        [h("Mumble voice", S["tbl_body"]),     h("192.168.8.20", S["tbl_body"]),             h("64738", S["tbl_body"]),       h("No password required by default", S["tbl_note"])],
        [h("AdGuard Home", S["tbl_body"]),     h("http://192.168.8.10:3000", S["tbl_body"]), h("3000", S["tbl_body"]),        h("DNS admin \u2014 admin/admin default", S["tbl_note"])],
        [h("Matrix federation", S["tbl_body"]),h("http://192.168.8.10:8448", S["tbl_body"]), h("8448", S["tbl_body"]),        h("Conduit federation port", S["tbl_note"])],
        [h("Headscale admin", S["tbl_body"]),  h("https://m2vpn.yourdomain.com", S["tbl_body"]), h("443", S["tbl_body"]), h("Via Cloudflare Tunnel", S["tbl_note"])],
        [h("Monerod RPC", S["tbl_body"]),      h("http://192.168.8.20:18081", S["tbl_body"]),h("18081", S["tbl_body"]),       h("Local RPC only \u2014 not exposed to WAN", S["tbl_note"])],
    ]
    col_w = [CONTENT_W * 0.20, CONTENT_W * 0.30, CONTENT_W * 0.10, CONTENT_W * 0.40]
    story.append(make_table(url_data, col_w))
    story.append(sp(12))

    story.append(h("WiFi Networks", S["h2"]))
    wifi_data = [
        [h("SSID", S["tbl_hdr"]), h("Purpose", S["tbl_hdr"]), h("Access", S["tbl_hdr"])],
        [h("CommunityNode", S["tbl_body"]), h("Field operator / EUD WiFi", S["tbl_body"]),  h("Full node access (all services)", S["tbl_body"])],
        [h("NodeAdmin",     S["tbl_body"]), h("Tech admin only", S["tbl_body"]),             h("Router admin access + all node services", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.25, CONTENT_W * 0.35, CONTENT_W * 0.40]
    story.append(make_table(wifi_data, col_w))
    story.append(sp(12))

    story.append(h("Default Credentials", S["h2"]))
    story.append(body(
        "<b>Change all passwords before deployment.</b>  "
        "Sensitive values are in M2_SECRETS.md (gitignored \u2014 local only).",
        S["body"]
    ))
    story.append(sp(4))
    cred_data = [
        [
            h("Service", S["tbl_hdr"]),
            h("Username", S["tbl_hdr"]),
            h("Password", S["tbl_hdr"]),
        ],
        [h("ATAK enrollment",          S["tbl_body"]), h(_ATAK_USER,                               S["tbl_body"]), h(_ATAK_PWORD,              S["tbl_body"])],
        [h("OTS admin",                S["tbl_body"]), h("admin",                              S["tbl_body"]), h("[see M2_SECRETS.md]",    S["tbl_note"])],
        [h("GL.iNet admin",            S["tbl_body"]), h("root",                               S["tbl_body"]), h("[see M2_SECRETS.md]",    S["tbl_note"])],
        [h("AdGuard Home",             S["tbl_body"]), h("admin",                              S["tbl_body"]), h("[see M2_SECRETS.md]",    S["tbl_note"])],
        [h("Matrix admin",             S["tbl_body"]), h("@admin:m2.yourdomain.com",           S["tbl_body"]), h("[see M2_SECRETS.md]",    S["tbl_note"])],
        [h("Mumble SuperUser",         S["tbl_body"]), h("(blank)",                            S["tbl_note"]), h("[see M2_SECRETS.md]",    S["tbl_note"])],
        [h("ATAK truststore (cert)",   S["tbl_body"]), h("(n/a)",                              S["tbl_note"]), h(_ATAK_PASS,               S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.28, CONTENT_W * 0.35, CONTENT_W * 0.37]
    story.append(make_table(cred_data, col_w))
    return story


# ── Document builder ─────────────────────────────────────────────────────────

def build_pdf():
    styles = build_styles()

    doc = BaseDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + 12,
        bottomMargin=MARGIN + 12,
        title=TITLE,
        author="Community Node Project",
        subject="Field Operations Runbook",
    )

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

    title_template = PageTemplate(
        id="title",
        frames=[title_frame],
        onPage=on_title_page,
    )
    body_template = PageTemplate(
        id="body",
        frames=[body_frame],
        onPage=on_page,
    )

    doc.addPageTemplates([title_template, body_template])

    story = []
    story += page_title(styles)
    story += page_power_on(styles)
    story += page_pre_event(styles)
    story += pages_onboarding(styles)
    story += page_during_event(styles)
    story += page_teardown(styles)
    story += page_atak(styles)
    story += page_matrix(styles)
    story += page_quick_ref(styles)

    doc.build(story)
    print(f"Generated: {OUTPUT}")
    print(f"  Page size: US Letter")


if __name__ == "__main__":
    build_pdf()
