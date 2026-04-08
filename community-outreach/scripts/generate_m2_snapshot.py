"""
M2 Community Node — Snapshot (2-page front/back booth handout)
LFHI outreach marketing package
Output: ../pdf/M2_Snapshot.pdf

Page 1 (Front): Hook, photo, stats, service grid
Page 2 (Back):  Cost, timeline, skills, QR codes, photos
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
_assets_dir = os.path.join(_script_dir, "..", "assets")
OUTPUT = os.path.join(os.path.dirname(_script_dir), "pdf", "M2_Snapshot.pdf")

def _asset(name):
    p = os.path.join(_assets_dir, name)
    return p if os.path.exists(p) else None

PHOTO_PATH = _asset("node-photo.jpg")
CCC_PHOTO  = _asset("node-ccc.jpg")
SIDE_PHOTO = _asset("node-side.jpg")


# ── Helpers ────────────────────────────────────────────────────────────────

def rule(c, x, y, w, col=None, lw=0.5):
    c.setStrokeColor(col or RULE); c.setLineWidth(lw)
    c.line(x, y, x + w, y)

def card(c, x, y, w, h, r=3):
    c.setFillColor(CARD_BG); c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)

def section_header(c, x, y, text):
    """Prominent section header — JuraMed 11pt with accent rule."""
    c.setFont("JuraMed", 11); c.setFillColor(ACCENT)
    c.drawString(x, y, text.upper())
    rule(c, x, y - 4, W - 2 * M, col=RULE, lw=0.5)

def wrap_lines(c, text, font, size, max_w):
    words = text.split(); lines = []; line = []
    for w in words:
        test = " ".join(line + [w])
        if c.stringWidth(test, font, size) <= max_w:
            line.append(w)
        else:
            lines.append(" ".join(line)); line = [w]
    if line: lines.append(" ".join(line))
    return lines

def qr_image(url):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    from reportlab.lib.utils import ImageReader
    return ImageReader(buf)

def footer(c):
    rule(c, M, 52, W - 2 * M)
    c.setFont("Sans", 7); c.setFillColor(MUTED)
    c.drawString(M, 40,
        "License: CC BY-NC-SA 4.0 \u2014 Build one for your community. Cannot be sold.")
    c.drawRightString(W - M, 40, "Capable Enough Project")

def header_band(c, title, subtitle):
    c.setFillColor(ACCENT)
    c.rect(0, H - 62, W, 62, fill=1, stroke=0)
    c.setFont("BigShoulders", 26); c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, H - 36, title)
    c.setFont("Sans", 10); c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, H - 52, subtitle)
    logo_path = os.path.join(_assets_dir, "lfhi-logo.png")
    badge_w = 86; badge_h = 46
    badge_x = W - M - badge_w - 4; badge_y = H - 56
    c.setFillColor(HexColor("#111111")); c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(0.5)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 3, fill=1, stroke=1)
    c.setFont("BigShoulders", 13); c.setFillColor(HexColor("#c92a2a"))
    c.drawString(badge_x + 6, badge_y + 24, "CCC26")
    c.setFont("MonoBold", 9); c.setFillColor(HexColor("#ffffff"))
    c.drawString(badge_x + 6, badge_y + 10, "LFHI")
    c.setStrokeColor(HexColor("#444444")); c.setLineWidth(0.5)
    c.line(badge_x + 40, badge_y + 7, badge_x + 40, badge_y + 39)
    if os.path.exists(logo_path):
        c.drawImage(logo_path, badge_x + 44, badge_y + 5,
                    36, 36, preserveAspectRatio=True)


# ── Page 1 ─────────────────────────────────────────────────────────────────

def page_one(c):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c,
        "M2 COMMUNITY NODE",
        "Field-deployable communications infrastructure \u2014 no internet required.")

    hook_y = H - 88
    c.setFont("BigShoulders", 15); c.setFillColor(TEXT)
    c.drawString(M, hook_y,
        "When the network goes down, yours doesn't.")
    rule(c, M, hook_y - 6, W - 2 * M, col=ACCENT, lw=1.5)

    # ── Photo slot (portrait, centered) ────────────────────────────────────
    photo_w   = 252
    photo_h   = 326
    photo_x   = (W - photo_w) / 2
    photo_top = hook_y - 14
    photo_bot = photo_top - photo_h

    if PHOTO_PATH:
        c.setFillColor(HexColor("#111111")); c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(1)
        c.roundRect(photo_x - 3, photo_bot - 3, photo_w + 6, photo_h + 6,
                    3, fill=1, stroke=1)
        c.drawImage(PHOTO_PATH, photo_x, photo_bot, photo_w, photo_h,
                    preserveAspectRatio=True, anchor="c")
    else:
        c.setFillColor(HexColor("#f0eded")); c.setStrokeColor(CARD_BRD)
        c.setLineWidth(1)
        c.roundRect(photo_x, photo_bot, photo_w, photo_h, 4, fill=1, stroke=1)
        c.setFont("BigShoulders", 14); c.setFillColor(HexColor("#bbaaaa"))
        c.drawCentredString(W / 2, photo_bot + photo_h / 2 + 8, "[ INSERT NODE PHOTO ]")
        c.setFont("Sans", 9); c.setFillColor(HexColor("#bbaaaa"))
        c.drawCentredString(W / 2, photo_bot + photo_h / 2 - 10,
            "Drop node-photo.jpg into outreach/assets/ and regenerate")

    cap_y = photo_bot - 12
    c.setFont("Mono", 7.5); c.setFillColor(MUTED)
    c.drawCentredString(W / 2, cap_y,
        "8U 10\u201d mini-rack \u2014 Dual Raspberry Pi 5 16GB \u2014 Deploys in 15 minutes")

    # ── Stat pills ──────────────────────────────────────────────────────────
    stats = [("~$1,385","full build"), ("8","services"), ("3","weekends"), ("$0","per month")]
    pill_y = cap_y - 18; pill_h = 44; pill_gap = 8
    pill_w = (W - 2 * M - 3 * pill_gap) / 4

    for i, (big, small) in enumerate(stats):
        px = M + i * (pill_w + pill_gap)
        c.setFillColor(CARD_BG); c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
        c.roundRect(px, pill_y - pill_h, pill_w, pill_h, 3, fill=1, stroke=1)
        c.setStrokeColor(ACCENT); c.setLineWidth(2)
        c.line(px + 4, pill_y - 1, px + pill_w - 4, pill_y - 1)
        cx = px + pill_w / 2
        c.setFont("BigShoulders", 18); c.setFillColor(ACCENT)
        c.drawCentredString(cx, pill_y - 22, big)
        c.setFont("Sans", 7.5); c.setFillColor(MUTED)
        c.drawCentredString(cx, pill_y - 34, small)

    # ── Service grid ────────────────────────────────────────────────────────
    grid_top = pill_y - pill_h - 14
    section_header(c, M, grid_top, "What's running on the node")

    services = [
        ("Matrix / Element",  "Encrypted group chat \u2014 works on Tor + LAN"),
        ("OpenTAK / iTAK",    "Tactical mapping and situational awareness"),
        ("Meshtastic LoRa",   "Off-grid mesh radio, no infrastructure needed"),
        ("Mumble",            "Low-latency encrypted voice comms"),
        ("Tor + I2P",         "Anonymous routing, .onion services"),
        ("Headscale VPN",     "Peer-to-peer mesh VPN, no cloud"),
        ("Reticulum / RNode", "Multi-transport mesh backbone"),
        ("Monero Node",       "Local privacy-preserving transaction relay"),
    ]
    col_w = (W - 2 * M - 12) / 2
    grid_y = grid_top - 12; row_h = 22

    for i, (name, desc) in enumerate(services):
        col = i % 2; row = i // 2
        sx = M + col * (col_w + 12)
        sy = grid_y - row * row_h
        if (i // 2) % 2 == 0:
            c.setFillColor(HexColor("#faf6f6"))
            c.rect(sx, sy - row_h + 5, col_w, row_h - 2, fill=1, stroke=0)
        c.setFont("SansBold", 8.5); c.setFillColor(TEXT)
        c.drawString(sx + 4, sy - 3, name)
        c.setFont("Sans", 7.5); c.setFillColor(MUTED)
        c.drawString(sx + 4, sy - 13, desc)

    footer(c)


# ── Page 2 ─────────────────────────────────────────────────────────────────

def page_two(c):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header
    c.setFillColor(ACCENT); c.rect(0, H - 40, W, 40, fill=1, stroke=0)
    c.setFont("BigShoulders", 18); c.setFillColor(HexColor("#ffffff"))
    c.drawString(M + 8, H - 26, "M2 COMMUNITY NODE \u2014 BUILD INFO")
    logo_path = os.path.join(_assets_dir, "lfhi-logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, W - M - 28, H - 36, 24, 24, preserveAspectRatio=True)

    y = H - 68  # top of content — 28pt padding below header

    # ── WHAT DOES IT COST? ──────────────────────────────────────────────────
    section_header(c, M, y, "What does it cost?")
    y -= 18

    card_h = 100; card_gap = 10
    card_w = (W - 2 * M - card_gap) / 2

    cost_cards = [
        {"label": "RECOMMENDED BUILD", "col": GREEN_PRT, "price": "~$1,385",
         "lines": ["Dual Raspberry Pi 5 16GB", "Full comms + tactical stack",
                   "Best for active chapters", "and regular deployments"]},
        {"label": "BUDGET BUILD",      "col": ACCENT,    "price": "~$889",
         "lines": ["Single Raspberry Pi 5 16GB", "Comms or tactical stack",
                   "Great starting point \u2014", "expand hardware later"]},
    ]
    for i, cc in enumerate(cost_cards):
        cx = M + i * (card_w + card_gap)
        card(c, cx, y - card_h, card_w, card_h)
        c.setStrokeColor(cc["col"]); c.setLineWidth(3)
        c.line(cx + 3, y - 1, cx + card_w - 3, y - 1)
        mid = cx + card_w / 2; ty = y - 18
        c.setFont("MonoBold", 8); c.setFillColor(cc["col"])
        c.drawCentredString(mid, ty, cc["label"]); ty -= 20
        c.setFont("BigShoulders", 20); c.setFillColor(TEXT)
        c.drawCentredString(mid, ty, cc["price"]); ty -= 14
        for ln in cc["lines"]:
            c.setFont("Sans", 8); c.setFillColor(MUTED)
            c.drawCentredString(mid, ty, ln); ty -= 11

    y -= card_h + 10

    # Zero-cost callout — draw checkmark in MonoBold (has the glyph), text in SansBold
    c.setFont("MonoBold", 9); c.setFillColor(GREEN_PRT)
    c.drawString(M, y, "\u2713")
    c.setFont("SansBold", 8.5); c.setFillColor(GREEN_PRT)
    c.drawString(M + 13, y, "$0 / month.  No subscriptions. No cloud. No third-party data.")
    y -= 22

    # ── HOW LONG DOES IT TAKE? ──────────────────────────────────────────────
    section_header(c, M, y, "How long does it take?")
    y -= 18

    timeline = [
        ("Weekend 1",     "Hardware assembly, OS install, basic networking"),
        ("Weekend 2",     "Docker services, Matrix, ATAK, LoRa config"),
        ("Weekend 3",     "Hardening, field test, print field cards"),
        ("Future events", "< 1 hour deploy time once built"),
    ]
    for label, desc in timeline:
        lw2 = c.stringWidth(label, "MonoBold", 8.5)
        c.setFont("MonoBold", 8.5); c.setFillColor(TEXT)
        c.drawString(M, y, label)
        c.setFont("Sans", 8.5); c.setFillColor(MUTED)
        c.drawString(M + lw2 + 8, y, desc)
        y -= 14
    y -= 8

    # ── WHAT SKILLS DO YOU NEED? ────────────────────────────────────────────
    section_header(c, M, y, "What skills do you need?")
    y -= 18

    skills = [
        "Linux command line (SSH, apt, systemctl)",
        "Basic networking (IP addresses, ports, DNS)",
        "Patience \u2014 the rest is documented",
    ]
    for sk in skills:
        c.setFont("MonoBold", 9); c.setFillColor(GREEN_PRT)
        c.drawString(M + 2, y, "\u2713")
        c.setFont("Sans", 9); c.setFillColor(TEXT)
        c.drawString(M + 14, y, sk)
        y -= 14
    c.setFont("SansBold", 10); c.setFillColor(ACCENT)
    c.drawString(M + 14, y, "13 phases. Every command included.")
    y -= 24

    # ── QR codes — single containing card ──────────────────────────────────
    qr_size  = 70
    qr_card_h = qr_size + 52  # room for QR + two lines of text + padding
    card(c, M, y - qr_card_h, W - 2 * M, qr_card_h)

    qrs = [
        (
            "https://github.com/PapaSierra555/M2-Community-Node",
            "github.com/PapaSierra555/M2-Community-Node",
            "Full project \u2014 build guide, BOM, config files",
        ),
        (
            "https://github.com/PapaSierra555/M2-Community-Node/releases",
            "github.com/PapaSierra555/M2-Community-Node/releases",
            "Download build guide PDF \u2014 13 phases, every command",
        ),
    ]

    col_w_qr = (W - 2 * M) / 2
    for i, (url, label, desc) in enumerate(qrs):
        qx_center = M + col_w_qr * i + col_w_qr / 2
        qx = qx_center - qr_size / 2
        qy = y - 6 - qr_size
        c.drawImage(qr_image(url), qx, qy, qr_size, qr_size)
        # Label — MonoBold 7pt, clipped to column width
        c.setFont("MonoBold", 7); c.setFillColor(ACCENT)
        max_w = col_w_qr - 12
        lines = wrap_lines(c, label, "MonoBold", 7, max_w)
        ty = qy - 11
        for ln in lines:
            c.drawCentredString(qx_center, ty, ln); ty -= 10
        # Desc — Sans 6.5pt
        c.setFont("Sans", 6.5); c.setFillColor(MUTED)
        dlines = wrap_lines(c, desc, "Sans", 6.5, max_w)
        for ln in dlines:
            c.drawCentredString(qx_center, ty, ln); ty -= 9

        # Vertical divider between QRs
        if i == 0:
            c.setStrokeColor(CARD_BRD); c.setLineWidth(0.5)
            c.line(M + col_w_qr, y - 4, M + col_w_qr, y - qr_card_h + 4)

    y -= qr_card_h + 12

    # ── Bottom photos ───────────────────────────────────────────────────────
    photos = [(p, cap) for p, cap in [
        (CCC_PHOTO,  "Front panel \u2014 kiosk service status display"),
        (SIDE_PHOTO, "Side panel \u2014 QR onboarding codes"),
    ] if p]

    if photos:
        ph_h    = 110
        ph_gap  = 8
        ph_w    = (W - 2 * M - (len(photos) - 1) * ph_gap) / len(photos)

        for i, (path, cap) in enumerate(photos):
            px = M + i * (ph_w + ph_gap)
            c.setFillColor(HexColor("#111111")); c.setStrokeColor(HexColor("#222222"))
            c.setLineWidth(0.5)
            c.roundRect(px, y - ph_h, ph_w, ph_h, 2, fill=1, stroke=1)
            c.drawImage(path, px + 2, y - ph_h + 14, ph_w - 4, ph_h - 18,
                        preserveAspectRatio=True, anchor="c")
            c.setFont("Sans", 6.5); c.setFillColor(HexColor("#aaaaaa"))
            c.drawCentredString(px + ph_w / 2, y - ph_h + 5, cap)

    footer(c)


# ── Main ───────────────────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)
    page_one(c)
    c.showPage()
    page_two(c)
    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
