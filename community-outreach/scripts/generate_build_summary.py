"""
M2 Community Node — Build Summary (1-page)
LFHI outreach marketing package
Output: ../pdf/M2_Build_Summary.pdf
"""
import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import qrcode, io

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../scripts/fonts")

BG        = HexColor("#ffffff")
TEXT      = HexColor("#0f0f0f")
MUTED     = HexColor("#4a4a4a")
ACCENT    = HexColor("#921212")
ACCENT_LT = HexColor("#f9e0e0")
RULE      = HexColor("#dcc8c8")
CARD_BG   = HexColor("#faf6f6")
CARD_BRD  = HexColor("#e4d0d0")
GREEN_PRT = HexColor("#1a7a3a")
AMBER_PRT = HexColor("#a06010")
RED_PRT   = HexColor("#8b1a1a")

pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{FONTS}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoBold",     f"{FONTS}/IBMPlexMono-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SansItalic",   f"{FONTS}/InstrumentSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Jura",         f"{FONTS}/Jura-Light.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))

W, H = letter  # 612 x 792
M = 36

_script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pdf", "M2_Build_Summary.pdf"
)


# ── Helpers ────────────────────────────────────────────────────────────────

def rule(c, x, y, w, col=None, lw=0.5):
    c.setStrokeColor(col or RULE); c.setLineWidth(lw); c.line(x, y, x+w, y)

def card(c, x, y, w, h, r=3):
    c.setFillColor(CARD_BG); c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)

def section_label(c, x, y, text):
    c.setFont("JuraMed", 7); c.setFillColor(ACCENT)
    cx = x
    for ch in text.upper():
        c.drawString(cx, y, ch); cx += c.stringWidth(ch, "JuraMed", 7) + 1.8

def section_header(c, x, y, text):
    """Prominent section header — JuraMed 11pt with rule."""
    c.setFont("JuraMed", 11); c.setFillColor(ACCENT)
    c.drawString(x, y, text.upper())
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    c.line(x, y - 4, W - M, y - 4)

def wrap_lines(c, text, font, size, max_w):
    words = text.split(); lines = []; line = []
    for w in words:
        test = " ".join(line + [w])
        if c.stringWidth(test, font, size) <= max_w: line.append(w)
        else: lines.append(" ".join(line)); line = [w]
    if line: lines.append(" ".join(line))
    return lines

def qr_image(url, size_pts):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    from reportlab.lib.utils import ImageReader
    return ImageReader(buf)

def footer(c):
    rule(c, M, 52, W - 2*M)
    c.setFont("Sans", 7); c.setFillColor(MUTED)
    c.drawString(M, 40,
        "License: CC BY-NC-SA 4.0 \u2014 Build one for your community. Cannot be sold.")
    c.setFillColor(MUTED)
    c.drawRightString(W - M, 40, "Capable Enough Project")

def header_band(c, title, subtitle):
    c.setFillColor(ACCENT)
    c.rect(0, H - 62, W, 62, fill=1, stroke=0)
    c.setFont("BigShoulders", 26); c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, H - 36, title)
    c.setFont("Sans", 10)
    c.drawString(M + 8, H - 52, subtitle)
    # CCC26 × LFHI badge
    logo_path = os.path.join(_script_dir, "..", "assets", "lfhi-logo.png")
    badge_w = 86; badge_h = 46
    badge_x = W - M - badge_w - 4; badge_y = H - 56
    c.setFillColor(HexColor("#111111"))
    c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(0.5)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 3, fill=1, stroke=1)
    c.setFont("BigShoulders", 13)
    c.setFillColor(HexColor("#c92a2a"))
    c.drawString(badge_x + 6, badge_y + 24, "CCC26")
    c.setFont("MonoBold", 9)
    c.setFillColor(HexColor("#ffffff"))
    c.drawString(badge_x + 6, badge_y + 10, "LFHI")
    c.setStrokeColor(HexColor("#444444"))
    c.setLineWidth(0.5)
    c.line(badge_x + 40, badge_y + 7, badge_x + 40, badge_y + 39)
    if os.path.exists(logo_path):
        logo_size = 36
        c.drawImage(logo_path, badge_x + 44, badge_y + 5,
                    logo_size, logo_size, preserveAspectRatio=True)

