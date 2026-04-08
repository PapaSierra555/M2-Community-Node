"""
Generate ATAK Field Setup Card — M2 Community Node
Print-ready PDF: both cards on one landscape US Letter sheet.
Card trim size: 3.5" x 5.5" (fits standard 4x6 lamination pouches).

Single page: front (left) + back (right) — print, fold/cut, laminate.

Run:  python generate_field_card.py
Output: M2_ATAK_FieldCard.pdf
"""

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from instance_config import cfg as _cfg
_ATAK_PASS = _cfg["ATAK_TRUSTSTORE_PASS"]

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{FONTS}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoBold",     f"{FONTS}/IBMPlexMono-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))

# ── Dimensions ────────────────────────────────────────────────
CARD_W = 3.5 * inch
CARD_H = 5.5 * inch
PAGE_W, PAGE_H = landscape(letter)   # 792 x 612 pt

# Two cards side by side, centered with a 0.5" gutter
GUTTER   = 0.5 * inch
SIDE_MAR = (PAGE_W - 2 * CARD_W - GUTTER) / 2
CARD_Y   = (PAGE_H - CARD_H) / 2
FRONT_X  = SIDE_MAR
BACK_X   = SIDE_MAR + CARD_W + GUTTER

# ── Colors ────────────────────────────────────────────────────
TEXT      = HexColor("#0f0f0f")
MUTED     = HexColor("#4a4a4a")
ACCENT    = HexColor("#921212")
RULE      = HexColor("#dcc8c8")
CROP_COLOR = black

# ── Measurements ──────────────────────────────────────────────
PAD = 0.2 * inch
CROP_LEN = 0.2 * inch
CROP_OFFSET = 0.08 * inch
PUNCH_X_INSET = 0.3 * inch
PUNCH_Y_INSET = 0.3 * inch
PUNCH_RADIUS = 0.12 * inch
BAND_H = 40

# Front spacing (fewer lines, more room)
F_SEC_GAP = 8
F_BULLET = 10.5
F_INFO = 11.5
F_SEC_AFTER = 12
F_OPT_AFTER = 10

# Back spacing (denser)
B_SEC_GAP = 7
B_BULLET = 10
B_INFO = 11
B_SEC_AFTER = 13
B_OPT_AFTER = 11

# Active spacing globals
SEC_GAP = F_SEC_GAP
BULLET_LEAD = F_BULLET
INFO_LEAD = F_INFO
SEC_AFTER = F_SEC_AFTER
OPT_AFTER = F_OPT_AFTER


def draw_crop_marks(c, x, y, w, h):
    c.setStrokeColor(CROP_COLOR)
    c.setLineWidth(0.5)
    for cx, cy in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
        if cx == x:
            c.line(cx - CROP_OFFSET - CROP_LEN, cy, cx - CROP_OFFSET, cy)
        else:
            c.line(cx + CROP_OFFSET, cy, cx + CROP_OFFSET + CROP_LEN, cy)
        if cy == y:
            c.line(cx, cy - CROP_OFFSET - CROP_LEN, cx, cy - CROP_OFFSET)
        else:
            c.line(cx, cy + CROP_OFFSET, cx, cy + CROP_OFFSET + CROP_LEN)


def draw_border(c, x, y, w, h):
    c.setStrokeColor(HexColor("#999999"))
    c.setLineWidth(0.25)
    c.rect(x, y, w, h, stroke=1, fill=0)


def draw_hole_punch(c, x, y, w, h):
    cx = x + PUNCH_X_INSET
    cy = y + h - PUNCH_Y_INSET
    c.setStrokeColor(white)
    c.setLineWidth(0.5)
    c.setDash(2, 2)
    c.circle(cx, cy, PUNCH_RADIUS, stroke=1, fill=0)
    c.setDash()
    c.setLineWidth(0.4)
    c.line(cx - PUNCH_RADIUS - 2, cy, cx + PUNCH_RADIUS + 2, cy)
    c.line(cx, cy - PUNCH_RADIUS - 2, cx, cy + PUNCH_RADIUS + 2)


# ── Text helpers ──────────────────────────────────────────────

