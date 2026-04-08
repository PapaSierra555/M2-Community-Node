"""
M2 Community Node — Build Book Generator
Outputs: M2_Community_Node_Build_Book.pdf (US Letter, ~8 pages)

High-level handout for people who want to build their own node.
Not a step-by-step guide — that's M2_BUILD_GUIDE.md.

Run: python generate_build_book.py
"""

import os as _os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, PageBreak, KeepTogether,
    HRFlowable, NextPageTemplate,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

# ── Font registration ─────────────────────────────────────────────────────────
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

# ── Color palette ─────────────────────────────────────────────────────────────
ACCENT     = HexColor("#921212")
BG         = HexColor("#ffffff")
TEXT       = HexColor("#0f0f0f")
MUTED      = HexColor("#4a4a4a")
RULE_COLOR = HexColor("#dcc8c8")
CARD_BG    = HexColor("#faf6f6")
ROW_ALT    = HexColor("#faf6f6")
ROW_WHITE  = HexColor("#ffffff")
TABLE_HDR  = HexColor("#921212")
GREEN      = HexColor("#2e7d32")

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

OUTPUT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "operational-pdfs", "M2_Community_Node_Build_Book.pdf")
TITLE  = "M2 Community Node — Build Guide"
VERSION = "v1.0"


# ── Styles ────────────────────────────────────────────────────────────────────
def build_styles():
    styles = {}

    styles["title_main"] = ParagraphStyle(
        "title_main", fontName="BigShoulders", fontSize=38, leading=44,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6,
    )
    styles["title_sub"] = ParagraphStyle(
        "title_sub", fontName="Sans", fontSize=18, leading=24,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
    )
    styles["title_version"] = ParagraphStyle(
        "title_version", fontName="JuraMed", fontSize=11, leading=16,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
    )
    styles["title_tagline"] = ParagraphStyle(
        "title_tagline", fontName="SansItalic", fontSize=10, leading=14,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=4,
    )
    styles["title_license"] = ParagraphStyle(
        "title_license", fontName="Sans", fontSize=9, leading=13,
        textColor=MUTED, alignment=TA_CENTER, spaceAfter=2,
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontName="BigShoulders", fontSize=18, leading=22,
        textColor=white, spaceBefore=0, spaceAfter=8,
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontName="SansBold", fontSize=13, leading=17,
        textColor=ACCENT, spaceBefore=12, spaceAfter=4,
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontName="SansBold", fontSize=10, leading=14,
        textColor=ACCENT, spaceBefore=8, spaceAfter=3,
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="Sans", fontSize=9, leading=13,
        textColor=TEXT, spaceBefore=2, spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontName="Sans", fontSize=9, leading=13,
        textColor=TEXT, spaceBefore=1, spaceAfter=1,
        leftIndent=14, bulletIndent=0,
    )
    styles["note"] = ParagraphStyle(
        "note", fontName="SansItalic", fontSize=8, leading=12,
        textColor=MUTED, spaceBefore=2, spaceAfter=4,
    )
    styles["tbl_hdr"] = ParagraphStyle(
        "tbl_hdr", fontName="SansBold", fontSize=8, leading=11,
        textColor=white,
    )
    styles["tbl_body"] = ParagraphStyle(
        "tbl_body", fontName="Sans", fontSize=8, leading=11, textColor=TEXT,
    )
    styles["tbl_body_bold"] = ParagraphStyle(
        "tbl_body_bold", fontName="SansBold", fontSize=8, leading=11, textColor=TEXT,
    )
    styles["tbl_note"] = ParagraphStyle(
        "tbl_note", fontName="SansItalic", fontSize=7.5, leading=10, textColor=MUTED,
    )
    styles["tbl_green"] = ParagraphStyle(
        "tbl_green", fontName="SansBold", fontSize=8, leading=11, textColor=GREEN,
    )

    return styles


# ── Header/Footer ─────────────────────────────────────────────────────────────
section_registry = {}


