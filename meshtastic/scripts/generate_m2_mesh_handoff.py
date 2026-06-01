"""
M2 Community Node — Meshtastic Field Operations Handoff
Operator reference: hardware, scripts, pre-event checklist, troubleshooting.

Output: meshtastic/pdf/M2_Mesh_Handoff.pdf

Usage: python meshtastic/scripts/generate_m2_mesh_handoff.py
"""
import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

_script_dir = os.path.dirname(os.path.abspath(__file__))
FONTS       = os.path.join(_script_dir, "../../scripts/fonts")
ASSETS      = os.path.join(_script_dir, "../../community-outreach/assets")
OUTPUT      = os.path.join(_script_dir, "../pdf/M2_Mesh_Handoff.pdf")

pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",         f"{FONTS}/IBMPlexMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("MonoBold",     f"{FONTS}/IBMPlexMono-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))

ACCENT    = HexColor("#921212")
DARK      = HexColor("#0f0f0f")
MUTED     = HexColor("#4a4a4a")
CARD_BG   = HexColor("#faf6f6")
CARD_BRD  = HexColor("#e4d0d0")
LIGHT_ACC = HexColor("#f9e0e0")
LIGHT_GR  = HexColor("#f0f5f0")
LIGHT_BL  = HexColor("#e8f0fb")
WHITE     = HexColor("#ffffff")
GREEN     = HexColor("#1a7a3a")

W, H   = letter
M      = 40
HDR_H  = 54
FTR_H  = 22
TOP_Y  = H - HDR_H - 12
BOT_Y  = FTR_H + 8
BODY_W = W - 2 * M

_logo_path = os.path.join(ASSETS, "lfhi-logo.png")


def draw_header(c, page_num=None):
    c.setFillColor(ACCENT)
    c.rect(0, H - HDR_H, W, HDR_H, fill=1, stroke=0)
    if os.path.exists(_logo_path):
        c.drawImage(_logo_path, M, H - HDR_H + 9, 36, 36, preserveAspectRatio=True)
    c.setFont("BigShoulders", 20)
    c.setFillColor(WHITE)
    c.drawString(M + 44, H - 30, "M2 COMMUNITY NODE")
    c.setFont("Sans", 9)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(M + 44, H - 46, "Meshtastic Field Operations Handoff")
    c.setFont("JuraMed", 9)
    c.setFillColor(WHITE)
    c.drawRightString(W - M, H - 30,
        "2x Heltec LoRa V3  |  CommunityNode  |  US / LONG_FAST  |  ROUTER")
    if page_num:
        c.setFont("Sans", 8)
        c.setFillColor(HexColor("#ffcccc"))
        c.drawRightString(W - M, H - 46, f"Page {page_num}")


def draw_footer(c):
    c.setFillColor(HexColor("#1a1a1a"))
    c.rect(0, 0, W, FTR_H, fill=1, stroke=0)
    c.setFont("Sans", 7)
    c.setFillColor(HexColor("#666666"))
    c.drawString(M, 8, "M2 Community Node  —  Internal Use Only  —  Rotate PSK before every event")
    c.drawRightString(W - M, 8, "lightfighterhomefront.org")


def rule(c, x, y, w, col=None, lw=0.5):
    c.setStrokeColor(col or CARD_BRD)
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)


def h1(c, y, text, num=""):
    if num:
        c.setFont("JuraMed", 9)
        c.setFillColor(ACCENT)
        c.drawString(M, y, num)
    c.setFont("BigShoulders", 16)
    c.setFillColor(ACCENT)
    offset = c.stringWidth(num + "  ", "JuraMed", 9) if num else 0
    c.drawString(M + offset, y, text.upper())
    rule(c, M, y - 5, BODY_W, col=ACCENT, lw=1.5)
    return y - 22


def body(c, y, text, indent=0, bold=False):
    font = "SansBold" if bold else "Sans"
    c.setFont(font, 9)
    c.setFillColor(DARK)
    words = text.split()
    lines = []; line = []
    max_w = BODY_W - indent
    for w in words:
        test = " ".join(line + [w])
        if c.stringWidth(test, font, 9) <= max_w:
            line.append(w)
        else:
            lines.append(" ".join(line)); line = [w]
    if line:
        lines.append(" ".join(line))
    for ln in lines:
        c.drawString(M + indent, y, ln)
        y -= 13
    return y - 2