def draw_title(c, x, y, w, title, subtitle):
    """ACCENT header band with BigShoulders title + CCC26×LFHI badge."""
    band_top = y + PAD + 2   # == top of card
    band_bot = band_top - BAND_H

    # Band fill
    c.setFillColor(ACCENT)
    c.rect(x, band_bot, w, BAND_H, fill=1, stroke=0)

    # Title text — offset past hole punch zone
    title_x = x + 0.55 * inch
    c.setFillColor(white)
    c.setFont("BigShoulders", 12)
    c.drawString(title_x, band_top - 15, title)
    c.setFont("Sans", 7)
    c.setFillColor(HexColor("#ffdddd"))
    c.drawString(title_x, band_top - 27, subtitle)

    # CCC26×LFHI badge — top-right of band
    badge_w = 56; badge_h = 32
    badge_x = x + w - 4 - badge_w
    badge_y = band_bot + 4
    c.setFillColor(HexColor("#111111"))
    c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(0.5)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 2, fill=1, stroke=1)
    c.setFont("BigShoulders", 8)
    c.setFillColor(HexColor("#c92a2a"))
    c.drawString(badge_x + 3, badge_y + 18, "CCC26")
    c.setFont("MonoBold", 7)
    c.setFillColor(white)
    c.drawString(badge_x + 3, badge_y + 7, "LFHI")
    c.setStrokeColor(HexColor("#444444"))
    c.setLineWidth(0.5)
    c.line(badge_x + 28, badge_y + 4, badge_x + 28, badge_y + 28)
    logo_path = _os.path.join(_ROOT, "outreach", "assets", "lfhi-logo.png")
    if _os.path.exists(logo_path):
        c.drawImage(logo_path, badge_x + 31, badge_y + 6,
                    20, 20, preserveAspectRatio=True)

    return band_bot - 8


def draw_section(c, x, y, w, text):
    c.setFillColor(ACCENT)
    c.setFont("JuraMed", 9)
    c.drawString(x + PAD, y, text.upper())
    y -= 3
    c.setStrokeColor(RULE)
    c.setLineWidth(0.4)
    c.line(x + PAD, y, x + w - PAD, y)
    return y - SEC_AFTER


def draw_bullet(c, x, y, text, bold_prefix=""):
    if bold_prefix:
        c.setFillColor(ACCENT)
        c.setFont("MonoBold", 7.5)
        bw = c.stringWidth(bold_prefix, "MonoBold", 7.5)
        c.drawString(x + PAD + 10, y, bold_prefix)
        c.setFont("Sans", 7.5)
        c.setFillColor(TEXT)
        c.drawString(x + PAD + 10 + bw, y, " " + text)
    else:
        c.setFillColor(TEXT)
        c.setFont("Sans", 7.5)
        c.drawString(x + PAD + 10, y, "\u2022  " + text)
    return y - BULLET_LEAD


def draw_info(c, x, y, label, value):
    c.setFillColor(MUTED)
    c.setFont("Mono", 7.5)
    c.drawString(x + PAD + 10, y, label)
    lw = c.stringWidth(label, "Mono", 7.5) + 3
    c.setFillColor(TEXT)
    c.setFont("MonoBold", 8)
    c.drawString(x + PAD + 10 + lw, y, value)
    return y - INFO_LEAD


def draw_option(c, x, y, text):
    c.setFillColor(ACCENT)
    c.setFont("SansBold", 8)
    c.drawString(x + PAD, y, text)
    return y - OPT_AFTER


def draw_footer(c, x, y, w):
    c.setFillColor(MUTED)
    c.setFont("Sans", 5.5)
    c.drawCentredString(x + w / 2, y + 6,
                        "CommunityNode WiFi  |  yourdomain.com  |  v1.0")


# ── Front ─────────────────────────────────────────────────────
def draw_front(c, x, y):
    global SEC_GAP, BULLET_LEAD, INFO_LEAD, SEC_AFTER, OPT_AFTER
    SEC_GAP, BULLET_LEAD, INFO_LEAD = F_SEC_GAP, F_BULLET, F_INFO
    SEC_AFTER, OPT_AFTER = F_SEC_AFTER, F_OPT_AFTER

    top = y + CARD_H
    cur = draw_title(c, x, top - PAD - 2, CARD_W,
                     "ATAK Field Setup", "M2 Community Node  \u2014  Operator Reference")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "1.  Install Apps")
    cur = draw_bullet(c, x, cur, "ATAK-CIV \u2014 Play Store (Android only)")
    cur = draw_bullet(c, x, cur, "Mumla \u2014 Play Store (push-to-talk voice)")
    cur = draw_bullet(c, x, cur, "Meshtastic Plugin \u2014 GitHub APK (sideload)")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "2.  Connect to Server")
    cur = draw_option(c, x, cur, "Option A \u2014 Data Package (preferred)")
    cur = draw_bullet(c, x, cur, "Join CommunityNode WiFi")
    cur = draw_bullet(c, x, cur, "Scan rack QR \u2192 tap Open in ATAK")
    cur = draw_info(c, x, cur, "Login:", "field / community")
    cur = draw_bullet(c, x, cur, "Tap OK \u2192 server connects automatically")

    cur -= SEC_GAP
    cur = draw_option(c, x, cur, "Option B \u2014 Manual Entry")
    cur = draw_bullet(c, x, cur, "Settings > TAK Servers > Add")
    cur = draw_info(c, x, cur, "Server:", "192.168.8.20  Port: 8089 (SSL)")
    cur = draw_bullet(c, x, cur, "Enroll for cert \u2022 uncheck Default SSL")
    cur = draw_info(c, x, cur, "Cert pwd:", _ATAK_PASS)

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "3.  Set Callsign")
    cur = draw_bullet(c, x, cur, "Settings > My Preferences > Callsign")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "4.  Verify")
    cur = draw_bullet(c, x, cur, "Your icon appears on the shared map")
    cur = draw_bullet(c, x, cur, "Test GeoChat: send a message in #general")

    draw_footer(c, x, y, CARD_W)
    draw_hole_punch(c, x, y, CARD_W, CARD_H)
    draw_border(c, x, y, CARD_W, CARD_H)
    draw_crop_marks(c, x, y, CARD_W, CARD_H)


