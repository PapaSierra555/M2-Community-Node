"""
M2 Community Node — New Member Onboarding Card
LFHI outreach — laminated 3.5x5.5 handout
Output: ../pdf/M2_New_Member_Card.pdf
"""
import os
import io
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import qrcode

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
WHITE     = HexColor("#ffffff")

pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{FONTS}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoBold",     f"{FONTS}/IBMPlexMono-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Jura",         f"{FONTS}/Jura-Medium.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))

# Card dimensions: 3.5 x 5.5 inches
W, H = 252, 396
M = 12  # margin

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pdf", "M2_New_Member_Card.pdf"
)


# ── Helpers ────────────────────────────────────────────────────────────────

def rule(c, x, y, w, col=None, lw=0.4):
    c.setStrokeColor(col or RULE)
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)

def card_rect(c, x, y, w, h, r=3):
    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1)

def section_header(c, x, y, text):
    """Prominent section header — JuraMed 9pt with rule (card proportions)."""
    c.setFont("JuraMed", 9); c.setFillColor(ACCENT)
    c.drawString(x, y, text.upper())
    c.setStrokeColor(RULE); c.setLineWidth(0.4)
    c.line(x, y - 3, W - M, y - 3)

def wrap_lines(c, text, font, size, max_w):
    words = text.split()
    lines, line = [], []
    for w in words:
        test = " ".join(line + [w])
        if c.stringWidth(test, font, size) <= max_w:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    return lines

def qr_image(url):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)

def dot(c, x, y, r, color):
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.circle(x, y, r, fill=1, stroke=0)

def header_band(c, title, band_h=40):
    """Draw ACCENT header band at top of card with CCC26×LFHI badge."""
    c.setFillColor(ACCENT)
    c.rect(0, H - band_h, W, band_h, fill=1, stroke=0)
    c.setFont("BigShoulders", 12)
    c.setFillColor(WHITE)
    c.drawString(M, H - band_h + 15, title)
    # CCC26 × LFHI badge
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "assets", "lfhi-logo.png")
    badge_w = 56; badge_h = 32
    badge_x = W - 4 - badge_w; badge_y = H - band_h + 4
    c.setFillColor(HexColor("#111111"))
    c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(0.5)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 2, fill=1, stroke=1)
    c.setFont("BigShoulders", 8)
    c.setFillColor(HexColor("#c92a2a"))
    c.drawString(badge_x + 3, badge_y + 18, "CCC26")
    c.setFont("MonoBold", 7)
    c.setFillColor(WHITE)
    c.drawString(badge_x + 3, badge_y + 7, "LFHI")
    c.setStrokeColor(HexColor("#444444"))
    c.setLineWidth(0.5)
    c.line(badge_x + 28, badge_y + 4, badge_x + 28, badge_y + 28)
    if os.path.exists(logo_path):
        c.drawImage(logo_path, badge_x + 31, badge_y + 6,
                    20, 20, preserveAspectRatio=True)


# ── Side 1 — Get Connected ─────────────────────────────────────────────────