def mono_line(c, y, text, indent=0):
    c.setFont("Mono", 8)
    c.setFillColor(HexColor("#333333"))
    c.drawString(M + indent, y, text)
    return y - 12


def step(c, y, num, text):
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, f"{num}.")
    c.setFont("Sans", 9)
    c.setFillColor(DARK)
    c.drawString(M + 18, y, text)
    return y - 14


def substep(c, y, text):
    c.setFont("Mono", 7.5)
    c.setFillColor(MUTED)
    c.drawString(M + 28, y, "→  " + text)
    return y - 12


def code_block(c, y, lines, w=None):
    bw = w or BODY_W
    bh = len(lines) * 13 + 12
    c.setFillColor(HexColor("#1e1e1e"))
    c.roundRect(M, y - bh, bw, bh, 3, fill=1, stroke=0)
    ty = y - 10
    for line in lines:
        c.setFont("Mono", 8)
        c.setFillColor(HexColor("#00ff88"))
        c.drawString(M + 10, ty, line)
        ty -= 13
    return y - bh - 8


def callout(c, y, kind, heading, lines):
    styles = {
        "warn":  (HexColor("#fffbea"), HexColor("#e6a817"), HexColor("#a06010")),
        "info":  (LIGHT_BL,           HexColor("#2e6cc7"), HexColor("#1a3a7a")),
        "green": (LIGHT_GR,           GREEN,               GREEN),
    }
    bg, border_col, head_col = styles[kind]
    bh = 16 + len(lines) * 13 + 8
    c.setFillColor(bg)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.roundRect(M, y - bh, BODY_W, bh, 3, fill=1, stroke=1)
    c.setStrokeColor(border_col)
    c.setLineWidth(3)
    c.line(M + 1.5, y - bh + 2, M + 1.5, y - 2)
    c.setFont("SansBold", 8.5)
    c.setFillColor(head_col)
    c.drawString(M + 10, y - 12, heading)
    ty = y - 24
    for ln in lines:
        c.setFont("Sans", 8)
        c.setFillColor(DARK)
        c.drawString(M + 10, ty, ln)
        ty -= 13
    return y - bh - 8


def table_header(c, y, cols):
    """cols = [(text, x, w), ...]"""
    h = 18
    for text, x, w in cols:
        c.setFillColor(ACCENT)
        c.rect(x, y - h, w, h, fill=1, stroke=0)
        c.setFont("SansBold", 8)
        c.setFillColor(WHITE)
        c.drawString(x + 6, y - 13, text)
    return y - h


def table_row(c, y, cells, shade=False):
    h = 16
    for text, x, w in cells:
        c.setFillColor(HexColor("#f0eeee") if shade else WHITE)
        c.setStrokeColor(CARD_BRD)
        c.setLineWidth(0.4)
        c.rect(x, y - h, w, h, fill=1, stroke=1)
        c.setFont("Sans", 8)
        c.setFillColor(DARK)
        c.drawString(x + 6, y - 12, text)
    return y - h


def mono_row(c, y, cells, shade=False):
    h = 16
    for text, font, x, w in cells:
        c.setFillColor(HexColor("#f0eeee") if shade else WHITE)
        c.setStrokeColor(CARD_BRD)
        c.setLineWidth(0.4)
        c.rect(x, y - h, w, h, fill=1, stroke=1)
        c.setFont(font, 7.5 if font == "Mono" else 8)
        c.setFillColor(DARK)
        c.drawString(x + 6, y - 11.5, text)
    return y - h


def spacer(y, n=10):
    return y - n


def check_break(c, y, needed, pages):
    if y - needed < BOT_Y:
        draw_footer(c)
        c.showPage()
        pages[0] += 1
        draw_header(c, pages[0])
        draw_footer(c)
        return TOP_Y
    return y


