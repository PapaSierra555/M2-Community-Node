"""
M2 Community Node — PACE Communications Plan Card
LFHI outreach reference sheet
Output: ../pdf/M2_PACE_Card.pdf
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

W, H = letter   # 612 x 792
M = 36

_script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(_script_dir, "..", "pdf", "M2_PACE_Card.pdf")


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


# ── Status pill ────────────────────────────────────────────────────────────

def status_pill(c, x, y, text, bg_color, w=None):
    """Draw a filled rounded-rect status pill. Returns pill width."""
    c.setFont("MonoBold", 7)
    tw = c.stringWidth(text, "MonoBold", 7)
    pw = w or (tw + 12)
    ph = 13
    c.setFillColor(bg_color)
    c.setStrokeColor(bg_color)
    c.setLineWidth(0)
    c.roundRect(x, y, pw, ph, 3, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.drawString(x + (pw - tw) / 2, y + 3, text)
    return pw


# ── Technology block helper ────────────────────────────────────────────────

def tech_block(c, x, y, name, desc, max_w):
    """
    Draw a technology entry: MonoBold name on top, Sans italic desc below.
    Returns the y position after the block.
    """
    c.setFont("MonoBold", 9)
    c.setFillColor(ACCENT)
    name_lines = wrap_lines(c, name, "MonoBold", 9, max_w)
    for ln in name_lines:
        c.drawString(x, y, ln)
        y -= 11

    c.setFont("Sans", 8)
    c.setFillColor(MUTED)
    desc_lines = wrap_lines(c, desc, "Sans", 8, max_w)
    for ln in desc_lines:
        c.drawString(x + 4, y, ln)
        y -= 10

    return y - 2


# ── PACE row ───────────────────────────────────────────────────────────────

def pace_row(c, row_x, row_y, row_w, row_h,
             letter_ch, tier_name, tier_sub,
             tech_entries, range_main, range_sub,
             pill_text, stripe_color):
    """
    Draw one PACE tier row.
    tech_entries: list of (name, desc) tuples
    """
    # Card background
    card(c, row_x, row_y, row_w, row_h)

    # Left accent stripe
    stripe_w = 10
    c.setFillColor(stripe_color)
    c.setStrokeColor(stripe_color)
    c.roundRect(row_x, row_y, stripe_w, row_h, 3, fill=1, stroke=0)
    # Square off the right side of the stripe
    c.rect(row_x + stripe_w - 3, row_y, 3, row_h, fill=1, stroke=0)

    content_x = row_x + stripe_w + 10
    center_y  = row_y + row_h / 2

    # Column widths (relative to content area)
    content_w  = row_w - stripe_w - 10 - 10  # 10 right margin
    letter_col = 36
    name_col   = 110
    tech_col   = content_w - letter_col - name_col - 90 - 10  # leave 90 for range, 10 gap
    range_col  = 90

    # ── Tier letter ──
    letter_x = content_x
    c.setFont("BigShoulders", 36)
    c.setFillColor(stripe_color)
    lh = 36 * 0.72
    c.drawString(letter_x, center_y - lh / 2, letter_ch)

    # ── Tier name block ──
    name_x = content_x + letter_col
    name_y = center_y + 8
    c.setFont("MonoBold", 11)
    c.setFillColor(TEXT)
    c.drawString(name_x, name_y, tier_name)
    c.setFont("Sans", 9)
    c.setFillColor(MUTED)
    c.drawString(name_x, name_y - 13, tier_sub)

    # ── Technology entries ──
    tech_x = content_x + letter_col + name_col
    tech_y = row_y + row_h - 16

    for t_name, t_desc in tech_entries:
        c.setFont("MonoBold", 9)
        c.setFillColor(ACCENT)
        t_lines = wrap_lines(c, t_name, "MonoBold", 9, tech_col)
        for ln in t_lines:
            c.drawString(tech_x, tech_y, ln)
            tech_y -= 11
        c.setFont("Sans", 8)
        c.setFillColor(MUTED)
        d_lines = wrap_lines(c, t_desc, "Sans", 8, tech_col)
        for ln in d_lines:
            c.drawString(tech_x + 2, tech_y, ln)
            tech_y -= 10
        tech_y -= 3

    # ── Range / Requirement ──
    range_x = tech_x + tech_col + 8
    range_y = center_y + 8
    c.setFont("MonoBold", 9)
    c.setFillColor(TEXT)
    c.drawString(range_x, range_y, range_main)
    c.setFont("Sans", 8)
    c.setFillColor(MUTED)
    for ln in wrap_lines(c, range_sub, "Sans", 8, range_col):
        range_y -= 12
        c.drawString(range_x, range_y, ln)

    # ── Status pill — bottom right of row ──
    pill_x = row_x + row_w - 110
    pill_y = row_y + 8
    status_pill(c, pill_x, pill_y, pill_text, stripe_color, w=100)


# ── Main ───────────────────────────────────────────────────────────────────

def build():
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Header band (y=730–792) ─────────────────────────────────────────────
    c.setFillColor(ACCENT)
    c.rect(0, 730, W, 62, fill=1, stroke=0)

    c.setFont("BigShoulders", 26)
    c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, 758, "PACE COMMUNICATIONS PLAN")

    c.setFont("Sans", 10)
    c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, 742,
        "M2 Community Node \u2014 Build it. Own it. Control it.")

    # CCC26 × LFHI badge — top right of header
    logo_path = os.path.join(_script_dir, "..", "assets", "lfhi-logo.png")
    badge_w = 86; badge_h = 46
    badge_x = W - M - badge_w - 4; badge_y = 736
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

    # ── Intro paragraph (y=700–725) ─────────────────────────────────────────
    intro = (
        "A PACE plan defines four tiers of communication, ordered from most capable "
        "to most resilient. The M2 Community Node provides all four tiers in a single "
        "deployable rack. Each tier operates independently \u2014 losing one does not "
        "affect the others below it."
    )
    c.setFont("Sans", 10)
    c.setFillColor(TEXT)
    iy = 710
    for ln in wrap_lines(c, intro, "Sans", 10, W - 2 * M):
        c.drawString(M, iy, ln)
        iy -= 14

    # ── PACE rows ────────────────────────────────────────────────────────────
    table_top = 655
    table_bot = 200
    table_h   = table_top - table_bot
    row_gap   = 6
    row_h     = (table_h - 3 * row_gap) / 4   # ~118pt each
    row_w     = W - 2 * M

    pace_rows = [
        {
            "letter_ch":   "P",
            "tier_name":   "PRIMARY",
            "tier_sub":    "Local WiFi Network",
            "tech_entries": [
                ("Matrix / Element",
                 "Encrypted group chat, E2E, self-hosted"),
                ("OpenTAK Server",
                 "Shared tactical map, CoT, GeoChat, voice"),
                ("AdGuard DNS",
                 "Local DNS resolution, ad blocking"),
            ],
            "range_main":  "~300m WiFi range",
            "range_sub":   "Node powered on",
            "pill_text":   "FULL CAPABILITY",
            "stripe_color": GREEN_PRT,
        },
        {
            "letter_ch":   "A",
            "tier_name":   "ALTERNATE",
            "tier_sub":    "Clearnet Tunnel",
            "tech_entries": [
                ("Cloudflare Tunnel",
                 "Zero-trust encrypted tunnel, no open ports"),
                ("communitynode.yourdomain.com",
                 "Element Web accessible worldwide"),
                ("Headscale VPN",
                 "Remote operator access, encrypted"),
            ],
            "range_main":  "Worldwide",
            "range_sub":   "Internet connection required",
            "pill_text":   "INTERNET REQUIRED",
            "stripe_color": HexColor("#c49a00"),
        },
        {
            "letter_ch":   "C",
            "tier_name":   "CONTINGENCY",
            "tier_sub":    "Anonymous Routing",
            "tech_entries": [
                ("Tor Hidden Services",
                 "Three .onion addresses, censorship-resistant"),
                ("I2P / i2pd",
                 "Distributed anonymous network, eepsite"),
                ("No DNS dependency",
                 "Works when DNS is blocked or compromised"),
            ],
            "range_main":  "Worldwide",
            "range_sub":   "Internet + Tor Browser or I2P router",
            "pill_text":   "CENSORSHIP RESISTANT",
            "stripe_color": HexColor("#c06010"),
        },
        {
            "letter_ch":   "E",
            "tier_name":   "EMERGENCY",
            "tier_sub":    "Radio \u2014 No Infrastructure",
            "tech_entries": [
                ("Meshtastic / LoRa",
                 "1\u20135 km range, encrypted, no internet, no WiFi"),
                ("Reticulum / RNode",
                 "Encrypted mesh backbone, LoRa + TCP transport"),
                ("Heltec V3 LoRa",
                 "LEFT=RNode/Reticulum  RIGHT=Meshtastic"),
            ],
            "range_main":  "1\u20135 km per hop",
            "range_sub":   "No internet. No WiFi. No infrastructure.",
            "pill_text":   "NO INFRASTRUCTURE",
            "stripe_color": RED_PRT,
        },
    ]

    ry = table_top
    for i, row in enumerate(pace_rows):
        ry -= row_h
        pace_row(
            c, M, ry, row_w, row_h - 2,
            row["letter_ch"],
            row["tier_name"],
            row["tier_sub"],
            row["tech_entries"],
            row["range_main"],
            row["range_sub"],
            row["pill_text"],
            row["stripe_color"],
        )
        ry -= row_gap

    # ── Footer notes (y=140–195) ─────────────────────────────────────────────
    notes_top = 170
    section_header(c, M, notes_top, "DEPLOYMENT NOTES")

    note_texts = [
        ("Each tier is independent \u2014 failure of a higher tier does not affect"
         " lower tiers."),
        ("Meshtastic and Reticulum operate from the node's onboard LoRa radios"
         " \u2014 no external hardware needed by operators."),
        ("This PACE plan covers the node's output. Operators still need client"
         " devices (phone, laptop, ATAK-compatible)."),
    ]

    ncol_gap = 8
    ncol_w   = (W - 2 * M - 2 * ncol_gap) / 3
    nx = M

    for note in note_texts:
        # Draw a subtle pill background
        note_lines = wrap_lines(c, note, "Sans", 7.5, ncol_w - 12)
        pill_h = len(note_lines) * 11 + 10
        pill_y = notes_top - 14 - pill_h

        c.setFillColor(CARD_BG)
        c.setStrokeColor(CARD_BRD)
        c.setLineWidth(0.5)
        c.roundRect(nx, pill_y, ncol_w, pill_h, 3, fill=1, stroke=1)

        ty = pill_y + pill_h - 13
        c.setFont("Sans", 7.5)
        c.setFillColor(MUTED)
        for ln in note_lines:
            c.drawString(nx + 6, ty, ln)
            ty -= 11

        nx += ncol_w + ncol_gap

    # ── Footer ───────────────────────────────────────────────────────────────
    rule(c, M, 52, W - 2 * M)

    c.setFont("Sans", 7)
    c.setFillColor(MUTED)
    c.drawString(M, 40,
        "License: CC BY-NC-SA 4.0 \u2014 Build one for your community. Cannot be sold.")
    c.drawRightString(W - M, 40, "Capable Enough Project")

    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
