"""
Generates the CCC26 Meshtastic channel QR join card.

Users scan with the Meshtastic app — CCC26 channel + PSK import automatically.
Output: meshtastic/pdf/CCC26_Channel_QR_DayOf.pdf
  2 identical cards per letter sheet. Print at 100%, cut on dashed line.
  Laminate or display on-screen day-of.

Dependencies:
  pip install meshtastic qrcode[pil] reportlab
  (run from project root — fonts in scripts/fonts/)

CHANNEL_PSK_B64 must match config_ccc_t114.py and config_ccc_t3s3.py exactly.
Regenerate this PDF after every PSK rotation.
"""

import sys
import base64
import io
import os

try:
    import qrcode
    from meshtastic.protobuf import apponly_pb2, channel_pb2, config_pb2
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("ERROR: pip install meshtastic qrcode[pil] reportlab")
    sys.exit(1)

_here  = os.path.dirname(os.path.abspath(__file__))
FONTS  = os.path.join(_here, "../../scripts/fonts")
ASSETS = os.path.join(_here, "../../community-outreach/assets")
OUTPUT = os.path.join(_here, "../pdf/CCC26_MESHTASTIC_Channel_QR_DayOf.pdf")

pdfmetrics.registerFont(TTFont("BigShoulders", os.path.join(FONTS, "BigShoulders-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Mono",         os.path.join(FONTS, "IBMPlexMono-Regular.ttf")))
pdfmetrics.registerFont(TTFont("MonoBold",     os.path.join(FONTS, "IBMPlexMono-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans",         os.path.join(FONTS, "InstrumentSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("SansBold",     os.path.join(FONTS, "InstrumentSans-Bold.ttf")))

ACCENT    = HexColor("#921212")
DARK      = HexColor("#0f0f0f")
MUTED     = HexColor("#4a4a4a")
CARD_BG   = HexColor("#faf6f6")
CARD_BRD  = HexColor("#e4d0d0")
LIGHT_ACC = HexColor("#f9e0e0")
WHITE     = HexColor("#ffffff")

# ── CONFIG ────────────────────────────────────────────────────────────────────
CHANNEL_NAME    = "CCC26"

# Must match config_ccc_t114.py and config_ccc_t3s3.py exactly.
# Rotate before every event — save to M2_SECRETS.md first.
CHANNEL_PSK_B64 = "WQz1nnlaQN4kGwIlTTSlRQ=="

REGION       = config_pb2.Config.LoRaConfig.RegionCode.US
MODEM_PRESET = config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
# ─────────────────────────────────────────────────────────────────────────────


def build_channel_url():
    psk_bytes   = base64.b64decode(CHANNEL_PSK_B64)
    channel_set = apponly_pb2.ChannelSet()
    ch          = channel_pb2.ChannelSettings()
    ch.name     = CHANNEL_NAME
    ch.psk      = psk_bytes
    channel_set.settings.append(ch)
    channel_set.lora_config.region       = REGION
    channel_set.lora_config.modem_preset = MODEM_PRESET
    data = channel_set.SerializeToString()
    b64  = base64.urlsafe_b64encode(data).decode().rstrip("=")
    return f"https://meshtastic.org/e/#{b64}"


def make_qr_reader(url):
    qr = qrcode.QRCode(version=None,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=12, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_card(c, x, y, w, h, qr_reader, logo_path):
    # Card background
    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.75)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)

    # Header band
    hdr_h = 46
    c.setFillColor(ACCENT)
    c.rect(x, y + h - hdr_h, w, hdr_h, fill=1, stroke=0)

    # Logo
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x + 9, y + h - hdr_h + 5,
                    36, 36, preserveAspectRatio=True)

    # Title + subtitle (left)
    c.setFont("BigShoulders", 17)
    c.setFillColor(WHITE)
    c.drawString(x + 53, y + h - 27, "CCC26 MESH — M2 COMMUNITY NODE")
    c.setFont("Sans", 8)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(x + 53, y + h - 41, "Off-grid communications — no internet required")

    # FOR BYOD USERS — white-bordered box, right side of header
    box_w = 168
    box_h = 34
    box_x = x + w - box_w - 8
    box_y = y + h - hdr_h + 6
    c.setFillColor(WHITE)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1)
    c.roundRect(box_x, box_y, box_w, box_h, 3, fill=0, stroke=1)
    c.setFont("BigShoulders", 13)
    c.setFillColor(WHITE)
    c.drawCentredString(box_x + box_w / 2, box_y + box_h - 16, "FOR BYOD USERS")
    c.setFont("Sans", 7)
    c.setFillColor(WHITE)
    c.drawCentredString(box_x + box_w / 2, box_y + 5, "Bring your own Meshtastic device")

    # Layout constants
    badge_h  = 22
    badge_pad = 10
    content_top = y + h - hdr_h - 8          # just below header
    content_bot = y + badge_h + badge_pad     # just above bottom badge
    content_h   = content_top - content_bot

    # QR code — right column, sized to fill content height with margin
    qr_size = content_h - 12
    qr_x    = x + w - qr_size - 14
    qr_y    = content_bot + 6
    c.setFillColor(WHITE)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.rect(qr_x - 4, qr_y - 4, qr_size + 8, qr_size + 8, fill=1, stroke=1)
    c.drawImage(qr_reader, qr_x, qr_y, qr_size, qr_size)

    # Left column — BYOD callout + steps
    left_w   = qr_x - x - 24
    byod_top = content_top - 4

    # BYOD callout box (two short lines)
    byod_h = 26
    byod_y = byod_top - byod_h
    c.setFillColor(LIGHT_ACC)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.5)
    c.roundRect(x + 10, byod_y, left_w, byod_h, 2, fill=1, stroke=1)
    c.setFont("SansBold", 7)
    c.setFillColor(ACCENT)
    c.drawString(x + 14, byod_y + 14, "Have your own Meshtastic device? Scan to join.")
    c.setFont("Sans", 7)
    c.setFillColor(MUTED)
    c.drawString(x + 14, byod_y + 4, "Loaner devices are already configured — no setup needed.")

    # Steps
    steps = [
        "1. Install Meshtastic app (Android or iPhone)",
        "2. Pair your device via Bluetooth in the app",
        "3. Scan the QR — channel imports automatically",
        "4. Settings → User: enter your name or handle",
        "5. Tap CCC26 channel to send a message",
    ]
    step_x = x + 14
    step_y = byod_y - 18
    for step in steps:
        c.setFont("Sans", 8.5)
        c.setFillColor(DARK)
        c.drawString(step_x, step_y, step)
        step_y -= 14

    # Channel badge at bottom
    badge_y = y + badge_pad - 4
    c.setFillColor(LIGHT_ACC)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.75)
    c.roundRect(x + 14, badge_y, w - 28, 22, 2, fill=1, stroke=1)
    c.setFont("MonoBold", 7.5)
    c.setFillColor(ACCENT)
    c.drawCentredString(
        x + w / 2, badge_y + 7,
        f"Channel: {CHANNEL_NAME}  —  Region: US  —  LongFast  —  Airplane mode OK, keep BT on"
    )