# ── Back ──────────────────────────────────────────────────────
def draw_back(c, x, y):
    global SEC_GAP, BULLET_LEAD, INFO_LEAD, SEC_AFTER, OPT_AFTER
    SEC_GAP, BULLET_LEAD, INFO_LEAD = B_SEC_GAP, B_BULLET, B_INFO
    SEC_AFTER, OPT_AFTER = B_SEC_AFTER, B_OPT_AFTER

    top = y + CARD_H
    cur = draw_title(c, x, top - PAD - 2, CARD_W,
                     "Voice & Mesh Setup", "M2 Community Node  \u2014  Operator Reference")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "Mumla \u2014 Push-to-Talk Voice")
    cur = draw_info(c, x, cur, "Server:", "192.168.8.20")
    cur = draw_info(c, x, cur, "Port:", "64738  (no password)")
    cur = draw_bullet(c, x, cur, "Open Mumla > Add server > Connect")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "Meshtastic \u2014 LoRa Mesh Radio")
    cur = draw_bullet(c, x, cur, "Install Meshtastic app (Play Store)")
    cur = draw_bullet(c, x, cur, "Pair Heltec V3 radio via Bluetooth")
    cur = draw_bullet(c, x, cur, "ATAK plugin bridges positions + messages")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "Troubleshooting")
    cur = draw_bullet(c, x, cur, "No map tiles? Must be on CommunityNode WiFi")
    cur = draw_bullet(c, x, cur, "Can't reach server? Disable VPN, Private DNS, firewall")
    cur = draw_bullet(c, x, cur, "Cert error? Delete server, re-add from Step 2")
    cur = draw_bullet(c, x, cur, "No GPS? Grant location permission, go outside")
    cur = draw_bullet(c, x, cur, "Not on map? Set Reporting Strategy to Consistent")
    cur = draw_bullet(c, x, cur, "Still not on map? Toggle server off/on in TAK Servers")
    cur = draw_bullet(c, x, cur, "Mumla echo? Use headphones or earbuds")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "Remote Access (Off-Network)")
    cur = draw_info(c, x, cur, "Web map:", "tak.yourdomain.com")
    cur = draw_bullet(c, x, cur, "Email OTP login \u2014 browser, full shared map")
    cur = draw_bullet(c, x, cur, "Remote ATAK: ask operator for VPN access")

    cur -= SEC_GAP
    cur = draw_section(c, x, cur, CARD_W, "Key Info")
    cur = draw_info(c, x, cur, "Community page:", "192.168.8.10:8081")
    cur = draw_bullet(c, x, cur, "Element chat: #general on yourdomain.com")
    cur = draw_bullet(c, x, cur, "Clearnet: element.yourdomain.com")
    cur = draw_bullet(c, x, cur, "Contact: info@yourdomain.com")

    draw_footer(c, x, y, CARD_W)
    draw_hole_punch(c, x, y, CARD_W, CARD_H)
    draw_border(c, x, y, CARD_W, CARD_H)
    draw_crop_marks(c, x, y, CARD_W, CARD_H)


# ── Build PDF ─────────────────────────────────────────────────
def main():
    output = _os.path.join(_ROOT, "operational-pdfs", "M2_ATAK_FieldCard.pdf")
    c = canvas.Canvas(output, pagesize=landscape(letter))
    c.setTitle("M2 Community Node \u2014 ATAK Field Setup Card")
    c.setAuthor("Community Node Project")
    c.setSubject("ATAK onboarding field reference card \u2014 3.5x5.5 for lamination")

    # Front (left) and back (right) on a single landscape page
    draw_front(c, FRONT_X, CARD_Y)
    draw_back(c, BACK_X, CARD_Y)
    c.showPage()

    c.save()
    print(f"Generated: {output}")
    print(f"  Card size: 3.5\" x 5.5\" (fits 4x6 lamination pouches)")
    print(f"  Layout: front + back on one landscape US Letter sheet")
    print(f"  Print single-sided, cut down the center, flip back behind front")


if __name__ == "__main__":
    main()