def side_one(c):
    # Background
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header band
    header_band(c, "M2 COMMUNITY NODE")

    # Subhead
    y = H - 54
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    sub = "Get Connected Now"
    sw = c.stringWidth(sub, "SansBold", 9)
    c.drawString((W - sw) / 2, y, sub)

    y -= 14

    # ── WiFi section ───────────────────────────────────────────────────────
    wifi_h = 52
    wifi_y = y - wifi_h
    card_rect(c, M, wifi_y, W - 2 * M, wifi_h)

    # WiFi label
    section_header(c, M + 6, wifi_y + wifi_h - 10, "WiFi")

    # WiFi icon placeholder (small antenna symbol using lines)
    icon_x = W - M - 14
    icon_y = wifi_y + wifi_h - 11
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.2)
    c.arc(icon_x - 6, icon_y - 2, icon_x + 6, icon_y + 10, 0, 180)
    c.setLineWidth(0.8)
    c.arc(icon_x - 4, icon_y, icon_x + 4, icon_y + 7, 0, 180)
    c.setFillColor(ACCENT)
    c.circle(icon_x, icon_y + 2, 1.5, fill=1, stroke=0)

    # Network name row
    row_y = wifi_y + wifi_h - 26
    c.setFont("Mono", 7)
    c.setFillColor(MUTED)
    c.drawString(M + 6, row_y, "NETWORK")
    c.setFont("MonoBold", 9)
    c.setFillColor(TEXT)
    c.drawString(M + 52, row_y, "CommunityNode")

    # Password row
    row_y -= 14
    c.setFont("Mono", 7)
    c.setFillColor(MUTED)
    c.drawString(M + 6, row_y, "PASSWORD")
    c.setFont("MonoBold", 9)
    c.setFillColor(TEXT)
    c.drawString(M + 52, row_y, "CapableEnough26")

    y = wifi_y - 10

    # ── Connection methods ─────────────────────────────────────────────────
    section_header(c, M, y, "Connection Methods")

    y -= 6

    methods = [
        ("Matrix Chat",   "communitynode.yourdomain.com", GREEN_PRT),
        ("ATAK / TAK",    "tak.yourdomain.com:8089",      AMBER_PRT),
        ("Mesh Radio",    "Meshtastic  \u2022  CommunityNode", ACCENT),
    ]

    row_h = 30
    for svc, addr, color in methods:
        y -= row_h
        card_rect(c, M, y, W - 2 * M, row_h - 3)

        # Colored left stripe
        c.setFillColor(color)
        c.setStrokeColor(color)
        c.roundRect(M, y, 6, row_h - 3, 2, fill=1, stroke=0)
        c.rect(M + 3, y, 3, row_h - 3, fill=1, stroke=0)

        # Status dot
        dot(c, M + 16, y + (row_h - 3) / 2, 3, color)

        # Service name
        tx = M + 24
        c.setFont("SansBold", 8)
        c.setFillColor(TEXT)
        c.drawString(tx, y + (row_h - 3) / 2 + 3, svc)

        # Address
        c.setFont("Mono", 6.5)
        c.setFillColor(MUTED)
        c.drawString(tx, y + (row_h - 3) / 2 - 7, addr)

    y -= 18

    # ── QR code (WiFi) ─────────────────────────────────────────────────────
    wifi_qr_data = "WIFI:T:WPA;S:CommunityNode;P:CapableEnough26;;"
    qr_size = 54
    qr_x = (W - qr_size) / 2
    # "WIFI" label above QR
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    wl_w = c.stringWidth("WIFI", "SansBold", 9)
    c.drawString((W - wl_w) / 2, y, "WIFI")
    qr_y = y - 14 - qr_size
    c.drawImage(qr_image(wifi_qr_data), qr_x, qr_y, qr_size, qr_size)
    c.setFont("Mono", 6)
    c.setFillColor(MUTED)
    cap = "Scan to join WiFi"
    cw = c.stringWidth(cap, "Mono", 6)
    c.drawString((W - cw) / 2, qr_y - 8, cap)
    # Network / password address line
    c.setFont("Mono", 6.5)
    c.setFillColor(TEXT)
    addr = "CommunityNode  \u2022  CapableEnough26"
    aw = c.stringWidth(addr, "Mono", 6.5)
    c.drawString((W - aw) / 2, qr_y - 18, addr)
    y = qr_y - 30

    # ── Footer ─────────────────────────────────────────────────────────────
    rule(c, M, y + 8, W - 2 * M)
    c.setFont("Sans", 5.5)
    c.setFillColor(MUTED)
    foot = "Powered by CC BY-NC-SA 4.0 open source hardware & software"
    fw = c.stringWidth(foot, "Sans", 5.5)
    c.drawString((W - fw) / 2, y - 2, foot)


# ── Side 2 — Quick Reference ───────────────────────────────────────────────