def main():
    url = build_channel_url()
    print(f"Channel: {CHANNEL_NAME}  |  PSK: {CHANNEL_PSK_B64}")
    print(f"URL: {url[:80]}...")

    qr_reader = make_qr_reader(url)
    logo_path = os.path.join(ASSETS, "lfhi-logo.png")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    W, H = letter
    M    = 36
    c    = rl_canvas.Canvas(OUTPUT, pagesize=letter)

    card_h = (H - 3 * M) / 2
    card_w = W - 2 * M

    draw_card(c, M, H / 2 + M / 2, card_w, card_h, qr_reader, logo_path)
    draw_card(c, M, M, card_w, card_h, qr_reader, logo_path)

    # Dashed cut line
    c.setStrokeColor(HexColor("#bbbbbb"))
    c.setLineWidth(0.5)
    c.setDash(4, 4)
    cut_y = H / 2
    c.line(M / 2, cut_y, W - M / 2, cut_y)
    c.setDash()
    c.setFont("Sans", 6.5)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(W / 2, cut_y + 4, "CUT")

    c.setFont("Sans", 6)
    c.setFillColor(HexColor("#cccccc"))
    c.drawCentredString(W / 2, 10,
        "Print at 100% / Actual Size — do not scale — 2 cards per sheet — regenerate after PSK rotation")

    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")
    print("Print, cut, laminate — or display digitally day-of.")


if __name__ == "__main__":
    main()