def build():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)
    pages = [1]

    draw_header(c, 1)
    draw_footer(c)
    y = TOP_Y - 14

    # ── SECTION 1: HARDWARE ───────────────────────────────────────────────────
    y = check_break(c, y, 200, pages)
    y = h1(c, y, "Hardware Inventory", "1.")
    y = body(c, y,
        "M2 runs two node types: 2 rack-mounted Heltec LoRa V3 infrastructure nodes (ROUTER role) "
        "and 8 Heltec T114 field nodes (CLIENT role) loaned to attendees at events. "
        "Rack nodes bridge traffic to MQTT/Matrix via Pi 2. Field nodes are pre-configured checkout devices.")
    y = spacer(y, 10)

    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "Infrastructure — Heltec LoRa V3 × 2  (ROUTER, rack-mounted)")
    y = spacer(y, 14)
    cols_spec = [
        ("Spec",  M,              int(BODY_W * 0.34)),
        ("Value", M + int(BODY_W * 0.34), int(BODY_W * 0.66)),
    ]
    y = table_header(c, y, cols_spec)
    spec_rows = [
        ("Chip",          "ESP32-S3 (Espressif)"),
        ("Radio",         "SX1262 LoRa 915 MHz"),
        ("GPS",           "None — infrastructure node, position not required"),
        ("Display",       "0.96\" OLED — 30s screen timeout"),
        ("Power",         "5V USB-C via rack panel power strip"),
        ("Firmware",      "Meshtastic — flash via esptool (.bin file)"),
        ("Role",          "ROUTER — relays all mesh traffic, bridges to MQTT via Pi 2"),
        ("Node names",    "M2 Community Node 01 / 02  |  short: M2-1, M2-2"),
        ("Host",          "Pi 2 — USB serial /dev/ttyUSB0, /dev/ttyUSB1"),
        ("MQTT bridge",   "mosquitto on Pi 2 — systemctl: meshtastic-mqtt"),
    ]
    for i, (spec, val) in enumerate(spec_rows):
        col_w1 = int(BODY_W * 0.34)
        col_w2 = int(BODY_W * 0.66)
        y = table_row(c, y, [
            (spec, M,          col_w1),
            (val,  M + col_w1, col_w2),
        ], shade=(i % 2 == 0))
    y = spacer(y, 10)

    y = check_break(c, y, 180, pages)
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "Field Nodes — Heltec T114 × 8  (CLIENT, loan devices)")
    y = spacer(y, 14)
    y = table_header(c, y, cols_spec)
    t114_rows = [
        ("Chip",          "nRF52840 (Nordic Semiconductor)"),
        ("Radio",         "SX1262 LoRa 915 MHz"),
        ("GPS",           "L76K — built-in GPS for location sharing"),
        ("Display",       "1.54\" E-ink — always-on node info screen"),
        ("Power",         "USB-C + Li-Po battery included in kit"),
        ("Firmware",      "Meshtastic — flash via UF2 drag-and-drop (no esptool)"),
        ("Role",          "CLIENT — personal loan device, one per attendee"),
        ("Node names",    "M2 Field Node 01-08  |  short: MF-1 through MF-8"),
        ("Config script", "meshtastic/scripts/config_m2_t114.py"),
        ("Channel",       "CommunityNode (shared PSK with rack nodes)"),
    ]
    for i, (spec, val) in enumerate(t114_rows):
        col_w1 = int(BODY_W * 0.34)
        col_w2 = int(BODY_W * 0.66)
        y = table_row(c, y, [
            (spec, M,          col_w1),
            (val,  M + col_w1, col_w2),
        ], shade=(i % 2 == 0))
    y = spacer(y, 14)

    # ── SECTION 2: NETWORK ARCHITECTURE ──────────────────────────────────────
    y = check_break(c, y, 150, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "Network Architecture", "2.")
    y = body(c, y,
        "M2 runs 2 rack-mounted Heltec V3 ROUTER nodes (infrastructure) plus 8 T114 CLIENT nodes "
        "(loan devices for attendees). The rack nodes connect to Pi 2 via USB serial. "
        "mosquitto bridges Meshtastic traffic to the internal MQTT broker, allowing Matrix "
        "and ATAK to receive mesh messages. T114 field nodes communicate over LoRa only — "
        "no serial connection to Pi 2.")
    y = spacer(y, 10)

    arch_lines = [
        "Personal phone  →  Bluetooth  →  M2-1 or M2-2 (LoRa radio)",
        "M2-1 / M2-2     →  USB serial  →  Pi 2 /dev/ttyUSB0, /dev/ttyUSB1",
        "Pi 2 mosquitto  →  MQTT topic  →  Matrix bridge / ATAK CoT relay",
        "M2-1  <-->  M2-2  (dual ROUTER — redundant coverage and relay)",
    ]
    y = code_block(c, y, arch_lines)

    y = callout(c, y, "info", "MQTT bridge service",
        ["Service: meshtastic-mqtt  (systemd, Pi 2)",
         "Status:  sudo systemctl status meshtastic-mqtt",
         "Restart: sudo systemctl restart meshtastic-mqtt",
         "Logs:    sudo journalctl -u meshtastic-mqtt -f"])
    y = spacer(y, 8)

    # ── SECTION 3: SCRIPTS ────────────────────────────────────────────────────
    y = check_break(c, y, 200, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "Script Reference", "3.")
    y = body(c, y, "All scripts run from the project root directory.")
    y = spacer(y, 10)

    col_s  = int(BODY_W * 0.28)
    col_w2 = int(BODY_W * 0.16)
    col_d  = BODY_W - col_s - col_w2
    y = table_header(c, y, [
        ("Script  (meshtastic/scripts/)", M,                   col_s),
        ("When",                          M + col_s,           col_w2),
        ("What it does",                  M + col_s + col_w2,  col_d),
    ])
    scripts = [
        ("config_heltec_v3.py",
         "Before event",
         "Push PSK + config to 2 rack nodes. Run after PSK rotation."),
        ("config_m2_t114.py",
         "Before event",
         "Push PSK + config to 8 T114 field nodes. Run after PSK rotation."),
        ("gen_m2_channel_qr.py",
         "Before event",
         "Regenerate day-of QR card with current PSK."),
        ("generate_m2_mesh_handoff.py",
         "When docs change",
         "Rebuild this operator reference PDF."),
        ("generate_m2_mesh_runbook.py",
         "When docs change",
         "Rebuild the non-technical runbook PDF."),
        ("generate_m2_mesh_cheatsheet.py",
         "When docs change",
         "Rebuild the 1-page operator cheatsheet."),
        ("generate_m2_mesh_connection_card.py",
         "When docs change",
         "Rebuild T114 device checkout cards (8 nodes, 4 pages)."),
    ]
    for i, (scr, when, what) in enumerate(scripts):
        row_h = 16
        shade = i % 2 == 0
        for cell_text, font, sz, x, w in [
            (scr,  "Mono", 6.5, M,                   col_s),
            (when, "Sans", 7.5, M + col_s,           col_w2),
            (what, "Sans", 7.5, M + col_s + col_w2,  col_d),
        ]:
            c.setFillColor(HexColor("#f0eeee") if shade else WHITE)
            c.setStrokeColor(CARD_BRD)
            c.setLineWidth(0.4)
            c.rect(x, y - row_h, w, row_h, fill=1, stroke=1)
            c.setFont(font, sz)
            c.setFillColor(DARK)
            c.drawString(x + 6, y - 11.5, cell_text)
        y -= row_h
    y = spacer(y, 14)

    # ── SECTION 4: FIRST-TIME SETUP ───────────────────────────────────────────
    y = check_break(c, y, 220, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "First-Time Node Setup", "4.")
    y = body(c, y,
        "Flash and configure each node once. For pre-event PSK rotation, "
        "skip directly to Section 5 — only the config scripts need re-running.")
    y = spacer(y, 8)

    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "T114 Field Nodes × 8  (UF2 drag-and-drop flash)")
    y = spacer(y, 14)

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step A — Download T114 firmware")
    y = spacer(y, 14)
    y = body(c, y,
        "Go to meshtastic.org/downloads. Select Heltec T114. "
        "Download the .uf2 file. No esptool required.", indent=10)

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step B — Enter bootloader mode on each T114")
    y = spacer(y, 14)
    y = body(c, y, "Double-tap the reset button quickly.", indent=10)
    y = body(c, y,
        "A USB drive appears on your computer. "
        "If no drive appears: hold BOOT while plugging in USB.", indent=10)

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step C — Copy firmware to the drive")
    y = spacer(y, 14)
    y = body(c, y,
        "Drag the .uf2 file onto the drive. "
        "The drive disappears and the node reboots automatically.", indent=10)

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step D — Configure all 8 T114 nodes")
    y = spacer(y, 14)
    y = code_block(c, y, ["python meshtastic/scripts/config_m2_t114.py"])
    y = body(c, y,
        "Plug in each T114 via USB-C data cable when prompted. "
        "Script pushes: CommunityNode channel, PSK, US region, LONG_FAST, CLIENT role.")
    y = spacer(y, 10)

    y = check_break(c, y, 160, pages)
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "Heltec LoRa V3 × 2  (esptool flash — rack nodes only)")
    y = spacer(y, 14)

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step E — Flash via esptool")
    y = spacer(y, 14)
    y = body(c, y,
        "Download firmware for Heltec Wireless Tracker V3 from meshtastic.org/downloads "
        "(.bin file). Flash each rack node:", indent=10)
    y = code_block(c, y, [
        "esptool.py --chip esp32s3 --port COM3 write_flash 0x0 firmware-heltec-v3-*.bin",
        "# Replace COM3 with actual port (Device Manager → Ports)",
    ])

    c.setFont("SansBold", 9)
    c.setFillColor(DARK)
    c.drawString(M, y, "Step F — Configure both rack nodes")
    y = spacer(y, 14)
    y = code_block(c, y, ["python meshtastic/scripts/config_heltec_v3.py"])
    y = body(c, y,
        "Plug in each Heltec V3 via USB-C data cable when prompted. "
        "Script pushes: CommunityNode channel, PSK, US region, LONG_FAST, ROUTER role, timezone.")
    y = spacer(y, 10)

    # ── SECTION 5: PRE-EVENT CHECKLIST ────────────────────────────────────────
    y = check_break(c, y, 220, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "Pre-Event Checklist", "5.")
    y = body(c, y,
        "Run before every event. PSK rotation is mandatory — "
        "anyone who scanned the QR at a previous event still holds the old key.")
    y = spacer(y, 8)

    y = callout(c, y, "warn", "PSK Rotation (required before every event)",
        ["Anyone who received the QR at a past event still holds the old key.",
         "Rotate it every event to invalidate previous access.",
         "",
         "Generate:  python -c \"import os,base64; print(base64.b64encode(os.urandom(16)).decode())\"",
         "Paste into CHANNEL_PSK_B64 in: config_heltec_v3.py, config_m2_t114.py, AND gen_m2_channel_qr.py",
         "Save the new PSK to M2_SECRETS.md (z_Backups/ vault) immediately."])
    y = spacer(y, 8)

    checklist = [
        ("1", "Generate new PSK and save."),
        ("2", "Update CHANNEL_PSK_B64 in config_heltec_v3.py, config_m2_t114.py, gen_m2_channel_qr.py"),
        ("3", "Run python meshtastic/scripts/config_heltec_v3.py — plug in each Heltec V3"),
        ("4", "Run python meshtastic/scripts/config_m2_t114.py — plug in each T114"),
        ("5", "Run QR generator — prints to meshtastic/pdf/M2_Mesh_ChannelQR_DayOf.pdf"),
        ("6", "Print 2-up QR cards and cut — bring at least 4 cards to the event"),
        ("7", "Print T114 device checkout cards — meshtastic/pdf/M2_Mesh_DeviceCard_Front.pdf"),
        ("8", "Test on 2 phones: Bluetooth pair → scan QR → confirm CommunityNode visible"),
        ("9", "Verify MQTT bridge is running on Pi 2 before deployment"),
    ]
    for num, text in checklist:
        y = step(c, y, num, text)
    y = spacer(y, 14)

    # ── SECTION 6: TROUBLESHOOTING ────────────────────────────────────────────
    y = check_break(c, y, 200, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "Troubleshooting", "6.")
    y = spacer(y, 8)

    col_p = int(BODY_W * 0.38)
    col_f = BODY_W - col_p
    y = table_header(c, y, [
        ("Problem",      M,          col_p),
        ("Fix",          M + col_p,  col_f),
    ])
    troubles = [
        ("Bootloader drive not appearing after double-tap",
         "Hold BOOT while plugging in USB to force bootloader. Try a different cable."),
        ("T114 stuck in bootloader (drive stays mounted)",
         "Firmware copy may have failed. Re-copy the .uf2 file onto the drive."),
        ("T114 GPS not acquiring fix",
         "Move outdoors. GPS cold start takes 2-5 min. E-ink shows GPS icon when locked."),
        ("No serial port after plugging in Heltec V3",
         "Use a data-capable USB-C cable. Check Device Manager for port assignment."),
        ("config_heltec_v3.py finds no port",
         "Install CH340 or CP2102 USB driver. Try a different USB port."),
        ("Node not appearing in Meshtastic app",
         "Toggle phone Bluetooth off/on. Force-close app and reopen. Short-press node reset."),
        ("Nodes not routing messages to each other",
         "Confirm both rack nodes show ROUTER role in app. Move closer. Check US region."),
        ("QR scan does nothing in app",
         "Update Meshtastic app — older versions cannot import URL-based channels."),
        ("MQTT bridge offline",
         "ssh pi2 — sudo systemctl restart meshtastic-mqtt — check journalctl logs."),
        ("Channel PSK mismatch — nodes can't decrypt",
         "Re-run config_heltec_v3.py, config_m2_t114.py, and gen_m2_channel_qr.py."),
        ("Heltec V3 firmware needs update",
         "Download latest .bin from meshtastic.org/downloads. Re-flash via esptool."),
        ("Node boots but no OLED display",
         "Expected in some firmware builds — verify via Meshtastic app over Bluetooth."),
    ]
    for i, (prob, fix) in enumerate(troubles):
        y = table_row(c, y, [
            (prob, M,          col_p),
            (fix,  M + col_p,  col_f),
        ], shade=(i % 2 == 0))
    y = spacer(y, 14)

    # ── SECTION 7: REPLACING A NODE ──────────────────────────────────────────
    y = check_break(c, y, 150, pages)
    rule(c, M, y, BODY_W)
    y = spacer(y, 22)
    y = h1(c, y, "Replacing a Node", "7.")
    y = body(c, y,
        "If a node is lost or damaged, the replacement gets a new permanent node ID. "
        "Update documentation to keep the operator reference accurate.")
    y = spacer(y, 8)

    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "Replacing a T114 Field Node  (MF-1 through MF-8)")
    y = spacer(y, 14)
    t114_replace = [
        ("1", "Flash firmware via UF2 (see Section 4, Steps A-C)"),
        ("2", "Run config_m2_t114.py — assign the same slot number as the replaced node"),
        ("3", "Verify new node appears in Meshtastic app with correct name (MF-x)"),
        ("4", "Update device checkout card label if node number changes"),
    ]
    for num, text in t114_replace:
        y = step(c, y, num, text)
    y = spacer(y, 10)

    y = check_break(c, y, 120, pages)
    c.setFont("SansBold", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, "Replacing a Heltec V3 Rack Node  (M2-1 or M2-2)")
    y = spacer(y, 14)
    heltec_replace = [
        ("1", "Flash firmware via esptool (see Section 4, Step E)"),
        ("2", "Connect via USB — run config_heltec_v3.py for the replacement slot"),
        ("3", "Verify new node in Meshtastic app and confirm it appears in the node list"),
        ("4", "Reconnect to Pi 2 USB and verify MQTT bridge picks up the new node ID"),
        ("5", "Rebuild this handoff PDF — python meshtastic/scripts/generate_m2_mesh_handoff.py"),
    ]
    for num, text in heltec_replace:
        y = step(c, y, num, text)

    draw_footer(c)
    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
