"""
M2 Community Node — Mesh Operator Cheatsheet (1-page)
Pre-event + day-of + post-event quick reference for node operators.

Output: ../pdf/M2_Mesh_Cheatsheet.pdf

Usage: python community-outreach/scripts/generate_m2_mesh_cheatsheet.py
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
OUTPUT      = os.path.join(_script_dir, "../pdf/M2_Mesh_Cheatsheet.pdf")

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
LIGHT_BL  = HexColor("#e8f0fb")
LIGHT_GR  = HexColor("#e8f7ed")
WHITE     = HexColor("#ffffff")
GREEN     = HexColor("#1a7a3a")
BLUE      = HexColor("#1a4a8a")

W, H = letter
M    = 28


def rule(c, x, y, w, col=None, lw=0.5):
    c.setStrokeColor(col or CARD_BRD)
    c.setLineWidth(lw)
    c.line(x, y, x + w, y)


def section_hdr(c, x, y, w, text, bg=None, text_col=None):
    bh = 20
    c.setFillColor(bg or LIGHT_ACC)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.rect(x, y - bh, w, bh, fill=1, stroke=0)
    c.line(x, y, x + w, y)
    c.setFont("JuraMed", 9)
    c.setFillColor(text_col or ACCENT)
    c.drawString(x + 8, y - 14, text.upper())
    return y - bh


def check_row(c, x, y, w, label, note="", col=None):
    c.setFillColor(col or ACCENT)
    c.rect(x + 6, y - 7, 8, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Sans", 7)
    c.drawCentredString(x + 10, y - 5.5, "□")
    c.setFillColor(DARK)
    c.setFont("SansBold", 8.5)
    c.drawString(x + 20, y - 1, label)
    if note:
        c.setFont("Sans", 7.5)
        c.setFillColor(MUTED)
        c.drawString(x + 20, y - 11, note)
    rule(c, x + 18, y - 14, w - 22, col=HexColor("#eeeeee"))
    return y - (22 if note else 17)


def code_block(c, x, y, w, lines):
    bh = len(lines) * 12 + 10
    c.setFillColor(HexColor("#1e1e1e"))
    c.roundRect(x, y - bh, w, bh, 2, fill=1, stroke=0)
    ty = y - 9
    for line in lines:
        c.setFont("Mono", 7.5)
        c.setFillColor(HexColor("#00ff88"))
        c.drawString(x + 8, ty, line)
        ty -= 12
    return y - bh - 4


def trouble_row(c, x, y, w, problem, fix):
    col_split = int(w * 0.42)
    c.setFillColor(HexColor("#f5f0f0"))
    c.rect(x, y - 26, col_split, 26, fill=1, stroke=0)
    c.setFont("SansBold", 7.5)
    c.setFillColor(DARK)
    # wrap problem text
    words = problem.split()
    lines = []; line = []
    for w_ in words:
        test = " ".join(line + [w_])
        if c.stringWidth(test, "SansBold", 7.5) <= col_split - 12:
            line.append(w_)
        else:
            lines.append(" ".join(line)); line = [w_]
    if line:
        lines.append(" ".join(line))
    ty = y - 8
    for ln in lines[:2]:
        c.drawString(x + 6, ty, ln); ty -= 10

    c.setFont("Sans", 7.5)
    c.setFillColor(MUTED)
    words2 = fix.split()
    lines2 = []; line2 = []
    for w_ in words2:
        test = " ".join(line2 + [w_])
        if c.stringWidth(test, "Sans", 7.5) <= w - col_split - 14:
            line2.append(w_)
        else:
            lines2.append(" ".join(line2)); line2 = [w_]
    if line2:
        lines2.append(" ".join(line2))
    ty2 = y - 8
    for ln in lines2[:2]:
        c.drawString(x + col_split + 6, ty2, ln); ty2 -= 10

    rule(c, x, y - 26, w, col=HexColor("#e0d8d8"))
    return y - 28


def build():
    logo_path = os.path.join(ASSETS, "lfhi-logo.png")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    c = rl_canvas.Canvas(OUTPUT, pagesize=letter)

    # ── HEADER BAND ──────────────────────────────────────────────────────────
    c.setFillColor(ACCENT)
    c.rect(0, H - 54, W, 54, fill=1, stroke=0)
    if os.path.exists(logo_path):
        c.drawImage(logo_path, M, H - 50, 40, 40, preserveAspectRatio=True)
    c.setFont("BigShoulders", 22)
    c.setFillColor(WHITE)
    c.drawString(M + 48, H - 28, "M2 COMMUNITY NODE")
    c.setFont("Sans", 9)
    c.setFillColor(HexColor("#ffcccc"))
    c.drawString(M + 48, H - 44, "Meshtastic Operator Cheatsheet")
    c.setFont("JuraMed", 9)
    c.setFillColor(WHITE)

    # ── TWO COLUMN LAYOUT ─────────────────────────────────────────────────────
    col_gap  = 18
    col_w    = (W - 2 * M - col_gap) / 2
    left_x   = M
    right_x  = M + col_w + col_gap
    top_y    = H - 54 - 12

    # ══════════════ LEFT COLUMN ══════════════
    y = top_y
    y = section_hdr(c, left_x, y, col_w, "PRE-EVENT  (24–48 hrs before)")
    y -= 6

    # Info callout
    c.setFillColor(LIGHT_BL)
    c.setStrokeColor(HexColor("#2e6cc7"))
    c.setLineWidth(2)
    blk_h = 42
    c.rect(left_x, y - blk_h, col_w, blk_h, fill=1, stroke=0)
    c.line(left_x, y, left_x, y - blk_h)
    c.setFont("SansBold", 8)
    c.setFillColor(HexColor("#1a3a7a"))
    c.drawString(left_x + 8, y - 11, "Node already configured? Skip flash/discover steps.")
    c.setFont("Sans", 7.5)
    c.setFillColor(MUTED)
    c.drawString(left_x + 8, y - 22, "You only need to rotate the PSK and regenerate the QR.")
    c.drawString(left_x + 8, y - 33, "Config takes ~5 min. Do it at least 24 hrs before the event.")
    y -= blk_h + 8

    y = check_row(c, left_x, y, col_w, "Rotate PSK")
    y = check_row(c, left_x, y, col_w,
        "Update PSK in both scripts",
        "CHANNEL_PSK_B64 in config_heltec_v3.py AND gen_m2_channel_qr.py")

    y -= 4
    y = code_block(c, left_x, y, col_w,
        ["python scripts/config_heltec_v3.py"])
    y -= 2
    y = code_block(c, left_x, y, col_w,
        ["python scripts/gen_m2_channel_qr.py"])
    y -= 4

    y = check_row(c, left_x, y, col_w,
        "Print QR cards",
        "community-outreach/pdf/M2_Mesh_ChannelQR_DayOf.pdf — 2 per sheet")
    y = check_row(c, left_x, y, col_w,
        "Print connection cards",
        "M2_Mesh_Connection_Card.pdf — laminate for reuse")
    y = check_row(c, left_x, y, col_w, "Save New PSK")
    y = check_row(c, left_x, y, col_w,
        "Test 2 phones on the channel",
        "Pair via Bluetooth, scan QR, send a message")
    y = check_row(c, left_x, y, col_w,
        "Verify MQTT bridge is running on Pi 2",
        "sudo systemctl status meshtastic-mqtt")
    y -= 8

    y = section_hdr(c, left_x, y, col_w, "POST-EVENT")
    y -= 6
    y = check_row(c, left_x, y, col_w, "Note any hardware issues or node resets")
    y = check_row(c, left_x, y, col_w,
        "Archive event PSK to M2_SECRETS.md",
        "Mark as expired — never reuse")
    y = check_row(c, left_x, y, col_w, "Verify both nodes reporting to MQTT")
    y = check_row(c, left_x, y, col_w,
        "Update handoff PDF if config changed",
        "python meshtastic/scripts/generate_m2_mesh_handoff.py")

    # ══════════════ RIGHT COLUMN ══════════════
    y = top_y
    y = section_hdr(c, right_x, y, col_w, "DAY-OF")
    y -= 6
    y = check_row(c, right_x, y, col_w,
        "Set out QR cards at check-in",
        "Scan yours first — confirm CommunityNode appears in app")
    y = check_row(c, right_x, y, col_w,
        "Brief new users",
        "App → Bluetooth → scan QR → set name → message")
    y = check_row(c, right_x, y, col_w,
        "Confirm both M2-1 and M2-2 are routing",
        "Meshtastic app → Nodes — both should show recent heartbeat")
    y = check_row(c, right_x, y, col_w,
        "Note who is on the channel",
        "Confirm organizers have working radios before dispersing")
    y -= 8

    y = section_hdr(c, right_x, y, col_w, "WHEN SOMETHING BREAKS")
    y -= 8

    # Trouble table header
    col_split = int(col_w * 0.42)
    c.setFillColor(ACCENT)
    c.rect(right_x, y - 18, col_w, 18, fill=1, stroke=0)
    c.setFont("SansBold", 8)
    c.setFillColor(WHITE)
    c.drawString(right_x + 6, y - 13, "Problem")
    c.drawString(right_x + col_split + 6, y - 13, "Fix")
    y -= 18

    troubles = [
        ("App won't connect to node", "Toggle BT off/on, force-close app, reopen"),
        ("Nodes not routing messages", "Check both show in app node list, move closer"),
        ("QR scan does nothing", "Update Meshtastic app — older versions can't import"),
        ("Channel PSK mismatch", "Re-run config_heltec_v3.py and gen_m2_channel_qr.py"),
        ("Node offline in MQTT", "ssh pi2 — sudo systemctl restart meshtastic-mqtt"),
        ("Node won't boot", "Hold PWR 3s. Check USB power. Reflash if needed."),
        ("GPS no fix", "Nodes have no built-in GPS — use phone location in app"),
        ("Can't find node in BT scan", "Short press reset. Toggle phone BT off/on."),
    ]
    for prob, fix in troubles:
        y = trouble_row(c, right_x, y, col_w, prob, fix)

    y -= 10

    y = section_hdr(c, right_x, y, col_w, "QUICK COMMANDS")
    y -= 6
    cmd_pairs = [
        ("python meshtastic/scripts/config_heltec_v3.py",            "Push PSK + config to both nodes"),
        ("python meshtastic/scripts/gen_m2_channel_qr.py",           "Regenerate day-of QR card"),
        ("python meshtastic/scripts/generate_m2_mesh_handoff.py",     "Rebuild handoff PDF"),
        ("python meshtastic/scripts/generate_m2_mesh_cheatsheet.py",  "Rebuild this cheatsheet"),
        ("python meshtastic/scripts/generate_m2_mesh_runbook.py",     "Rebuild runbook PDF"),
    ]
    for cmd, desc in cmd_pairs:
        c.setFont("Mono", 6.5)
        c.setFillColor(HexColor("#333333"))
        c.drawString(right_x + 6, y, cmd)
        y -= 10
        c.setFont("Sans", 7)
        c.setFillColor(MUTED)
        c.drawString(right_x + 14, y, desc)
        y -= 12

    # ── FOOTER ────────────────────────────────────────────────────────────────
    c.setFillColor(HexColor("#1a1a1a"))
    c.rect(0, 0, W, 22, fill=1, stroke=0)
    c.setFont("Sans", 7)
    c.setFillColor(HexColor("#666666"))
    c.drawString(M, 8, "M2 Community Node  —  Internal Use Only  —  Rotate PSK before every event")
    c.drawRightString(W - M, 8, "meshtastic.org  |  lightfighterhomefront.org")

    c.save()
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == "__main__":
    build()