def draw_bullet(c, x, y, text, font="Sans", size=9, color=None,
                indent=10, max_w=None):
    col = color or TEXT
    text_x = x + indent
    effective_w = max_w or (W - M - x - 8)
    c.setFont(font, size); c.setFillColor(col)
    c.drawString(x + 4, y, "\u2022")
    lines = wrap_lines(c, text, font, size, effective_w - indent)
    leading = size * 1.35
    for i, ln in enumerate(lines):
        tx = text_x if i == 0 else text_x + 4
        c.drawString(tx, y - (i * leading) + (leading - size) * 0.2, ln)
    return y - (len(lines) * leading)


# ── Cost tier cards ────────────────────────────────────────────────────────

def draw_cost_cards(c):
    card_top = 710
    card_bot = 592
    card_h   = card_top - card_bot
    card_gap = 8
    card_w   = (W - 2*M - 2*card_gap) / 3

    cost_cards = [
        {
            "label":   "RECOMMENDED",
            "label_col": GREEN_PRT,
            "price":   "~$1,385",
            "lines": [
                ("Dual Raspberry Pi 5 16GB",         "Sans",  8,  MUTED),
                ("Full redundancy. Both service stacks.", "Sans", 8, MUTED),
                ("Best for active chapters with",       "SansItalic", 8, MUTED),
                ("regular deployments.",               "SansItalic", 8, MUTED),
            ],
        },
        {
            "label":   "BUDGET BUILD",
            "label_col": ACCENT,
            "price":   "~$889",
            "lines": [
                ("Single Raspberry Pi 5 16GB",         "Sans",  8,  MUTED),
                ("Comms stack only or tactical stack only.", "Sans", 8, MUTED),
                ("Good starting point. Expand later.", "SansItalic", 8, MUTED),
            ],
        },
        {
            "label":   "WHAT YOU SAVE",
            "label_col": AMBER_PRT,
            "price":   None,
            "savings": [
                "Monthly subscription: $0",
                "Platform dependency: none",
                "Data handed to third parties: none",
                "Permission required to operate: none",
            ],
        },
    ]

    for i, cc in enumerate(cost_cards):
        cx = M + i * (card_w + card_gap)
        card(c, cx, card_bot, card_w, card_h)

        # Colored top border line
        c.setStrokeColor(cc["label_col"]); c.setLineWidth(3)
        c.line(cx + 3, card_top - 1, cx + card_w - 3, card_top - 1)

        inner_cx = cx + card_w / 2
        ty = card_top - 16

        # Label
        c.setFont("MonoBold", 8); c.setFillColor(cc["label_col"])
        c.drawCentredString(inner_cx, ty, cc["label"])
        ty -= 20

        if cc.get("price"):
            # Big price
            c.setFont("BigShoulders", 20); c.setFillColor(TEXT)
            c.drawCentredString(inner_cx, ty, cc["price"])
            ty -= 22

            for text, font, size, col in cc.get("lines", []):
                c.setFont(font, size); c.setFillColor(col)
                c.drawCentredString(inner_cx, ty, text)
                ty -= 12
        else:
            # Savings bullets
            bx = cx + 10
            bw = card_w - 20
            for sv in cc.get("savings", []):
                c.setFont("Sans", 8.5); c.setFillColor(TEXT)
                c.drawString(bx + 4, ty, "\u2022")
                c.drawString(bx + 12, ty, sv)
                ty -= 13


# ── Full BOM table ─────────────────────────────────────────────────────────