def on_page(canvas, doc):
    page_num = doc.page
    section = section_registry.get(page_num, "")
    canvas.saveState()

    if page_num > 1:
        # ACCENT header bar
        canvas.setFillColor(ACCENT)
        canvas.rect(0, PAGE_H - 0.45 * inch, PAGE_W, 0.45 * inch, fill=1, stroke=0)
        canvas.setFillColor(BG)
        canvas.setFont("SansBold", 8)
        canvas.drawString(MARGIN, PAGE_H - 0.28 * inch, TITLE)
        canvas.setFillColor(MUTED)
        canvas.setFont("Sans", 7.5)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.28 * inch, f"Page {page_num}")

    y_ftr = MARGIN - 16
    canvas.setStrokeColor(RULE_COLOR)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    if section:
        canvas.drawString(MARGIN, y_ftr, section)
    canvas.drawCentredString(PAGE_W / 2, y_ftr, "M2 Community Node Build Guide v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, f"Page {page_num}")
    canvas.restoreState()


def on_title_page(canvas, doc):
    canvas.saveState()
    y_ftr = MARGIN - 16
    canvas.setStrokeColor(RULE_COLOR)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, y_ftr + 10, PAGE_W - MARGIN, y_ftr + 10)
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(PAGE_W / 2, y_ftr, "M2 Community Node Build Guide v1.0")
    canvas.drawRightString(PAGE_W - MARGIN, y_ftr, "Page 1")
    canvas.restoreState()


# ── Helper flowables ──────────────────────────────────────────────────────────
class SectionMark(Flowable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.width = 0
        self.height = 0

    def draw(self):
        page = self.canv._doctemplate.page
        section_registry[page] = self.name


class CodeBlock(Flowable):
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
    n_rows = len(data)
    base_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  TABLE_HDR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  white),
        ("FONTNAME",      (0, 0), (-1, 0),  "SansBold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  5),
        ("TOPPADDING",    (0, 0), (-1, 0),  5),
        ("FONTNAME",      (0, 1), (-1, -1), "Sans"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.3, RULE_COLOR),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [ROW_ALT, ROW_WHITE]),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
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


