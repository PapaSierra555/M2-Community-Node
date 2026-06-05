"""
Generates CCC26 device sign-out and instruction cards.

Landscape 4"x6" cards — 2 per letter sheet, duplex short-edge flip for backs.
11 devices total: CCC fleet (MESH 01-08, T114) + personal (PS-01/02/03, T3S3).

Output:
  meshtastic/pdf/CCC26_DeviceCard_Front.pdf
  meshtastic/pdf/CCC26_DeviceCard_Back.pdf

Print at 100%, duplex short-edge flip. Cut on crop marks. Laminate.

Dependencies:
  pip install reportlab qrcode[pil]
  (run from project root — fonts in scripts/fonts/, assets in community-outreach/assets/)
"""

import sys
import os
import io

try:
    import qrcode
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("ERROR: pip install reportlab qrcode[pil]")
    sys.exit(1)

_here   = os.path.dirname(os.path.abspath(__file__))
FONTS   = os.path.join(_here, "../../scripts/fonts")
ASSETS  = os.path.join(_here, "../../community-outreach/assets")
OUT_DIR = os.path.join(_here, "../pdf")

pdfmetrics.registerFont(TTFont("BigShoulders", os.path.join(FONTS, "BigShoulders-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Mono",         os.path.join(FONTS, "IBMPlexMono-Regular.ttf")))
pdfmetrics.registerFont(TTFont("MonoBold",     os.path.join(FONTS, "IBMPlexMono-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans",         os.path.join(FONTS, "InstrumentSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("SansBold",     os.path.join(FONTS, "InstrumentSans-Bold.ttf")))

ACCENT    = HexColor("#921212")
DARK      = HexColor("#0f0f0f")
MUTED     = HexColor("#4a4a4a")
WHITE     = HexColor("#ffffff")
CARD_BG   = HexColor("#faf6f6")
CARD_BRD  = HexColor("#e4d0d0")
LIGHT_ACC = HexColor("#f9e0e0")

# Landscape 4"x6"
CARD_W = 6 * 72   # 432 pt
CARD_H = 4 * 72   # 288 pt

DEVICES = [
    ("01", "MESH 01", "T114 — Loaner"),
    ("02", "MESH 02", "T114 — Loaner"),
    ("03", "MESH 03", "T114 — Loaner"),
    ("04", "MESH 04", "T114 — Loaner"),
    ("05", "MESH 05", "T114 — Loaner"),
    ("06", "MESH 06", "T114 — Loaner"),
    ("07", "MESH 07", "T114 — Loaner"),
    ("08", "MESH 08", "T114 — Loaner"),
    ("PS-01", "PS-01", "T3S3 — Personal"),
    ("PS-02", "PS-02", "T3S3 — Personal"),
    ("PS-03", "PS-03", "T3S3 — Personal"),
]

ANDROID_QR_URL = "https://play.google.com/store/apps/details?id=com.geeksville.mesh"
IPHONE_QR_URL  = "https://apps.apple.com/us/app/meshtastic/id1586432531"


def make_qr(url):
    qr = qrcode.QRCode(version=None,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_crop_marks(c, x, y, w, h, tick=8):
    c.setStrokeColor(HexColor("#aaaaaa"))
    c.setLineWidth(0.25)
    for cx, cy in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
        dx = tick if cx == x else -tick
        dy = tick if cy == y else -tick
        c.line(cx, cy, cx + dx, cy)
        c.line(cx, cy, cx, cy + dy)


def draw_front(c, x, y, num, long_name, type_label, android_qr, iphone_qr, logo_path):
    # Background
    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=1)

    # Header — full width, 38pt
    hdr_h = 38
    c.setFillColor(ACCENT)
    c.rect(x, y + CARD_H - hdr_h, CARD_W, hdr_h, fill=1, stroke=0)

    # Logo in header
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x + 8, y + CARD_H - hdr_h + 3,
                    32, 32, preserveAspectRatio=True)

    # Header title
    c.setFont("BigShoulders", 15)
    c.setFillColor(WHITE)
    c.drawString(x + 46, y + CARD_H - 22, "CCC26 MESH DEVICE")
    c.setFont("Sans", 7)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(x + 46, y + CARD_H - 34, f"{long_name}  —  {type_label}")

    # Device number badge — right side of header
    badge_r = 16
    badge_cx = x + CARD_W - badge_r - 8
    badge_cy = y + CARD_H - hdr_h / 2
    c.setFillColor(WHITE)
    c.circle(badge_cx, badge_cy, badge_r, fill=1, stroke=0)
    font_sz = 13 if len(num) <= 2 else 9
    c.setFont("BigShoulders", font_sz)
    c.setFillColor(ACCENT)
    c.drawCentredString(badge_cx, badge_cy - font_sz * 0.37, num)

    # Content area — two columns below header
    content_y_top = y + CARD_H - hdr_h - 6
    sign_h        = 38
    content_y_bot = y + sign_h + 4

    # Left column: HOW TO USE steps
    col_split = x + CARD_W * 0.55
    c.setFont("SansBold", 6.5)
    c.setFillColor(ACCENT)
    c.drawString(x + 10, content_y_top - 2, "HOW TO USE")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.4)
    c.line(x + 10, content_y_top - 4, x + 10 + 50, content_y_top - 4)

    steps = [
        "1. This device is pre-configured. Pick up and go.",
        "2. Enable Bluetooth on your phone",
        "3. Open Meshtastic app — pair this device",
        "4. Settings → User: enter your name",
        "5. Tap CCC26 channel to send messages",
    ]
    step_y = content_y_top - 16
    for step in steps:
        c.setFont("Sans", 7)
        c.setFillColor(DARK)
        c.drawString(x + 10, step_y, step)
        step_y -= 11

    # Right column: GET THE APP
    qr_col_x = col_split + 6
    c.setFont("SansBold", 6.5)
    c.setFillColor(ACCENT)
    c.drawString(qr_col_x, content_y_top - 2, "GET THE APP")
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.4)
    c.line(qr_col_x, content_y_top - 4, qr_col_x + 50, content_y_top - 4)

    qr_sz      = 46
    qr_top     = content_y_top - 14
    android_x  = qr_col_x
    iphone_x   = qr_col_x + qr_sz + 18

    c.setFillColor(WHITE)
    c.rect(android_x - 2, qr_top - qr_sz - 2, qr_sz + 4, qr_sz + 4, fill=1, stroke=0)
    c.drawImage(android_qr, android_x, qr_top - qr_sz, qr_sz, qr_sz)
    c.setFont("Sans", 6)
    c.setFillColor(MUTED)
    c.drawCentredString(android_x + qr_sz / 2, qr_top - qr_sz - 9, "Android")

    c.setFillColor(WHITE)
    c.rect(iphone_x - 2, qr_top - qr_sz - 2, qr_sz + 4, qr_sz + 4, fill=1, stroke=0)
    c.drawImage(iphone_qr, iphone_x, qr_top - qr_sz, qr_sz, qr_sz)
    c.setFont("Sans", 6)
    c.setFillColor(MUTED)
    c.drawCentredString(iphone_x + qr_sz / 2, qr_top - qr_sz - 9, "iPhone")

    # Sign-out strip
    c.setFillColor(LIGHT_ACC)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.rect(x + 4, y + 2, CARD_W - 8, sign_h, fill=1, stroke=1)
    c.setFont("SansBold", 6.5)
    c.setFillColor(ACCENT)
    c.drawString(x + 10, y + sign_h - 9, f"DEVICE {num} SIGN-OUT")
    c.setFont("Sans", 6.5)
    c.setFillColor(DARK)
    c.drawString(x + 10, y + sign_h - 20, "Borrower: ______________________________")
    c.drawString(x + 10, y + sign_h - 30, "Signature: _____________________________")


def draw_back(c, x, y, num, logo_path):
    # Dark background
    c.setFillColor(DARK)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)

    # Horizontal line texture
    c.setStrokeColor(HexColor("#1e1e1e"))
    c.setLineWidth(0.3)
    for line_y in range(int(y), int(y + CARD_H), 8):
        c.line(x, line_y, x + CARD_W, line_y)

    # Accent border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.rect(x + 4, y + 4, CARD_W - 8, CARD_H - 8, fill=0, stroke=1)

    # Logo
    logo_sz = 32
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x + 18, y + CARD_H / 2 - logo_sz / 2,
                    logo_sz, logo_sz, preserveAspectRatio=True)

    # Title block (centered in remaining space)
    cx = x + logo_sz + 40 + (CARD_W - logo_sz - 40) / 2

    c.setFont("BigShoulders", 22)
    c.setFillColor(WHITE)
    c.drawCentredString(cx, y + CARD_H / 2 + 20, "CCC26")
    c.setFont("Sans", 9)
    c.setFillColor(ACCENT)
    c.drawCentredString(cx, y + CARD_H / 2 + 6, "MESH DEVICE")

    # Device number circle
    circle_r  = 38
    circle_cx = cx
    circle_cy = y + CARD_H / 2 - 28
    c.setFillColor(ACCENT)
    c.circle(circle_cx, circle_cy, circle_r, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.circle(circle_cx, circle_cy, circle_r - 2, fill=0, stroke=1)
    c.setLineWidth(1)
    font_sz = 36 if len(num) <= 2 else 22
    c.setFont("BigShoulders", font_sz)
    c.setFillColor(WHITE)
    c.drawCentredString(circle_cx, circle_cy - font_sz * 0.35, num)

    # Footer
    c.setFont("Sans", 6.5)
    c.setFillColor(MUTED)
    c.drawCentredString(x + CARD_W / 2, y + 18, "CCC26 — M2 Community Node — Off-Grid Event Communications")
    c.setFont("Sans", 6)
    c.setFillColor(HexColor("#555555"))
    c.drawCentredString(x + CARD_W / 2, y + 9, "Return to operator after event")


def main():
    logo_path  = os.path.join(ASSETS, "lfhi-logo.png")
    android_qr = make_qr(ANDROID_QR_URL)
    iphone_qr  = make_qr(IPHONE_QR_URL)
    os.makedirs(OUT_DIR, exist_ok=True)

    W, H   = letter                          # 612 x 792
    MARGIN = 72                              # 1" margins top/bottom
    card_x = (W - CARD_W) / 2              # centered horizontally

    start_y_top = H - MARGIN - CARD_H       # 792 - 72 - 288 = 432
    start_y_bot = MARGIN                     # 72

    pairs = [DEVICES[i:i+2] for i in range(0, len(DEVICES), 2)]

    # ── FRONT ────────────────────────────────────────────────────────────────
    front_path = os.path.join(OUT_DIR, "CCC26_DeviceCard_Front.pdf")
    c = rl_canvas.Canvas(front_path, pagesize=letter)

    for pair in pairs:
        num, long_name, type_label = pair[0]
        draw_front(c, card_x, start_y_top, num, long_name, type_label,
                   android_qr, iphone_qr, logo_path)
        draw_crop_marks(c, card_x, start_y_top, CARD_W, CARD_H)

        if len(pair) > 1:
            num, long_name, type_label = pair[1]
            draw_front(c, card_x, start_y_bot, num, long_name, type_label,
                       android_qr, iphone_qr, logo_path)
            draw_crop_marks(c, card_x, start_y_bot, CARD_W, CARD_H)

        # Cut line between cards
        c.setStrokeColor(HexColor("#cccccc"))
        c.setLineWidth(0.4)
        c.setDash(4, 4)
        cut_y = (start_y_top + start_y_bot + CARD_H) / 2
        c.line(MARGIN / 2, cut_y, W - MARGIN / 2, cut_y)
        c.setDash()
        c.setFont("Sans", 6)
        c.setFillColor(HexColor("#bbbbbb"))
        c.drawCentredString(W / 2, cut_y + 3, "CUT")

        c.setFont("Sans", 5.5)
        c.setFillColor(HexColor("#cccccc"))
        c.drawCentredString(W / 2, 8,
            "CCC26 Device Cards — Print at 100% — Duplex short-edge flip for backs")
        c.showPage()

    c.save()
    print(f"Front saved: {os.path.abspath(front_path)}")

    # ── BACK (short-edge flip: top slot → bottom position) ───────────────────
    back_path = os.path.join(OUT_DIR, "CCC26_DeviceCard_Back.pdf")
    c = rl_canvas.Canvas(back_path, pagesize=letter)

    for pair in pairs:
        num, _, _ = pair[0]
        draw_back(c, card_x, start_y_bot, num, logo_path)
        draw_crop_marks(c, card_x, start_y_bot, CARD_W, CARD_H)

        if len(pair) > 1:
            num, _, _ = pair[1]
            draw_back(c, card_x, start_y_top, num, logo_path)
            draw_crop_marks(c, card_x, start_y_top, CARD_W, CARD_H)

        c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(0.4)
        c.setDash(4, 4)
        cut_y = (start_y_top + start_y_bot + CARD_H) / 2
        c.line(MARGIN / 2, cut_y, W - MARGIN / 2, cut_y)
        c.setDash()
        c.showPage()

    c.save()
    print(f"Back saved:  {os.path.abspath(back_path)}")
    print()
    print("Print instructions:")
    print("  1. Print CCC26_DeviceCard_Front.pdf (side 1)")
    print("  2. Reload — flip on SHORT edge")
    print("  3. Print CCC26_DeviceCard_Back.pdf (side 2)")
    print("  4. Cut on crop marks. Laminate.")
    print(f"  {len(DEVICES)} devices — {len(pairs)} sheets front+back")


if __name__ == "__main__":
    main()