BOM_ROWS = [
    ("Raspberry Pi 5 16GB",      "2",  "$160 ea",  "Compute nodes (comms + tactical)"),
    ("Pi 5 active cooler",        "2",  "$10 ea",   "Thermal management"),
    ("Samsung 256GB microSD",     "2",  "$28 ea",   "OS + boot media"),
    ("Samsung 2TB NVMe SSD",      "1",  "$120",     "Monero blockchain + data persistence"),
    ("NVMe HAT for Pi 5",         "1",  "$25",      "NVMe interface"),
    ("8U 10\" mini rack",          "1",  "$85",      "Enclosure"),
    ("1U 10\" rack shelf",         "2",  "$18 ea",   "Pi mounting"),
    ("GL.iNet Slate AX router",   "1",  "$80",      "WiFi gateway + LAN"),
    ("TP-Link 8-port switch",     "1",  "$18",      "Managed LAN"),
    ("Heltec LoRa V3",            "2",  "$25 ea",   "LoRa radios (Reticulum + Meshtastic)"),
    ("Tripp Lite BC600R UPS",     "1",  "$55",      "Power continuity"),
    ("Anker 747 GaN 150W",        "1",  "$50",      "Multi-port charging"),
    ("Tupavco 8-outlet PDU",      "1",  "$30",      "Rack power distribution"),
    ("7\" touchscreen",            "1",  "$75",      "Kiosk display"),
    ("Cables, hardware, misc",    "\u2014", "~$50",  "USB, Ethernet, SMA, etc."),
]
BOM_TOTAL = ("TOTAL", "", "~$1,385", "")

COL_HEADERS = ["Component", "Qty", "Approx. Cost", "Purpose"]
COL_WIDTHS  = [200, 28, 76, 220]  # must sum <= W - 2*M = 540


def draw_bom_table(c):
    table_top  = 568
    table_bot  = 290
    section_header(c, M, table_top + 8, "BILL OF MATERIALS \u2014 RECOMMENDED BUILD")

    row_h     = 13
    header_h  = 16
    col_xs    = [M]
    for w in COL_WIDTHS[:-1]:
        col_xs.append(col_xs[-1] + w)

    # Header row
    c.setFillColor(ACCENT); c.setStrokeColor(CARD_BRD); c.setLineWidth(0)
    c.rect(M, table_top - header_h, sum(COL_WIDTHS), header_h, fill=1, stroke=0)

    c.setFont("MonoBold", 8); c.setFillColor(HexColor("#ffffff"))
    for j, hdr in enumerate(COL_HEADERS):
        c.drawString(col_xs[j] + 4, table_top - header_h + 4, hdr)

    y = table_top - header_h

    for r_idx, row in enumerate(BOM_ROWS):
        bg = CARD_BG if r_idx % 2 == 0 else BG
        c.setFillColor(bg); c.setStrokeColor(CARD_BRD); c.setLineWidth(0)
        c.rect(M, y - row_h, sum(COL_WIDTHS), row_h, fill=1, stroke=0)

        c.setFont("Sans", 7.5); c.setFillColor(TEXT)
        for j, cell in enumerate(row):
            c.drawString(col_xs[j] + 4, y - row_h + 3, cell)

        y -= row_h

    # Total row
    c.setFillColor(ACCENT_LT); c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
    c.rect(M, y - row_h - 1, sum(COL_WIDTHS), row_h + 1, fill=1, stroke=1)

    c.setFont("MonoBold", 8); c.setFillColor(TEXT)
    for j, cell in enumerate(BOM_TOTAL):
        if cell:
            c.drawString(col_xs[j] + 4, y - row_h + 3, cell)

    # Outer border
    c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
    c.rect(M, y - row_h - 1, sum(COL_WIDTHS),
           table_top - (y - row_h - 1), fill=0, stroke=1)

    # Column dividers
    c.setLineWidth(0.3)
    for j in range(1, len(col_xs)):
        c.line(col_xs[j], table_top - header_h,
               col_xs[j], y - row_h - 1)


# ── Timeline + skills strip ────────────────────────────────────────────────

