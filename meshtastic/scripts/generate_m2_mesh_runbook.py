"""
M2 Community Node — Meshtastic Device Runbook
Non-technical guide: initial setup, pre-event workflow, troubleshooting.
Written for node operators who may not have a technical background.

Output: meshtastic/pdf/M2_Mesh_Runbook.pdf

Usage: python meshtastic/scripts/generate_m2_mesh_runbook.py
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
OUTPUT      = os.path.join(_script_dir, "../pdf/M2_Mesh_Runbook.pdf")

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
LIGHT_YE  = HexColor("#fffbea")
WHITE     = HexColor("#ffffff")
GREEN     = HexColor("#1a7a3a")
AMBER     = HexColor("#b7770d")

W, H   = letter
M      = 40
HDR_H  = 54
FTR_H  = 22
TOP_Y  = H - HDR_H - 14
BOT_Y  = FTR_H + 10
BODY_W = W - 2 * M

_logo_path = os.path.join(ASSETS, "lfhi-logo.png")


def draw_header(c, page_num):
    c.setFillColor(ACCENT)
    c.rect(0, H - HDR_H, W, HDR_H, fill=1, stroke=0)
    if os.path.exists(_logo_path):
        c.drawImage(_logo_path, M, H - HDR_H + 9, 36, 36, preserveAspectRatio=True)
    c.setFont("BigShoulders", 20)
    c.setFillColor(WHITE)
    c.drawString(M + 44, H - 30, "M2 COMMUNITY NODE")
    c.setFont("Sans", 9)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(M + 44, H - 46, "Meshtastic Device Runbook")
    c.setFont("JuraMed", 9)
    c.setFillColor(WHITE)
    c.drawRightString(W - M, H - 30, "Emergency Setup & Recovery Guide")
    c.setFont("Sans", 8)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawRightString(W - M, H - 46, f"Page {page_num}")


def draw_footer(c):
    c.setFillColor(HexColor("#1a1a1a"))
    c.rect(0, 0, W, FTR_H, fill=1, stroke=0)
    c.setFont("Sans", 7)
    c.setFillColor(HexColor("#666666"))
    c.drawString(M, 8, "M2 Community Node  —  Internal Use Only")
    c.drawRightString(W - M, 8, "lightfighterhomefront.org  |  meshtastic.org")


def rule(c, x, y, w, col=None, lw=0.5):
    c.setStrokeColor(col or CARD_BRD)
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)


def section_title(c, y, num, text):
    c.setFont("JuraMed", 9)
    c.setFillColor(ACCENT)
    c.drawString(M, y, f"SECTION {num}")
    c.setFont("BigShoulders", 20)
    c.setFillColor(ACCENT)
    offset = c.stringWidth(f"SECTION {num}  ", "JuraMed", 9)
    c.drawString(M + offset, y, text.upper())
    rule(c, M, y - 6, BODY_W, col=ACCENT, lw=1.5)
    return y - 26


def body(c, y, text, indent=0, col=None):
    c.setFont("Sans", 9.5)
    c.setFillColor(col or DARK)
    words = text.split()
    lines = []; line = []
    max_w = BODY_W - indent
    for w in words:
        test = " ".join(line + [w])
        if c.stringWidth(test, "Sans", 9.5) <= max_w:
            line.append(w)
        else:
            lines.append(" ".join(line)); line = [w]
    if line:
        lines.append(" ".join(line))
    for ln in lines:
        c.drawString(M + indent, y, ln)
        y -= 14
    return y - 2


def step_block(c, y, num, heading, sub_lines=None):
    # Numbered step with big circle badge
    circle_r = 14
    cx = M + circle_r
    cy = y - circle_r
    c.setFillColor(ACCENT)
    c.circle(cx, cy, circle_r, fill=1, stroke=0)
    c.setFont("BigShoulders", 16)
    c.setFillColor(WHITE)
    c.drawCentredString(cx, cy - 6, str(num))

    # Heading text
    c.setFont("SansBold", 11)
    c.setFillColor(DARK)
    c.drawString(M + circle_r * 2 + 10, y - 10, heading)

    y -= circle_r * 2 + 6

    if sub_lines:
        for line in sub_lines:
            c.setFont("Mono", 7.5)
            c.setFillColor(MUTED)
            c.drawString(M + 8, y, "  →  " + line)
            y -= 13
    return y - 4


def code_block(c, y, lines):
    bh = len(lines) * 14 + 12
    c.setFillColor(HexColor("#1e1e1e"))
    c.roundRect(M, y - bh, BODY_W, bh, 3, fill=1, stroke=0)
    ty = y - 11
    for line in lines:
        c.setFont("Mono", 8.5)
        c.setFillColor(HexColor("#00ff88"))
        c.drawString(M + 12, ty, line)
        ty -= 14
    return y - bh - 10


def callout(c, y, kind, heading, lines):
    styles = {
        "warn":  (LIGHT_YE,  HexColor("#e6a817"), AMBER),
        "info":  (LIGHT_BL,  HexColor("#2e6cc7"), HexColor("#1a3a7a")),
        "green": (LIGHT_GR,  GREEN,               GREEN),
    }
    bg, border_col, head_col = styles[kind]
    bh = 18 + len(lines) * 14 + 8
    c.setFillColor(bg)
    c.setStrokeColor(CARD_BRD)
    c.setLineWidth(0.5)
    c.roundRect(M, y - bh, BODY_W, bh, 3, fill=1, stroke=1)
    c.setStrokeColor(border_col)
    c.setLineWidth(3)
    c.line(M + 1.5, y - bh + 2, M + 1.5, y - 2)
    c.setFont("SansBold", 9.5)
    c.setFillColor(head_col)
    c.drawString(M + 12, y - 14, heading)
    ty = y - 28
    for ln in lines:
        c.setFont("Sans", 8.5)
        c.setFillColor(DARK)
        c.drawString(M + 12, ty, ln)
        ty -= 14
    return y - bh - 10


def two_col_table(c, y, headers, rows, widths):
    hh = 18
    for i, (hdr, x, w) in enumerate(zip(headers, _x_positions(M, widths), widths)):
        c.setFillColor(ACCENT)
        c.rect(x, y - hh, w, hh, fill=1, stroke=0)
        c.setFont("SansBold", 8.5)
        c.setFillColor(WHITE)
        c.drawString(x + 6, y - 13, hdr)
    y -= hh
    xs = _x_positions(M, widths)
    for ri, row in enumerate(rows):
        rh = 18
        for i, (text, x, w) in enumerate(zip(row, xs, widths)):
            c.setFillColor(HexColor("#f0eeee") if ri % 2 == 0 else WHITE)
            c.setStrokeColor(CARD_BRD)
            c.setLineWidth(0.4)
            c.rect(x, y - rh, w, rh, fill=1, stroke=1)
            c.setFont("Sans", 8.5)
            c.setFillColor(DARK)
            c.drawString(x + 6, y - 13, text)
        y -= rh
    return y - 6


def _x_positions(start, widths):
    xs = [start]
    for w in widths[:-1]:
        xs.append(xs[-1] + w)
    return xs


def spacer(y, n=12):
    return y - n


def check_break(c, y, needed, pages):
    if y - needed < BOT_Y:
        draw_footer(c)
        c.showPage()
        pages[0] += 1
        draw_header(c, pages[0])
        draw_footer(c)
        return TOP_Y - 18
    return y


def build():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)
    pages = [1]

    draw_header(c, 1)
    draw_footer(c)
    y = TOP_Y

    # ── WHO THIS IS FOR ───────────────────────────────────────────────────────
    y = callout(c, y, "info", "Who this document is for",
        ["This runbook covers the M2 Meshtastic nodes from first-time setup through",
         "replacing a broken unit. No deep technical background required.",
         "Read each section fully before starting. If something goes wrong, every error has a fix listed.",
         "M2 runs 2 rack-mounted Heltec V3 ROUTER nodes plus 8 Heltec T114 CLIENT loan devices."])
    y = spacer(y, 8)
    y = body(c, y,
        "The M2 mesh network provides off-grid radio communications at any event or deployment. "
        "Two infrastructure nodes in the rack relay messages between phones and the MQTT bridge. "
        "Eight T114 field nodes are loaned to attendees — each connects over LoRa to the rack nodes. "
        "Attendees join the channel by scanning a QR code. No cell service or internet required.")
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 1: WHAT YOU NEED ──────────────────────────────────────────────
    y = check_break(c, y, 200, pages)
    y = section_title(c, y, "1", "What You Need")
    y = spacer(y, 6)
    y = two_col_table(c, y,
        ["Item", "Notes"],
        [
            ["8× Heltec T114 nodes",                      "MF-1 through MF-8 — loan devices"],
            ["8× USB-C data cables",                      "Must be data cables — charge-only will not work"],
            ["Windows or Linux PC with project folder",   r"C:\SOURCE CONTROL\M2-Community-Node"],
            ["T114 firmware .uf2 file",                   "Download from meshtastic.org/downloads — Heltec T114"],
            ["Python 3.12 + dependencies installed",      "pip install meshtastic pyserial qrcode[pil] reportlab"],
            ["M2_SECRETS.md",                             "For recording and rotating the PSK"],
        ],
        [int(BODY_W * 0.45), int(BODY_W * 0.55)])
    y = callout(c, y, "warn", "Data cable vs. charge-only cable",
        ["If the config script says 'No port detected' after plugging in a node,",
         "the cable is probably charge-only. Try a different cable.",
         "USB-C cables included with laptops and wall chargers are often charge-only."])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 2: FLASH FIRMWARE ─────────────────────────────────────────────
    y = check_break(c, y, 220, pages)
    y = section_title(c, y, "2", "Flash Firmware — T114 Field Nodes  (do once per node)")
    y = spacer(y, 6)
    y = body(c, y,
        "T114 uses a UF2 bootloader — no terminal or esptool needed. "
        "The node appears as a USB drive when in bootloader mode. "
        "Copy the firmware file onto the drive and it installs itself.")
    y = spacer(y, 8)

    y = step_block(c, y, 1, "Download T114 firmware from meshtastic.org/downloads",
        ["Select: Heltec T114",
         "Download the .uf2 file"])
    y = step_block(c, y, 2, "Enter bootloader mode on the T114",
        ["Double-tap the reset button quickly",
         "A USB drive appears on your computer",
         "If no drive appears: hold BOOT while plugging in USB"])
    y = check_break(c, y, 160, pages)
    y = step_block(c, y, 3, "Copy the firmware to the drive",
        ["Drag the .uf2 file onto the drive",
         "Drive disappears automatically — node reboots with Meshtastic installed"])
    y = step_block(c, y, 4, "Repeat for all 8 T114 nodes  (MF-1 through MF-8)")
    y = callout(c, y, "green", "How you know it worked",
        ["T114 E-ink screen shows the Meshtastic logo after reboot.",
         "Each node is visible in the Meshtastic app over Bluetooth."])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 3: CONFIGURE NODES ────────────────────────────────────────────
    y = check_break(c, y, 220, pages)
    y = section_title(c, y, "3", "Configure Nodes")
    y = spacer(y, 6)
    y = callout(c, y, "info", "Flash vs. Configure — two completely different operations",
        ["FLASH  (Section 2) — installs Meshtastic on the hardware. Done once per node, ever.",
         "       Never flash again unless doing a firmware upgrade.",
         "",
         "CONFIGURE  (this section) — sets the channel name, PSK, role, and name.",
         "           Run this before every event to rotate the PSK. No reflashing."])
    y = spacer(y, 8)
    y = callout(c, y, "warn", "PSK must be rotated before every event",
        ["Anyone who scanned the QR at a past event still holds the old key.",
         "Generate new key:  python -c \"import os,base64; print(base64.b64encode(os.urandom(16)).decode())\"",
         "Paste into CHANNEL_PSK_B64 in: config_m2_t114.py, config_heltec_v3.py, AND gen_m2_channel_qr.py",
         "Save the new PSK to M2_SECRETS.md before running the script."])
    y = spacer(y, 8)

    y = step_block(c, y, 1, "Run the T114 config script")
    y = code_block(c, y, ["python meshtastic/scripts/config_m2_t114.py"])
    y = step_block(c, y, 2, "For each of the 8 T114 nodes — in slot order (MF-1 through MF-8):",
        ["Script prompts: '[1/8] Plug in node for: M2 Field Node 01'",
         "Plug in the matching T114 via USB-C data cable",
         "Press Enter — script pushes the PSK, channel, name, and role",
         "Wait for '[OK] M2 Field Node 01 configured.'",
         "Unplug and label. Repeat for MF-2 through MF-8."])
    y = callout(c, y, "green", "How you know it worked",
        ["Terminal shows: [OK] M2 Field Node 01 configured.",
         "Meshtastic app shows the node with channel name CommunityNode."])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── PAGE BREAK BEFORE SECTION 4 ───────────────────────────────────────────
    y = check_break(c, y, 300, pages)

    # ── SECTION 4: GENERATE QR CARD ───────────────────────────────────────────
    y = section_title(c, y, "4", "Generate the Day-Of QR Card")
    y = spacer(y, 6)
    y = body(c, y,
        "The QR card lets attendees join the CommunityNode channel by scanning with their phone. "
        "Generate a fresh card after every PSK rotation.")
    y = spacer(y, 8)

    y = step_block(c, y, 1, "Run the QR generator")
    y = code_block(c, y, ["python meshtastic/scripts/gen_m2_channel_qr.py"])
    y = step_block(c, y, 2, "Print the output file",
        ["Open: meshtastic/pdf/M2_Mesh_ChannelQR_DayOf.pdf",
         "Print at 100% actual size — do NOT scale to fit",
         "Cut on the dashed line — you get 2 identical cards per sheet",
         "Place one at check-in. Give one to the lead organizer."])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 5: PRINT CONNECTION CARDS ────────────────────────────────────
    y = check_break(c, y, 160, pages)
    y = section_title(c, y, "5", "Print Attendee Connection Cards")
    y = spacer(y, 6)
    y = body(c, y,
        "Device checkout cards are front+back cards for each T114 loan node (MF-1 through MF-8). "
        "Print once, laminate, and reuse. Reprint only if node info or instructions change.")
    y = spacer(y, 8)

    y = step_block(c, y, 1, "Generate the cards")
    y = code_block(c, y, ["python meshtastic/scripts/generate_m2_mesh_connection_card.py"])
    y = step_block(c, y, 2, "Print double-sided",
        ["Open: meshtastic/pdf/M2_Mesh_DeviceCard_Front.pdf (front) + Back.pdf (back)",
         "Print at 100% — cut on crop marks — 2 cards per sheet",
         "Laminate each card for durability"])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 6: REPLACING A NODE ───────────────────────────────────────────
    y = check_break(c, y, 180, pages)
    y = section_title(c, y, "6", "Replacing a Broken Node")
    y = spacer(y, 6)
    y = body(c, y,
        "If a T114 is lost or damaged, replace it with any spare T114 unit. "
        "Flash and configure it to match the slot of the broken node.")
    y = spacer(y, 8)

    y = two_col_table(c, y,
        ["Step", "What to do"],
        [
            ["1. Flash firmware",        "UF2 drag-and-drop (Section 2) — just the 1 replacement node"],
            ["2. Configure it",          "python meshtastic/scripts/config_m2_t114.py — select its slot"],
            ["3. Verify in app",         "Node should appear as MF-x in Meshtastic app over Bluetooth"],
            ["4. Update device card",    "Label the replacement with its assigned slot number"],
        ],
        [int(BODY_W * 0.28), int(BODY_W * 0.72)])
    rule(c, M, y, BODY_W)
    y = spacer(y, 24)

    # ── SECTION 7: TROUBLESHOOTING ────────────────────────────────────────────
    y = check_break(c, y, 250, pages)
    y = section_title(c, y, "7", "Troubleshooting")
    y = spacer(y, 6)

    troubles = [
        ("Bootloader drive not appearing",
         "Hold BOOT while plugging in USB to force bootloader. Try a different cable."),
        ("T114 stuck in bootloader (drive stays mounted)",
         "Firmware copy may have failed. Re-copy the .uf2 file onto the drive."),
        ("T114 GPS not acquiring fix",
         "Move outdoors. GPS cold start takes 2-5 min. E-ink shows lock icon."),
        ("'No port detected' after plugging in T114",
         "Use a data-capable USB-C cable. Try a different USB port."),
        ("pip install errors",
         "pip install meshtastic pyserial qrcode[pil] Pillow reportlab"),
        ("App can't find node in Bluetooth scan",
         "Short-press reset. Toggle phone Bluetooth off and back on. Reopen app."),
        ("Nodes not messaging each other",
         "Confirm all show CommunityNode channel and same PSK. Move nodes closer."),
        ("QR scan does nothing",
         "Update Meshtastic app — older builds can't import URL channels."),
        ("Config script pushed wrong name to a node",
         "Re-run config_m2_t114.py and redo only the affected slot."),
        ("T114 E-ink screen stays blank after reboot",
         "E-ink refresh takes 10-15 seconds. Wait, then verify in app."),
    ]
    y = two_col_table(c, y,
        ["Problem", "Fix"],
        troubles,
        [int(BODY_W * 0.38), int(BODY_W * 0.62)])
    y = spacer(y, 14)

    # ── SECTION 8: QUICK REFERENCE ────────────────────────────────────────────
    y = check_break(c, y, 500, pages)
    y = section_title(c, y, "8", "Quick Reference — Full Workflow")
    y = spacer(y, 6)
    y = two_col_table(c, y,
        ["Command", "Purpose"],
        [
            ["python meshtastic/scripts/config_m2_t114.py",
             "Push PSK, channel, name, and role to all 8 T114 field nodes"],
            ["python meshtastic/scripts/gen_m2_channel_qr.py",
             "Generate the day-of QR card for attendees"],
            ["python meshtastic/scripts/generate_m2_mesh_connection_card.py",
             "Generate T114 device checkout cards (8 nodes, front+back)"],
            ["python meshtastic/scripts/generate_m2_mesh_handoff.py",
             "Rebuild the operator handoff reference PDF"],
            ["python meshtastic/scripts/generate_m2_mesh_runbook.py",
             "Rebuild this runbook PDF"],
            ["python meshtastic/scripts/generate_m2_mesh_cheatsheet.py",
             "Rebuild the 1-page operator cheatsheet"],
        ],
        [int(BODY_W * 0.48), int(BODY_W * 0.52)])
    y = spacer(y, 8)

    y = callout(c, y, "green", "Normal pre-event checklist (nodes already configured from a prior event)",
        ["1. Generate new PSK — save to M2_SECRETS.md",
         "2. Update CHANNEL_PSK_B64 in config_m2_t114.py, config_heltec_v3.py, AND gen_m2_channel_qr.py",
         "3. Push new config to T114 nodes — python meshtastic/scripts/config_m2_t114.py",
         "4. Regenerate QR card — python meshtastic/scripts/gen_m2_channel_qr.py",
         "5. Print QR cards — meshtastic/pdf/M2_Mesh_ChannelQR_DayOf.pdf",
         "6. Test 2 phones: Bluetooth pair → scan QR → send message",
         "7. Verify MQTT bridge running on Pi 2 before deployment"])

    draw_footer(c)
    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
