"""
Generates a Meshtastic channel QR card for M2 Community Node.

Users scan with the Meshtastic app — CommunityNode channel + PSK
import automatically. No manual key entry needed.

Output: community-outreach/pdf/M2_Mesh_ChannelQR_DayOf.pdf
  2 identical cards per letter sheet. Print at 100%, cut on dashed line.

Dependencies:
  pip install meshtastic qrcode[pil] reportlab
  (fonts must be in scripts/fonts/ — run from project root)

CHANNEL_PSK_B64 must match config_heltec_v3.py exactly.
Regenerate after every PSK rotation.
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
OUTPUT = os.path.join(_here, "../pdf/M2_Mesh_ChannelQR_DayOf.pdf")

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
CHANNEL_NAME    = "CommunityNode"
CHANNEL_PSK_B64 = "+aVLpPfwX/SfD0j8Xe56cg=="  # REPLACE before every event — must match config_heltec_v3.py
REGION          = config_pb2.Config.LoRaConfig.RegionCode.US
MODEM_PRESET    = config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
# ─────────────────────────────────────────────────────────────────────────────


def build_channel_url():
    psk_bytes   = base64.b64decode(CHANNEL_PSK_B64)
    channel_set = apponly_pb2.ChannelSet()
    ch          = channel_pb2.ChannelSettings()
    ch.name = CHANNEL_NAME
    ch.psk  = psk_bytes
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
    """Draw one card at (x,y) bottom-left, dimensions w×h."""
    # Card background
    c.setFillColor(CARD_BG)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.75)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)

    # Header band
    hdr_h = 46
    c.setFillColor(ACCENT)
    c.rect(x, y + h - hdr_h, w, hdr_h, fill=1, stroke=0)
    if os.path.exists(logo_path):
        c.drawImage(logo_path, x + 9, y + h - hdr_h + 5,
                    36, 36, preserveAspectRatio=True)
    c.setFont("BigShoulders", 17)
    c.setFillColor(WHITE)
    c.drawString(x + 53, y + h - 27, "M2 COMMUNITY NODE")
    c.setFont("Sans", 8)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(x + 53, y + h - 41, "Meshtastic mesh — off-grid communications")

    # Steps (left column)
    steps = [
        "1. Install Meshtastic app (Android or iPhone)",
        "2. Enable Bluetooth on your phone",
        "3. Scan the QR — channel imports automatically",
        "4. Settings → User: enter your name",
        "5. Tap the channel to send a message",
    ]
    step_x = x + 14
    step_y = y + h - hdr_h - 18
    for step in steps:
        c.setFont("Sans", 8.5)
        c.setFillColor(DARK)
        c.drawString(step_x, step_y, step)
        step_y -= 14

    # QR code (right side)
    qr_size = h - hdr_h - 70
    qr_x    = x + w - qr_size - 12
    qr_y    = y + h - hdr_h - 12 - qr_size
    c.setFillColor(WHITE)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.rect(qr_x - 4, qr_y - 4, qr_size + 8, qr_size + 8, fill=1, stroke=1)
    c.drawImage(qr_reader, qr_x, qr_y, qr_size, qr_size)

    # Channel badge at bottom
    badge_y = y + 9
    c.setFillColor(LIGHT_ACC)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.75)
    c.roundRect(x + 14, badge_y, w - 28, 22, 2, fill=1, stroke=1)
    c.setFont("MonoBold", 7.5)
    c.setFillColor(ACCENT)
    c.drawCentredString(x + w / 2, badge_y + 7,
                        f"Channel: {CHANNEL_NAME}  —  Region: US  —  LongFast  —  No internet required")


def main():
    if CHANNEL_PSK_B64 == "AAAAAAAAAAAAAAAAAAAAAA==":
        print("WARNING: Using null placeholder PSK. Generate and paste a real key first.")
        print("  python -c \"import os,base64; print(base64.b64encode(os.urandom(16)).decode())\"")

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

    # Top card
    draw_card(c, M, H / 2 + M / 2, card_w, card_h, qr_reader, logo_path)
    # Bottom card
    draw_card(c, M, M, card_w, card_h, qr_reader, logo_path)

    # Dashed cut line between cards
    c.setStrokeColor(HexColor("#bbbbbb"))
    c.setLineWidth(0.5)
    c.setDash(4, 4)
    cut_y = H / 2
    c.line(M / 2, cut_y, W - M / 2, cut_y)
    c.setDash()
    c.setFont("Sans", 6.5)
    c.setFillColor(HexColor("#aaaaaa"))
    c.drawCentredString(W / 2, cut_y + 4, "CUT")

    # Print note
    c.setFont("Sans", 6)
    c.setFillColor(HexColor("#cccccc"))
    c.drawCentredString(W / 2, 10,
        "Print at 100% / Actual Size — do not scale — 2 cards per sheet — regenerate after PSK rotation")

    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")
    print("Share URL digitally or print card for day-of distribution.")


if __name__ == "__main__":
    main()