def draw_timeline_skills(c):
    strip_top = 325
    strip_bot = 205
    col_w = (W - 2*M - 8) / 2
    lx = M; rx = M + col_w + 8

    # Left — HOW LONG DOES IT TAKE?
    section_header(c, lx, strip_top, "HOW LONG DOES IT TAKE?")
    ty = strip_top - 14

    timeline = [
        ("Weekend 1",    "Hardware assembly, OS installation, basic networking"),
        ("Weekend 2",    "Docker services, Matrix, ATAK, LoRa configuration"),
        ("Weekend 3",    "Hardening, field test, documentation, field card printing"),
        ("Future events", "< 1 hour deploy time once built and tested"),
    ]

    for label, desc in timeline:
        lw = c.stringWidth(label, "MonoBold", 8.5)
        c.setFont("MonoBold", 8.5); c.setFillColor(TEXT)
        c.drawString(lx, ty, label)
        c.setFont("Sans", 8.5); c.setFillColor(MUTED)
        desc_lines = wrap_lines(c, desc, "Sans", 8.5, col_w - lw - 16)
        c.drawString(lx + lw + 6, ty, desc_lines[0] if desc_lines else "")
        if len(desc_lines) > 1:
            ty -= 11
            for ln in desc_lines[1:]:
                c.drawString(lx + lw + 6, ty, ln); ty -= 11
        ty -= 13

    # Right — WHAT SKILLS DO YOU NEED?
    section_header(c, rx, strip_top, "WHAT SKILLS DO YOU NEED?")
    ry = strip_top - 14

    checklist = [
        "Linux command line (SSH, apt, systemctl)",
        "Basic networking (IP addresses, ports, DNS)",
        "Patience and a build guide",
    ]

    max_w = col_w - 4
    for item in checklist:
        # Green checkmark prefix
        c.setFont("MonoBold", 9); c.setFillColor(GREEN_PRT)
        c.drawString(rx + 2, ry, "\u2713")
        c.setFont("Sans", 9); c.setFillColor(TEXT)
        lines = wrap_lines(c, item, "Sans", 9, max_w - 14)
        for k, ln in enumerate(lines):
            ix = rx + 14 if k == 0 else rx + 18
            c.drawString(ix, ry - k * 12, ln)
        ry -= len(lines) * 12 + 2

    ry -= 4
    c.setFont("SansBold", 10); c.setFillColor(ACCENT)
    c.drawString(rx, ry, "The rest is documented.")
    ry -= 13

    c.setFont("Sans", 9); c.setFillColor(MUTED)
    c.drawString(rx, ry, "13 phases. Every command included.")


# ── CTA footer card ────────────────────────────────────────────────────────

def draw_cta(c):
    cta_y = 105; cta_h = 96
    # ACCENT_LT background
    c.setFillColor(ACCENT_LT); c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
    c.roundRect(M, cta_y, W - 2*M, cta_h, 3, fill=1, stroke=1)

    left_w  = (W - 2*M) * 0.64
    right_w = 82
    right_x = W - M - right_w - 8
    lx = M + 12
    ty = cta_y + cta_h - 38   # top padding inside card

    c.setFont("BigShoulders", 20); c.setFillColor(ACCENT)
    c.drawString(lx, ty, "Start building.")
    ty -= 18

    c.setFont("Sans", 9); c.setFillColor(TEXT)
    c.drawString(lx, ty,
        "Full build guide, BOM with Amazon links, and all config files:")
    ty -= 13

    c.setFont("MonoBold", 9); c.setFillColor(ACCENT)
    c.drawString(lx, ty, "github.com/PapaSierra555/M2-Community-Node")
    ty -= 13

    c.setFont("Sans", 8); c.setFillColor(MUTED)
    c.drawString(lx, ty,
        "Scan QR \u2192 open project, clone repo, or read docs online.")

    # QR code — top-anchored with caption below
    qr_size = 60
    qr_url  = "https://github.com/PapaSierra555/M2-Community-Node"
    qr_x    = right_x + (right_w - qr_size) / 2
    qr_y    = cta_y + (cta_h - qr_size) / 2 + 6   # vertically centered, nudged up
    c.drawImage(qr_image(qr_url, qr_size), qr_x, qr_y, qr_size, qr_size)
    c.setFont("Sans", 6.5); c.setFillColor(MUTED)
    c.drawCentredString(right_x + right_w / 2, qr_y - 9, "Scan to open")


# ── Main ───────────────────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)

    header_band(c,
        "BUILD YOUR OWN M2 NODE",
        "What it costs. What it takes. What you get.")

    draw_cost_cards(c)
    draw_bom_table(c)
    draw_timeline_skills(c)
    draw_cta(c)
    footer(c)

    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