def h1_banner(text, S):
    """Wrap an h1 Paragraph in an ACCENT background Table banner."""
    cell = h(text, S["h1"])
    t = Table([[cell]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


# ── Sections ──────────────────────────────────────────────────────────────────

def page_title(styles):
    S = styles
    story = []
    story.append(NextPageTemplate("title"))
    story.append(sp(2 * inch))
    story.append(h("M2 COMMUNITY NODE", S["title_main"]))
    story.append(sp(8))
    story.append(h("Build Guide", S["title_sub"]))
    story.append(sp(16))
    story.append(h("v1.0  |  April 2026", S["title_version"]))
    story.append(sp(8))
    story.append(h(
        "Build your own field-portable community communications node \u2014 "
        "ATAK \u00b7 Matrix \u00b7 Mesh \u00b7 Monero",
        S["title_tagline"]
    ))
    story.append(sp(8))
    story.append(sp(32))
    story.append(rule())
    story.append(sp(8))
    story.append(h("CC BY-NC-SA 4.0", S["title_license"]))
    story.append(h("yourdomain.com", S["title_license"]))
    return story


def page_overview(styles):
    S = styles
    story = []
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    story.append(SectionMark("System Capabilities"))
    story.append(sp(12))
    story.append(h1_banner("System Capabilities", S))
    story.append(sp(8))

    cap_data = [
        [h("Capability", S["tbl_hdr"]),          h("Technology", S["tbl_hdr"]),               h("Internet?", S["tbl_hdr"])],
        [h("Tactical maps & positions", S["tbl_body"]),   h("OpenTAK Server + ATAK", S["tbl_body"]),         h("No", S["tbl_green"])],
        [h("Encrypted group chat", S["tbl_body"]),        h("Matrix (Conduit) + Element Web", S["tbl_body"]), h("No", S["tbl_green"])],
        [h("Push-to-talk voice", S["tbl_body"]),          h("Mumble + Mumla app", S["tbl_body"]),             h("No", S["tbl_green"])],
        [h("Off-grid mesh radio", S["tbl_body"]),         h("Reticulum + Meshtastic (LoRa)", S["tbl_body"]),  h("No", S["tbl_green"])],
        [h("Anonymous access", S["tbl_body"]),            h("Tor hidden services + I2P", S["tbl_body"]),      h("No", S["tbl_green"])],
        [h("Clearnet remote access", S["tbl_body"]),      h("Cloudflare Tunnel", S["tbl_body"]),              h("Yes", S["tbl_note"])],
        [h("Remote VPN", S["tbl_body"]),                  h("Headscale (self-hosted WireGuard)", S["tbl_body"]), h("Yes", S["tbl_note"])],
        [h("DNS filtering + Android bypass", S["tbl_body"]), h("AdGuard Home", S["tbl_body"]),                h("No", S["tbl_green"])],
        [h("Financial sovereignty", S["tbl_body"]),       h("Monero pruned node", S["tbl_body"]),             h("No", S["tbl_green"])],
    ]
    col_w = [CONTENT_W * 0.35, CONTENT_W * 0.47, CONTENT_W * 0.18]
    story.append(make_table(cap_data, col_w))
    story.append(sp(10))

    principles_block = [h("Design Principles", S["h2"])]
    for p in [
        "Privacy-first. Censorship-resistant. Open-source only.",
        "Field-deployable in under 15 minutes \u2014 wall power, vehicle 12V, or UPS.",
        "Commodity hardware only. No vendor lock-in. ~$994 recommended build.",
        "All core services run with zero internet \u2014 air-gap capable.",
        "Built on two Raspberry Pi 5 16GB boards. Easy to source, easy to replace.",
    ]:
        principles_block.append(bullet(p, S["bullet"]))
    story.append(KeepTogether(principles_block))
    return story


def page_architecture(styles):
    S = styles
    story = []
    story.append(PageBreak())
    story.append(SectionMark("System Architecture"))
    story.append(sp(12))
    story.append(h1_banner("System Architecture", S))
    story.append(sp(8))

    arch_text = (
        "  INTERNET / CELLULAR\n"
        "         |\n"
        "  [GL.iNet Slate AX]  192.168.8.1\n"
        "  WiFi: CommunityNode / NodeAdmin\n"
        "         |\n"
        "  [TP-Link TL-SG108S Switch]\n"
        "    |                   |\n"
        "[Pi #1 Comms]     [Pi #2 Tactical]\n"
        "192.168.8.10      192.168.8.20\n"
        "256GB NVMe        1TB NVMe\n"
        "    |                   |\n"
        "Conduit (Matrix)   OpenTAK Server\n"
        "Element Web        Mumble\n"
        "Nginx              Reticulum\n"
        "Tor + I2P          NomadNet\n"
        "Cloudflared        Monerod\n"
        "AdGuard Home       Headscale\n"
        "                   [LEFT LoRa: RNode / Reticulum]\n"
        "                   [RIGHT LoRa: Meshtastic]"
    )
    story.append(CodeBlock(arch_text))
    story.append(sp(10))

    story.append(h("Node Roles", S["h2"]))
    node_data = [
        [h("", S["tbl_hdr"]),             h("Pi #1 \u2014 Comms", S["tbl_hdr"]),          h("Pi #2 \u2014 Tactical", S["tbl_hdr"])],
        [h("IP", S["tbl_body_bold"]),      h("192.168.8.10", S["tbl_body"]),                h("192.168.8.20", S["tbl_body"])],
        [h("Storage", S["tbl_body_bold"]), h("256GB M.2 2230 NVMe", S["tbl_body"]),         h("1TB M.2 2230 NVMe", S["tbl_body"])],
        [h("Key services", S["tbl_body_bold"]), h("Matrix, Element, Nginx, Tor, I2P, Cloudflared, AdGuard", S["tbl_body"]), h("OpenTAK Server, Mumble, Reticulum, Monerod, Headscale", S["tbl_body"])],
        [h("Radio", S["tbl_body_bold"]),   h("None", S["tbl_note"]),                        h("2\u00d7 Heltec V3 LoRa (USB)", S["tbl_body"])],
        [h("Runtime mode", S["tbl_body_bold"]), h("Docker Compose", S["tbl_body"]),         h("OpenTAK = native systemd; others = Docker", S["tbl_body"])],
    ]
    col_w = [CONTENT_W * 0.20, CONTENT_W * 0.40, CONTENT_W * 0.40]
    story.append(make_table(node_data, col_w))
    story.append(sp(10))

    story.append(h("Rack Layout", S["h2"]))
    rack_text = (
        "U8  Custom 1U LoRa panel  [LEFT: RNode]  [RIGHT: Meshtastic]\n"
        "U7  GeeekPi 2U Touchscreen (node status display)\n"
        "U6  (touchscreen continues)\n"
        "U5  GL.iNet Slate AX + TP-Link Switch (shared 1U shelf)\n"
        "U4  GeeekPi 1U Dual Pi 5 Mount  [Pi #1 | Pi #2]  (NVMe built in)\n"
        "U3  Open\n"
        "U2  Tupavco PDU (rear rails, outlets face inward)\n"
        "U1  Tripp Lite BC600R UPS (rack floor)"
    )
    story.append(CodeBlock(rack_text))
    return story


def page_bom(styles):
    S = styles
    story = []
    story.append(PageBreak())
    story.append(SectionMark("Bill of Materials"))
    story.append(sp(12))
    story.append(h1_banner("Bill of Materials", S))
    story.append(sp(8))
    story.append(body(
        "All prices are approximate (verified Feb\u2013Apr 2026). "
        "Verify before ordering \u2014 Pi 5 and M.2 2230 prices fluctuate.",
        S["note"]
    ))
    story.append(sp(6))

    # ---- Compute & Storage ----
    story.append(h("Compute & Storage", S["h2"]))
    compute_data = [
        [h("Item", S["tbl_hdr"]),                              h("Qty", S["tbl_hdr"]), h("Est. Price", S["tbl_hdr"]), h("Where", S["tbl_hdr"])],
        [h("Raspberry Pi 5 16GB", S["tbl_body"]),              h("2",   S["tbl_body"]), h("~$160 ea",   S["tbl_body"]), h("Amazon/PiShop.us",  S["tbl_note"])],
        [h("Pi 5 Official Active Cooler", S["tbl_body"]),      h("2",   S["tbl_body"]), h("~$11 ea",    S["tbl_body"]), h("PiShop.us",         S["tbl_note"])],
        [h("GeeekPi 1U Dual Pi5 Mount (B0F7XBVV4D)", S["tbl_body"]), h("1", S["tbl_body"]), h("~$60",  S["tbl_body"]), h("Amazon",            S["tbl_note"])],
        [h("WD SN740 256GB M.2 2230 NVMe \u2014 Pi #1", S["tbl_body"]), h("1", S["tbl_body"]), h("~$40", S["tbl_body"]), h("Amazon (B0C6MVP42M)", S["tbl_note"])],
        [h("Crucial P310 1TB M.2 2230 NVMe \u2014 Pi #2", S["tbl_body"]), h("1", S["tbl_body"]), h("~$130", S["tbl_body"]), h("Amazon/Newegg",  S["tbl_note"])],
        [h("SanDisk Extreme 32GB microSD \u00d72", S["tbl_body"]), h("2", S["tbl_body"]), h("~$12 ea",  S["tbl_body"]), h("Amazon",            S["tbl_note"])],
    ]
    col_w = [CONTENT_W * 0.42, CONTENT_W * 0.08, CONTENT_W * 0.15, CONTENT_W * 0.35]
    story.append(make_table(compute_data, col_w))
    story.append(sp(8))

    # ---- Rack & Networking ----
    story.append(h("Rack & Networking", S["h2"]))
    rack_data = [
        [h("Item", S["tbl_hdr"]),                              h("Qty", S["tbl_hdr"]), h("Est. Price", S["tbl_hdr"]), h("Where", S["tbl_hdr"])],
        [h("GeeekPi 8U 10\u201d Mini Rack (RackMate T1)", S["tbl_body"]), h("1", S["tbl_body"]), h("~$95",    S["tbl_body"]), h("Amazon",              S["tbl_note"])],
        [h("GeeekPi 2U Touchscreen Display", S["tbl_body"]),  h("1",   S["tbl_body"]), h("~$70",      S["tbl_body"]), h("Amazon",              S["tbl_note"])],
        [h("GL.iNet Slate AX (AXT1800)", S["tbl_body"]),       h("1",   S["tbl_body"]), h("~$120",     S["tbl_body"]), h("GL.iNet store",       S["tbl_note"])],
        [h("TP-Link TL-SG108S 8-Port Switch", S["tbl_body"]), h("1",   S["tbl_body"]), h("~$27",      S["tbl_body"]), h("Amazon/CompSource",   S["tbl_note"])],
        [h("1U Shelf (for switch + GL.iNet)", S["tbl_body"]),  h("1",   S["tbl_body"]), h("~$18",      S["tbl_body"]), h("Amazon",              S["tbl_note"])],
        [h("Short Cat6 patch cables (6\u201d\u20131\u2019), 5-pack", S["tbl_body"]), h("1", S["tbl_body"]), h("~$12", S["tbl_body"]), h("Amazon", S["tbl_note"])],
    ]
    story.append(make_table(rack_data, col_w))
    story.append(sp(8))

    # ---- Power ----
    story.append(h("Power", S["h2"]))
    power_data = [
        [h("Item", S["tbl_hdr"]),                              h("Qty", S["tbl_hdr"]), h("Est. Price", S["tbl_hdr"]), h("Where", S["tbl_hdr"])],
        [h("Anker 747 GaNPrime 150W Charger", S["tbl_body"]), h("1",   S["tbl_body"]), h("~$65",      S["tbl_body"]), h("Amazon (B09W2PNLX7)", S["tbl_note"])],
        [h("Tupavco 10\u201d 1U Rack PDU", S["tbl_body"]),    h("1",   S["tbl_body"]), h("~$35",      S["tbl_body"]), h("Amazon",              S["tbl_note"])],
        [h("Tripp Lite BC600R UPS (600VA/300W)", S["tbl_body"]), h("1", S["tbl_body"]), h("~$70",     S["tbl_body"]), h("DigiKey / Amazon",    S["tbl_note"])],
        [h("USB-C to USB-C cables 1\u2019 3-pack", S["tbl_body"]), h("1", S["tbl_body"]), h("~$10",  S["tbl_body"]), h("Amazon",              S["tbl_note"])],
        [h("Micro HDMI to HDMI cables 2-pack", S["tbl_body"]), h("1",  S["tbl_body"]), h("~$10",      S["tbl_body"]), h("Amazon",              S["tbl_note"])],
    ]
    story.append(make_table(power_data, col_w))

    story.append(PageBreak())

    # ---- Radio ----
    story.append(h("Radio (LoRa)", S["h2"]))
    radio_data = [
        [h("Item", S["tbl_hdr"]),                              h("Qty", S["tbl_hdr"]), h("Est. Price", S["tbl_hdr"]), h("Where", S["tbl_hdr"])],
        [h("Heltec WiFi LoRa 32 V3 915MHz", S["tbl_body"]),   h("2",   S["tbl_body"]), h("~$20 ea",   S["tbl_body"]), h("heltec.org / Rokland", S["tbl_note"])],
        [h("U.FL\u2013to\u2013SMA pigtail 6\u201d (IPEX)", S["tbl_body"]), h("2", S["tbl_body"]), h("~$5 ea", S["tbl_body"]), h("Amazon", S["tbl_note"])],
        [h("915 MHz LoRa antenna (SMA-F)", S["tbl_body"]),     h("2",   S["tbl_body"]), h("~$8 ea",    S["tbl_body"]), h("Amazon",              S["tbl_note"])],
    ]
    story.append(make_table(radio_data, col_w))
    story.append(sp(10))

    # Budget summary
    budget_data = [
        [h("Category", S["tbl_hdr"]),          h("Est. Subtotal", S["tbl_hdr"])],
        [h("Compute & Storage", S["tbl_body"]), h("~$396",  S["tbl_body"])],
        [h("Rack & Networking", S["tbl_body"]), h("~$342",  S["tbl_body"])],
        [h("Power", S["tbl_body"]),             h("~$190",  S["tbl_body"])],
        [h("Radio", S["tbl_body"]),             h("~$66",   S["tbl_body"])],
        [h("<b>TOTAL</b>", S["tbl_body_bold"]), h("<b>~$994</b>", S["tbl_body_bold"])],
    ]
    bw = [CONTENT_W * 0.65, CONTENT_W * 0.35]
    story.append(make_table(budget_data, bw))
    return story


def page_phases(styles):
    S = styles
    story = []
    story.append(PageBreak())
    story.append(SectionMark("Build Phases"))
    story.append(sp(12))
    story.append(h1_banner("Build Phases", S))
    story.append(sp(8))
    story.append(body(
        "Full step-by-step instructions are in <b>M2_BUILD_GUIDE.md</b>. "
        "This is the phase summary \u2014 what happens in what order and roughly how long it takes.",
        S["note"]
    ))
    story.append(sp(6))

    phase_data = [
        [h("Phase", S["tbl_hdr"]),                      h("What Happens", S["tbl_hdr"]),                                                          h("Est. Time", S["tbl_hdr"])],
        [h("0 \u2014 Pre-Build", S["tbl_body_bold"]),   h("Monero pre-sync on x86 PC. Software downloads. microSD prep.", S["tbl_body"]),           h("1\u20132 days", S["tbl_note"])],
        [h("1 \u2014 Rack Assembly", S["tbl_body_bold"]), h("Physical rack build. Cable management. Component mounting.", S["tbl_body"]),           h("1\u20132 hours", S["tbl_note"])],
        [h("2 \u2014 Network Baseline", S["tbl_body_bold"]), h("GL.iNet WiFi config. DHCP. Static IPs for both Pis. DNS overrides.", S["tbl_body"]), h("30 min", S["tbl_note"])],
        [h("3 \u2014 OS & Base Config", S["tbl_body_bold"]), h("Raspberry Pi OS Lite on both Pis. Docker. SSH hardening. NVMe boot.", S["tbl_body"]), h("1\u20132 hours", S["tbl_note"])],
        [h("4 \u2014 Pi #1 Comms Stack", S["tbl_body_bold"]), h("Conduit, Element Web, Nginx, i2pd, Tor, Cloudflared, AdGuard Home.", S["tbl_body"]), h("1\u20132 hours", S["tbl_note"])],
        [h("5 \u2014 Pi #2 Tactical Stack", S["tbl_body_bold"]), h("OpenTAK Server (native), Monero rsync, Reticulum, Headscale, Mumble.", S["tbl_body"]), h("1\u20132 hours", S["tbl_note"])],
        [h("6 \u2014 LoRa Radio Setup", S["tbl_body_bold"]), h("Flash LEFT Heltec with RNode firmware. Flash RIGHT Heltec with Meshtastic.", S["tbl_body"]), h("30 min", S["tbl_note"])],
        [h("7 \u2014 Integration Testing", S["tbl_body_bold"]), h("ATAK connect. GeoChat. Position sharing. Matrix federation check. Mesh verify.", S["tbl_body"]), h("30\u201360 min", S["tbl_note"])],
        [h("8 \u2014 Field Hardening", S["tbl_body_bold"]), h("Firewall rules. Backup. Credential rotation. Field card print. Kiosk setup.", S["tbl_body"]), h("30 min", S["tbl_note"])],
    ]
    col_w = [CONTENT_W * 0.25, CONTENT_W * 0.55, CONTENT_W * 0.20]
    story.append(make_table(phase_data, col_w))
    story.append(sp(10))

    timeline_block = [h("Timeline Reality Check", S["h2"])]
    for t in [
        "<b>Monero sync is the long pole.</b>  Do it first, in parallel, on any spare x86 PC. "
        "The Pi 5 cannot sync Monero from scratch in a reasonable timeframe \u2014 always rsync from a pre-synced machine.",
        "<b>Phases 1\u20138 take one focused day.</b>  With the Monero DB ready, the full rack build "
        "and software stack is a one-day project for someone comfortable with Linux and SSH.",
        "<b>Phases 4\u20135 are the hardest.</b>  OpenTAK Server installs its own PostgreSQL and RabbitMQ "
        "\u2014 follow the official OTS install script exactly. Do not use Docker for OTS.",
    ]:
        timeline_block.append(bullet(t, S["bullet"]))
    story.append(KeepTogether(timeline_block))
    return story


def page_software(styles):
    S = styles
    story = []
    story.append(PageBreak())
    story.append(SectionMark("Software Stack"))
    story.append(sp(12))
    story.append(h1_banner("Software Stack", S))
    story.append(sp(8))
    story.append(body("All open-source. All self-hosted. No SaaS, no subscriptions.", S["note"]))
    story.append(sp(6))

    svc_data = [
        [h("Service", S["tbl_hdr"]), h("Node", S["tbl_hdr"]), h("What It Does", S["tbl_hdr"]), h("Runtime", S["tbl_hdr"])],
        [h("Conduit", S["tbl_body"]),         h("Pi #1", S["tbl_body"]), h("Matrix homeserver \u2014 encrypted group chat", S["tbl_body"]),              h("Docker", S["tbl_note"])],
        [h("Element Web", S["tbl_body"]),     h("Pi #1", S["tbl_body"]), h("Browser-based Matrix client", S["tbl_body"]),                                  h("Docker", S["tbl_note"])],
        [h("Nginx", S["tbl_body"]),           h("Pi #1", S["tbl_body"]), h("Reverse proxy \u2014 routes all Pi #1 traffic", S["tbl_body"]),                h("Docker", S["tbl_note"])],
        [h("Tor", S["tbl_body"]),             h("Pi #1", S["tbl_body"]), h("Hidden service (.onion) for Matrix + community page", S["tbl_body"]),          h("Docker", S["tbl_note"])],
        [h("i2pd", S["tbl_body"]),            h("Pi #1", S["tbl_body"]), h("I2P eepsite \u2014 community page on I2P", S["tbl_body"]),                     h("Docker", S["tbl_note"])],
        [h("Cloudflared", S["tbl_body"]),     h("Pi #1", S["tbl_body"]), h("Clearnet tunnel \u2014 exposes Matrix/Element/OTS to internet", S["tbl_body"]),h("Docker", S["tbl_note"])],
        [h("AdGuard Home", S["tbl_body"]),    h("Pi #1", S["tbl_body"]), h("DNS resolver + ad blocking \u2014 also bypasses Android Private DNS", S["tbl_body"]), h("Docker", S["tbl_note"])],
        [h("OpenTAK Server", S["tbl_body"]), h("Pi #2", S["tbl_body"]), h("TAK CoT relay server \u2014 ATAK connect, positions, GeoChat, web map", S["tbl_body"]), h("Systemd (native)", S["tbl_note"])],
        [h("Mumble", S["tbl_body"]),          h("Pi #2", S["tbl_body"]), h("Push-to-talk voice (use Mumla on Android)", S["tbl_body"]),                    h("Docker", S["tbl_note"])],
        [h("Reticulum + NomadNet", S["tbl_body"]), h("Pi #2", S["tbl_body"]), h("Encrypted mesh transport + LoRa BBS", S["tbl_body"]),                    h("Python service", S["tbl_note"])],
        [h("Monerod", S["tbl_body"]),         h("Pi #2", S["tbl_body"]), h("Pruned Monero node \u2014 community privacy coin endpoint", S["tbl_body"]),    h("Docker", S["tbl_note"])],
        [h("Headscale", S["tbl_body"]),       h("Pi #2", S["tbl_body"]), h("Self-hosted WireGuard VPN coordination \u2014 remote ATAK access", S["tbl_body"]), h("Docker", S["tbl_note"])],
        [h("Mosquitto", S["tbl_body"]),       h("Pi #2", S["tbl_body"]), h("MQTT broker for IoT/sensor integration", S["tbl_body"]),                       h("Docker", S["tbl_note"])],
    ]
    svc_style = [
        ("TOPPADDING",    (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 2),
        ("TOPPADDING",    (0, 0), (-1, 0),  4),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  4),
    ]
    col_w = [CONTENT_W * 0.20, CONTENT_W * 0.10, CONTENT_W * 0.52, CONTENT_W * 0.18]
    story.append(make_table(svc_data, col_w, style_cmds=svc_style))
    story.append(sp(10))

    story.append(h("Operating System", S["h2"]))
    story.append(body(
        "<b>Raspberry Pi OS Lite (64-bit, Bookworm)</b> on both Pis. "
        "No desktop environment \u2014 headless SSH only. "
        "Docker Engine (not Docker Desktop) manages all containerized services.",
        S["body"]
    ))
    return story


def page_skills_and_resources(styles):
    S = styles
    story = []
    story.append(PageBreak())
    story.append(SectionMark("Skills & Key Gotchas"))
    story.append(sp(12))
    story.append(h1_banner("Skills You\u2019ll Need", S))
    story.append(sp(8))

    skills_data = [
        [h("Skill", S["tbl_hdr"]),                    h("Required For", S["tbl_hdr"]),                    h("Level", S["tbl_hdr"])],
        [h("Linux command line (SSH)", S["tbl_body"]), h("Everything \u2014 all config is CLI-based", S["tbl_body"]),      h("Comfortable", S["tbl_note"])],
        [h("Docker Compose", S["tbl_body"]),           h("Pi #1 full stack + most Pi #2 services", S["tbl_body"]),         h("Basic", S["tbl_note"])],
        [h("Networking basics", S["tbl_body"]),        h("IP assignment, DNS, firewall rules", S["tbl_body"]),              h("Basic", S["tbl_note"])],
        [h("Systemd", S["tbl_body"]),                  h("OpenTAK Server management and troubleshooting", S["tbl_body"]),  h("Basic", S["tbl_note"])],
        [h("Git + file transfer (SCP)", S["tbl_body"]),h("Config deployment, script updates", S["tbl_body"]),              h("Basic", S["tbl_note"])],
        [h("ATAK app familiarity", S["tbl_body"]),     h("Integration testing (Phase 7)", S["tbl_body"]),                  h("Helpful", S["tbl_note"])],
    ]
    col_w = [CONTENT_W * 0.30, CONTENT_W * 0.50, CONTENT_W * 0.20]
    story.append(make_table(skills_data, col_w))
    story.append(sp(10))

    gotchas_block = [h("Key Gotchas \u2014 Read These Before You Start", S["h2"])]
    for g in [
        "<b>Monero MUST be pre-synced on an x86 machine.</b>  Syncing natively on ARM Pi takes weeks. "
        "Sync on a spare laptop or desktop, then rsync the blockchain directory to Pi #2.",
        "<b>OpenTAK Server is NOT Docker.</b>  It installs its own PostgreSQL and RabbitMQ via the "
        "official install script. Do not try to containerize it \u2014 use the native systemd install.",
        "<b>Both Heltec V3 LoRa boards are identical hardware.</b>  The only difference is firmware: "
        "LEFT panel position gets RNode (Reticulum), RIGHT gets Meshtastic. Label them before flashing.",
        "<b>GL.iNet DNS overrides are required.</b>  Set static DNS entries on the GL.iNet router "
        "pointing matrix.yourdomain.com and atakenroll.yourdomain.com to the correct Pi IPs. "
        "Without this, Cloudflare-tunneled domains won't resolve on the local LAN.",
        "<b>NVMe must be M.2 2230 form factor.</b>  Standard 2280 drives will not fit in the GeeekPi "
        "dual mount. Verify the 2230 suffix before ordering \u2014 prices are volatile (Steam Deck demand).",
        "<b>Android phones block local DNS by default.</b>  The AdGuard Home container on Pi #1 handles "
        "DNS resolution for the LAN. GL.iNet DHCP serves Pi #1 (192.168.8.10) as the DNS server.",
        "<b>ATAK needs 'Consistent' reporting.</b>  Stationary phones default to event-driven reporting "
        "and won't appear on the map. Tell all users: Settings \u2192 Reporting \u2192 Consistent.",
    ]:
        gotchas_block.append(bullet(g, S["bullet"]))
    story.append(KeepTogether(gotchas_block[:4]))
    story.append(KeepTogether(gotchas_block[4:]))
    story.append(sp(10))

    story.append(h("Full Documentation", S["h2"]))
    res_data = [
        [h("Resource", S["tbl_hdr"]),                           h("Contents", S["tbl_hdr"])],
        [h("M2_BUILD_GUIDE.md", S["tbl_body_bold"]),            h("Complete step-by-step build (all phases, all commands)", S["tbl_body"])],
        [h("M2_Community_Node_Runbook.pdf", S["tbl_body_bold"]),h("Field operations guide \u2014 power-on, onboarding, troubleshooting", S["tbl_body"])],
        [h("M2_MiniRack_Hardware_BOM.md", S["tbl_body_bold"]),  h("Full BOM with ASINs, verified pricing, rack layout details", S["tbl_body"])],
        [h("M2_ATAK_Connectivity_Guide.md", S["tbl_body_bold"]),h("ATAK onboarding deep dive \u2014 all three connection paths", S["tbl_body"])],
        [h("M2_MASTER_COMMUNITY_NODE_PLAN.md", S["tbl_body_bold"]), h("Architecture, service inventory, design rationale", S["tbl_body"])],
        [h("github.com/PapaSierra555/M2-Community-Node", S["tbl_body"]), h("All source files, scripts, and generators", S["tbl_body"])],
    ]
    story.append(make_table(res_data, [CONTENT_W * 0.38, CONTENT_W * 0.62]))
    return story


# ── Document builder ──────────────────────────────────────────────────────────
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
        subject="Build Guide",
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
        PAGE_H - 2 * MARGIN - 40,
        id="body_frame",
    )

    doc.addPageTemplates([
        PageTemplate(id="title", frames=[title_frame], onPage=on_title_page),
        PageTemplate(id="body",  frames=[body_frame],  onPage=on_page),
    ])

    story = []
    story += page_title(styles)
    story += page_overview(styles)
    story += page_architecture(styles)
    story += page_bom(styles)
    story += page_phases(styles)
    story += page_software(styles)
    story += page_skills_and_resources(styles)

    doc.build(story)
    print(f"Generated: {OUTPUT}")
    print(f"  Page size: US Letter")


if __name__ == "__main__":
    build_pdf()