def side_two(c):
    c.showPage()

    # Background
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header band
    header_band(c, "QUICK REFERENCE")

    y = H - 52

    # ── PACE tier strip ────────────────────────────────────────────────────
    section_header(c, M, y, "PACE Communications Plan")

    y -= 6

    pace_rows = [
        ("P", "PRIMARY",     "Matrix Chat",            "communitynode.yourdomain.com", GREEN_PRT),
        ("A", "ALTERNATE",   "ATAK / TAK Server",      "tak.yourdomain.com:8089",      HexColor("#c49a00")),
        ("C", "CONTINGENCY", "Mesh Radio / Meshtastic", "Channel: CommunityNode",         HexColor("#c06010")),
        ("E", "EMERGENCY",   "Simplex / Voice Radio",  "Call-out: team freq / in person", RED_PRT),
    ]

    row_h = 32
    content_w = W - 2 * M

    for letter_ch, tier, svc, detail, color in pace_rows:
        y -= row_h
        card_rect(c, M, y, content_w, row_h - 3)

        # Left stripe
        stripe_w = 8
        c.setFillColor(color)
        c.setStrokeColor(color)
        c.roundRect(M, y, stripe_w, row_h - 3, 2, fill=1, stroke=0)
        c.rect(M + stripe_w - 2, y, 2, row_h - 3, fill=1, stroke=0)

        inner_x = M + stripe_w + 4

        # Tier letter
        c.setFont("BigShoulders", 16)
        c.setFillColor(color)
        lh = 16 * 0.72
        c.drawString(inner_x, y + (row_h - 3) / 2 - lh / 2 + 1, letter_ch)

        name_x = inner_x + 14

        # Tier label (small)
        c.setFont("Mono", 5.5)
        c.setFillColor(color)
        c.drawString(name_x, y + 21, tier)

        # Service name
        c.setFont("SansBold", 8)
        c.setFillColor(TEXT)
        c.drawString(name_x, y + 11, svc)

        # Detail / address
        c.setFont("Mono", 6)
        c.setFillColor(MUTED)
        c.drawString(name_x, y + 3, detail)

    y -= 18

    # ── Troubleshoot section ───────────────────────────────────────────────
    section_header(c, M, y, "If Something's Broken")

    y -= 6

    ts_items = [
        ("Can't connect?",   "Join CommunityNode WiFi first"),
        ("Matrix offline?",  "Check communitynode.yourdomain.com"),
        ("Need help?",       "Ask the Node Operator or Support team"),
    ]

    ts_h = len(ts_items) * 14 + 8
    card_rect(c, M, y - ts_h, content_w, ts_h)

    ty = y - 9
    for label, detail in ts_items:
        # Bullet dot
        dot(c, M + 8, ty + 3, 2, ACCENT)

        c.setFont("SansBold", 7.5)
        c.setFillColor(TEXT)
        c.drawString(M + 14, ty, label)

        lw = c.stringWidth(label, "SansBold", 7.5)
        c.setFont("Sans", 7.5)
        c.setFillColor(MUTED)
        c.drawString(M + 14 + lw + 4, ty, detail)

        ty -= 14

    y = y - ts_h - 10

    # ── GitHub QR ─────────────────────────────────────────────────────────
    qr_url = "https://github.com/PapaSierra555/M2-Community-Node"
    qr_size = 46
    qr_x = (W - qr_size) / 2
    # Label above QR
    c.setFont("SansBold", 7.5)
    c.setFillColor(ACCENT)
    qr_lbl = "BUILD GUIDE + FULL DOCS"
    ql_w = c.stringWidth(qr_lbl, "SansBold", 7.5)
    c.drawString((W - ql_w) / 2, y, qr_lbl)
    qr_y = y - 10 - qr_size
    c.drawImage(qr_image(qr_url), qr_x, qr_y, qr_size, qr_size)
    # Context below QR
    c.setFont("Sans", 6)
    c.setFillColor(MUTED)
    ctx = "Bill of materials, configs & step-by-step build guide"
    ctx_w = c.stringWidth(ctx, "Sans", 6)
    c.drawString((W - ctx_w) / 2, qr_y - 8, ctx)
    c.setFont("Mono", 5.5)
    c.setFillColor(ACCENT)
    gh = "github.com/PapaSierra555/M2-Community-Node"
    gw = c.stringWidth(gh, "Mono", 5.5)
    c.drawString((W - gw) / 2, qr_y - 16, gh)

    # ── Footer ─────────────────────────────────────────────────────────────
    rule(c, M, qr_y - 26, content_w)
    c.setFont("Sans", 5)
    c.setFillColor(MUTED)
    foot2 = "CC BY-NC-SA 4.0 \u2014 Capable Enough Project"
    fw2 = c.stringWidth(foot2, "Sans", 5)
    c.drawString((W - fw2) / 2, qr_y - 35, foot2)


# ── Main ───────────────────────────────────────────────────────────────────

def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = rl_canvas.Canvas(OUT, pagesize=(W, H))
    side_one(c)
    side_two(c)
    c.save()
    print(f"Saved: {os.path.abspath(OUT)}")


if __name__ == "__main__":
    build()
