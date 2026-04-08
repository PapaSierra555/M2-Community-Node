"""
M2 Community Node — Rack Wiring & Cable Routing Diagram
Produces: M2_Rack_Wiring_Diagram.pdf

Shows power chain, data routing, RF paths, and EMI separation zones.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "operational-pdfs", "M2_Rack_Wiring_Diagram.pdf")

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
pdfmetrics.registerFont(TTFont("BigShoulders", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans",         f"{FONTS}/InstrumentSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SansBold",     f"{FONTS}/InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SansIt",       f"{FONTS}/InstrumentSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("JuraMed",      f"{FONTS}/Jura-Medium.ttf"))

# ── Brand colours ─────────────────────────────────────────────────────────────
HDR_BAR     = colors.HexColor("#921212")   # red — header bars
MUTED       = colors.HexColor("#4a4a4a")
RULE_COLOR  = colors.HexColor("#dcc8c8")
PINK_SUB    = colors.HexColor("#f5cccc")   # subtitle in header bar
TEXT        = colors.HexColor("#0f0f0f")

# ── Diagram colours (functional — do not change) ──────────────────────────────
BLACK       = colors.HexColor("#0D0D0D")
DARK_GRAY   = colors.HexColor("#1A1A2E")
MID_GRAY    = colors.HexColor("#2D2D44")
LIGHT_GRAY  = colors.HexColor("#E8E8E8")
WHITE       = colors.white
ACCENT      = colors.HexColor("#00B4D8")   # teal — USB cable colour
WARN        = colors.HexColor("#E63946")   # red — warnings

# ── Cable colours (functional) ────────────────────────────────────────────────
PWR_COLOR   = colors.HexColor("#E63946")   # red — AC/DC power
USB_COLOR   = colors.HexColor("#00B4D8")   # teal — USB data/power
ETH_COLOR   = colors.HexColor("#2D6A4F")   # green — Ethernet
RF_COLOR    = colors.HexColor("#FF8C00")   # orange — RF/antenna
HDMI_COLOR  = colors.HexColor("#7B2D8B")   # purple — HDMI
AIR_COLOR   = colors.HexColor("#87CEEB")   # light blue — airflow

# Page dimensions
W, H = letter  # 612 x 792
MARGIN = 0.7 * inch


# ── Shared page chrome ────────────────────────────────────────────────────────

def draw_header(c, title, subtitle):
    """ACCENT header bar matching the other M2 documents."""
    c.setFillColor(HDR_BAR)
    c.rect(0, H - 50, W, 50, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("BigShoulders", 16)
    c.drawCentredString(W / 2, H - 33, title)
    c.setFillColor(PINK_SUB)
    c.setFont("Sans", 9)
    c.drawCentredString(W / 2, H - 46, subtitle)


def draw_footer(c, page_num, section=""):
    """Footer rule + centered doc title + page number — matching other M2 docs."""
    y = MARGIN - 0.16 * inch
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.5)
    c.line(MARGIN, y + 10, W - MARGIN, y + 10)
    c.setFont("Sans", 7.5)
    c.setFillColor(MUTED)
    if section:
        c.drawString(MARGIN, y, section)
    c.drawCentredString(W / 2, y, "M2 Community Node Wiring Diagram v1.0")
    c.drawRightString(W - MARGIN, y, f"Page {page_num}")


def draw_cover_page(c):
    """Title page matching the Runbook, Build Book, and Troubleshooting Guide."""
    # Centered layout
    cx = W / 2
    c.setFillColor(HDR_BAR)
    c.setFont("BigShoulders", 38)
    c.drawCentredString(cx, H / 2 + 110, "M2 COMMUNITY NODE")

    c.setFillColor(MUTED)
    c.setFont("Sans", 18)
    c.drawCentredString(cx, H / 2 + 72, "Rack Wiring & Cable Routing Diagram")

    c.setFont("JuraMed", 11)
    c.drawCentredString(cx, H / 2 + 46, "v1.0  |  April 2026")

    c.setFont("SansIt", 10)
    c.drawCentredString(cx, H / 2 + 24,
                        "Power chain \u00b7 Data routing \u00b7 RF paths \u00b7 EMI separation zones")

    # Rule
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.5)
    c.line(MARGIN * 2, H / 2 + 4, W - MARGIN * 2, H / 2 + 4)

    c.setFillColor(MUTED)
    c.setFont("Sans", 9)
    c.drawCentredString(cx, H / 2 - 10, "CC BY-NC-SA 4.0")
    c.drawCentredString(cx, H / 2 - 24, "yourdomain.com")

    draw_footer(c, 1)


def draw_page1_front_side(c):
    """Page 2: Front view + right-side cross-section with cable routing"""

    draw_header(c, "M2 COMMUNITY NODE — RACK WIRING DIAGRAM",
                "GeeekPi RackMate T1 8U  |  Front View + Side Cross-Section  |  Cable Routing")

    # =========================================================================
    # FRONT VIEW (left half)
    # =========================================================================
    fx, fy = 30, 80  # front view origin (bottom-left of rack)
    fw, fh = 220, 500  # rack width, height (500 leaves room for legend above)
    u_height = fh / 8  # height per U

    # Rack outline
    c.setStrokeColor(BLACK)
    c.setLineWidth(2)
    c.rect(fx, fy, fw, fh)

    # Title
    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(fx + fw/2, fy + fh + 15, "FRONT VIEW (Top-Down)")

    # U1=UPS, U2=PDU(rear), U3=OPEN, U4=Pi Mount, U5=Switch+GL.iNet, U6-U7=Screen, U8=LoRa+Fan
    components = [
        (1, "U1", "Tripp Lite BC600R (UPS)\n10.04\"x7.09\"x2.28\" (~1.3U)", colors.HexColor("#FFF9C4")),
        (2, "U2", "---- OPEN ----\n(PDU on rear rails)", LIGHT_GRAY),
        (3, "U3", "---- OPEN ----\n(future expansion)", LIGHT_GRAY),
        (4, "U4", "GeeekPi Dual Pi 5 Mount\nPi#1 (Comms) | Pi#2 (Tactical)", colors.HexColor("#B3E5FC")),
        (5, "U5", "TL-SG108S + GL.iNet\n(shared 1U shelf)", colors.HexColor("#C8E6C9")),
        (6, "U6", "2U Touchscreen\n(7.84\" LCD)", colors.HexColor("#E1BEE7")),
        (7, "U7", "(continued)", colors.HexColor("#E1BEE7")),
        (8, "U8", "LoRa Panel (front) + Fan (rear)\nHeltec V3 (L) | SMA | Heltec V3 (R)", colors.HexColor("#FFE0B2")),
    ]

    for u_num, label, desc, bg_color in components:
        y = fy + (u_num - 1) * u_height
        # Background
        c.setFillColor(bg_color)
        c.rect(fx + 2, y + 2, fw - 4, u_height - 4, fill=1, stroke=0)
        # Border
        c.setStrokeColor(colors.HexColor("#999999"))
        c.setLineWidth(0.5)
        c.rect(fx + 2, y + 2, fw - 4, u_height - 4, fill=0, stroke=1)
        # U label
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(fx + 6, y + u_height - 14, label)
        # Description
        c.setFont("Helvetica", 7)
        lines = desc.split("\n")
        for i, line in enumerate(lines):
            c.drawString(fx + 30, y + u_height - 14 - i * 10, line)

    # Antenna indicators on front of U8
    u8_y = fy + 7 * u_height
    ant_top = u8_y + u_height - 5  # stay inside rack outline
    # Left antenna — line + label to the right of the line (inside page)
    c.setStrokeColor(RF_COLOR)
    c.setLineWidth(2)
    c.line(fx - 10, u8_y + 15, fx - 10, ant_top)
    c.setFillColor(RF_COLOR)
    c.circle(fx - 10, ant_top, 3, fill=1)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(fx - 28, u8_y + 35, "ANT 1")
    c.setFont("Helvetica", 5)
    c.drawString(fx - 28, u8_y + 27, "RNode(L)")

    # Right antenna
    c.setStrokeColor(RF_COLOR)
    c.line(fx + fw + 10, u8_y + 15, fx + fw + 10, ant_top)
    c.setFillColor(RF_COLOR)
    c.circle(fx + fw + 10, ant_top, 3, fill=1)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(fx + fw + 18, u8_y + 35, "ANT 2")
    c.setFont("Helvetica", 5)
    c.drawString(fx + fw + 18, u8_y + 27, "Mesh(R)")

    # =========================================================================
    # SIDE CROSS-SECTION (right half) — cable routing
    # =========================================================================
    sx, sy = 310, 80  # side view origin
    sw, sh = 260, 500
    su = sh / 8

    c.setStrokeColor(BLACK)
    c.setLineWidth(2)
    c.rect(sx, sy, sw, sh)

    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(sx + sw/2, sy + sh + 15, "SIDE CROSS-SECTION (Cable Routing)")

    # Left side = FRONT of rack, Right side = REAR of rack
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(sx + 5, sy + sh - 18, "\u2190 FRONT")
    c.drawRightString(sx + sw - 5, sy + sh - 18, "REAR \u2192")

    # Draw center divider (component zone)
    comp_x = sx + 60
    comp_w = 120
    c.setStrokeColor(colors.HexColor("#CCCCCC"))
    c.setLineWidth(0.5)
    c.setDash([2, 2])
    c.line(comp_x, sy, comp_x, sy + sh)
    c.line(comp_x + comp_w, sy, comp_x + comp_w, sy + sh)
    c.setDash([])

    # Label zones
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.HexColor("#999999"))
    c.saveState()
    c.translate(sx + 18, sy + sh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "FRONT CABLE CHANNEL")
    c.restoreState()
    c.saveState()
    c.translate(sx + sw - 18, sy + sh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "REAR CABLE CHANNEL")
    c.restoreState()
    c.saveState()
    c.translate(comp_x + comp_w/2, sy + sh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "COMPONENT ZONE (7.87\" depth)")
    c.restoreState()

    # Draw U levels in side view
    for u in range(1, 9):
        y = sy + (u - 1) * su
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.setLineWidth(0.3)
        c.line(sx, y, sx + sw, y)
        c.setFillColor(colors.HexColor("#AAAAAA"))
        c.setFont("Helvetica", 6)
        c.drawString(sx + 2, y + 3, f"U{u}")

    # =====================================================================
    # CABLE ROUTING PATHS (side cross-section)
    # U1=UPS, U2=PDU, U3=open, U4=Pi, U5=Switch, U6-U7=Screen, U8=LoRa+Fan
    # =====================================================================

    # === POWER (RED) — LEFT/FRONT channel ===
    # UPS at U1 -> PDU at U2: ultra-short cable
    pwr_x = sx + 35
    pdu_y = sy + 1 * su + su/2  # U2 center
    ups_y = sy + su/2  # U1 center

    c.setStrokeColor(PWR_COLOR)
    c.setLineWidth(2.5)
    c.line(pwr_x, ups_y, pwr_x, pdu_y)
    c.setFillColor(PWR_COLOR)
    c.circle(pwr_x, pdu_y, 4, fill=1)

    # PDU -> Anker 747
    anker_x = pwr_x + 10
    c.setLineWidth(1.5)
    c.line(pwr_x + 4, pdu_y, anker_x + 15, pdu_y)
    c.line(anker_x + 15, pdu_y, anker_x + 15, pdu_y + 10)

    # PDU -> Switch 12V barrel (U5)
    switch_y = sy + 4 * su + su/2  # U5 center
    c.setStrokeColor(PWR_COLOR)
    c.setLineWidth(1.5)
    c.line(pwr_x, pdu_y, pwr_x - 8, pdu_y)
    c.line(pwr_x - 8, pdu_y, pwr_x - 8, switch_y)
    c.line(pwr_x - 8, switch_y, comp_x, switch_y)

    # Anker -> Pi #1, Pi #2 (USB-C power, runs UP front channel to U4)
    pi_y = sy + 3 * su + su/2  # U4 center
    c.setStrokeColor(USB_COLOR)
    c.setLineWidth(1.5)
    c.setDash([4, 2])
    c.line(pwr_x + 5, pdu_y + 15, pwr_x + 5, pi_y + 10)
    c.line(pwr_x + 5, pi_y + 10, comp_x, pi_y + 10)
    c.line(pwr_x + 12, pdu_y + 15, pwr_x + 12, pi_y - 5)
    c.line(pwr_x + 12, pi_y - 5, comp_x, pi_y - 5)
    c.setDash([])

    # Anker -> GL.iNet (USB-C power, up to U5)
    c.setStrokeColor(USB_COLOR)
    c.setDash([4, 2])
    c.line(pwr_x + 19, pdu_y + 15, pwr_x + 19, switch_y + 8)
    c.line(pwr_x + 19, switch_y + 8, comp_x, switch_y + 8)
    c.setDash([])

    # === ETHERNET (GREEN) — rear channel ===
    eth_x = comp_x + comp_w + 15
    c.setStrokeColor(ETH_COLOR)
    c.setLineWidth(1.5)
    # Switch (U5) to Pi #1 (U4)
    c.line(comp_x + comp_w, switch_y - 3, eth_x, switch_y - 3)
    c.line(eth_x, switch_y - 3, eth_x, pi_y + 5)
    c.line(eth_x, pi_y + 5, comp_x + comp_w, pi_y + 5)
    # Switch to Pi #2
    c.line(comp_x + comp_w, switch_y + 3, eth_x + 8, switch_y + 3)
    c.line(eth_x + 8, switch_y + 3, eth_x + 8, pi_y - 5)
    c.line(eth_x + 8, pi_y - 5, comp_x + comp_w, pi_y - 5)
    # Switch to GL.iNet (same shelf, short patch)
    c.setDash([2, 2])
    c.line(comp_x + comp_w/2 - 20, switch_y + 15, comp_x + comp_w/2 + 20, switch_y + 15)
    c.setDash([])

    # === RF / ANTENNA (ORANGE) — FRONT side, at U8 (top) ===
    rf_x = sx + 10
    lora_y = sy + 7 * su + su/2  # U8 center
    c.setStrokeColor(RF_COLOR)
    c.setLineWidth(2)
    c.line(rf_x, lora_y - 8, comp_x - 5, lora_y - 8)
    c.line(rf_x, lora_y + 8, comp_x - 5, lora_y + 8)
    c.line(rf_x, lora_y - 8, rf_x - 8, lora_y - 8)
    c.line(rf_x - 8, lora_y - 8, rf_x - 8, lora_y)
    c.line(rf_x, lora_y + 8, rf_x + 5, lora_y + 8)
    c.line(rf_x + 5, lora_y + 8, rf_x + 5, lora_y + 3)
    c.setFillColor(RF_COLOR)
    c.circle(rf_x - 8, lora_y, 2, fill=1)
    c.circle(rf_x + 5, lora_y + 3, 2, fill=1)

    # === USB DATA (TEAL, dashed) — Pi #2 (U4) to LoRa boards (U8), 3ft cables ===
    c.setStrokeColor(USB_COLOR)
    c.setLineWidth(1)
    c.setDash([3, 2])
    usb_lora_x = comp_x + comp_w + 35
    c.line(comp_x + comp_w, pi_y - 15, usb_lora_x, pi_y - 15)
    c.line(usb_lora_x, pi_y - 15, usb_lora_x, lora_y + 5)
    c.line(usb_lora_x, lora_y + 5, comp_x + comp_w, lora_y + 5)
    c.line(comp_x + comp_w, pi_y - 20, usb_lora_x + 8, pi_y - 20)
    c.line(usb_lora_x + 8, pi_y - 20, usb_lora_x + 8, lora_y - 5)
    c.line(usb_lora_x + 8, lora_y - 5, comp_x + comp_w, lora_y - 5)
    c.setDash([])

    # === HDMI (PURPLE) — Pi #1 (U4) to Touchscreen (U6-U7) ===
    hdmi_x = comp_x + comp_w + 30
    screen_y = sy + 5.5 * su  # center of U6-U7
    c.setStrokeColor(HDMI_COLOR)
    c.setLineWidth(1.5)
    c.line(comp_x + comp_w, pi_y + 15, hdmi_x, pi_y + 15)
    c.line(hdmi_x, pi_y + 15, hdmi_x, screen_y)
    c.line(hdmi_x, screen_y, comp_x + comp_w, screen_y)

    # === 80mm FAN USB (rear, U4-U3) ===
    fan_usb_x = sx + sw - 30
    c.setStrokeColor(USB_COLOR)
    c.setLineWidth(1)
    c.setDash([2, 3])
    fan_y = sy + 2.5 * su  # U3-U4 rear center
    c.line(comp_x + comp_w, pi_y - 10, fan_usb_x, pi_y - 10)
    c.line(fan_usb_x, pi_y - 10, fan_usb_x, fan_y)
    c.setDash([])
    c.setFillColor(USB_COLOR)
    c.setFont("Helvetica", 5)
    c.drawString(fan_usb_x - 25, fan_y - 8, "80mm fans")

    # === 120mm FAN (U8 rear) ===
    fan120_x = sx + sw - 25
    c.setStrokeColor(AIR_COLOR)
    c.setLineWidth(1.5)
    fan120_y = sy + 7 * su + su/2
    c.setDash([3, 3])
    c.line(comp_x + comp_w, fan120_y, fan120_x, fan120_y)
    c.setDash([])
    c.setFillColor(AIR_COLOR)
    c.setFont("Helvetica", 5)
    c.drawString(fan120_x - 30, fan120_y + 5, "120mm fan")
    c.drawString(fan120_x - 30, fan120_y - 5, "(U8 rear)")

    # =====================================================================
    # EMI SEPARATION ZONE indicator
    # =====================================================================
    c.setStrokeColor(WARN)
    c.setLineWidth(1)
    c.setDash([5, 3])
    sep_x = pwr_x + 22
    # Show clear zone between PDU (U2) and LoRa (U8) — 6U gap
    c.line(sep_x, sy + 5 * su, sep_x, sy + 7 * su)
    c.setDash([])
    c.setFillColor(WARN)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(sep_x - 35, sy + 5.8 * su, "EMI CLEAR")
    c.drawString(sep_x - 35, sy + 5.6 * su, "(6U gap)")

    # =====================================================================
    # LEGEND
    # =====================================================================
    leg_x, leg_y = 30, H - 80
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(BLACK)
    c.drawString(leg_x, leg_y, "CABLE LEGEND:")

    legends = [
        (PWR_COLOR, "------", "AC Power (UPS U1 -> PDU U2 rear rails; PDU -> Switch 12V barrel U5)", False),
        (USB_COLOR, "- - - ", "USB Power/Data (Anker -> Pi/GL.iNet USB-C, Pi -> LoRa 3ft USB-C, Hub -> Fans)", True),
        (ETH_COLOR, "------", "Ethernet (Switch U5 <-> Pi#1, Pi#2 U4, GL.iNet U5 -- 6\" patches)", False),
        (RF_COLOR,  "------", "RF / Antenna (U.FL pigtails -> SMA bulkheads -> 915 MHz antennas at U8 top)", False),
        (HDMI_COLOR,"------", "HDMI (Pi#1 micro HDMI U4 -> Touchscreen U7, 2ft cable)", False),
    ]

    for i, (color, style, desc, dashed) in enumerate(legends):
        y = leg_y - 14 - i * 12
        c.setStrokeColor(color)
        c.setLineWidth(2)
        if dashed:
            c.setDash([4, 2])
        else:
            c.setDash([])
        c.line(leg_x, y + 3, leg_x + 35, y + 3)
        c.setDash([])
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 7)
        c.drawString(leg_x + 40, y, desc)

    draw_footer(c, 2, "Front View + Side Cross-Section")


def draw_page2_power_chain(c):
    """Page 3: Complete power chain diagram + EMI analysis"""

    draw_header(c, "POWER CHAIN & EMI SEPARATION",
                "Wall -> UPS (U1) -> PDU (U2 rear) -> Devices  |  Cable Routing Rules  |  RF Protection Zones")

    # =========================================================================
    # POWER CHAIN FLOW DIAGRAM
    # =========================================================================
    c.setFillColor(HDR_BAR)
    c.setFont("SansBold", 12)
    c.drawString(40, H - 80, "1. COMPLETE POWER CHAIN")

    chain_y = 470
    box_h = 50
    box_w = 100
    gap = 30

    def power_box(x, y, title, details, color):
        c.setFillColor(color)
        c.roundRect(x, y, box_w, box_h, 5, fill=1, stroke=1)
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + box_w/2, y + box_h - 14, title)
        c.setFont("Helvetica", 6)
        for i, line in enumerate(details):
            c.drawCentredString(x + box_w/2, y + box_h - 26 - i * 9, line)

    def arrow(x1, y, x2):
        c.setStrokeColor(PWR_COLOR)
        c.setLineWidth(2)
        c.line(x1, y, x2, y)
        c.line(x2 - 6, y + 4, x2, y)
        c.line(x2 - 6, y - 4, x2, y)

    x = 20
    gap = 20
    power_box(x, chain_y, "WALL OUTLET", ["120V AC", "15A circuit"], colors.HexColor("#FFCDD2"))
    arrow(x + box_w, chain_y + box_h/2, x + box_w + gap)

    x += box_w + gap
    power_box(x, chain_y, "BC600R UPS (U1)", ["600VA / 300W", "Inside rack, U1", "Battery: 72Wh"], colors.HexColor("#FFF9C4"))
    arrow(x + box_w, chain_y + box_h/2, x + box_w + gap)

    x += box_w + gap
    power_box(x, chain_y, "RACK PDU (U2 rear)", ["4 outlets", "Rear rails, inward", "Adapters on UPS body"], colors.HexColor("#FFCDD2"))

    pdu_right = x + box_w
    pdu_cy = chain_y + box_h/2

    # Outlet 1: Anker 747
    branch1_y = chain_y + 65
    c.setStrokeColor(PWR_COLOR)
    c.setLineWidth(1.5)
    c.line(pdu_right, pdu_cy + 10, pdu_right + 15, pdu_cy + 10)
    c.line(pdu_right + 15, pdu_cy + 10, pdu_right + 15, branch1_y + box_h/2)
    c.line(pdu_right + 15, branch1_y + box_h/2, pdu_right + 20, branch1_y + box_h/2)

    power_box(pdu_right + 20, branch1_y, "ANKER 747 GaN", ["150W, 4xUSB-C", "2xUSB-A", "PDU Outlet 1"], colors.HexColor("#FFE0B2"))

    anker_right = pdu_right + 20 + box_w
    anker_cy = branch1_y + box_h/2

    sub_boxes = [
        ("Pi #1 (U4)", ["USB-C1, 27W", "Comms node"]),
        ("Pi #2 (U4)", ["USB-C2, 27W", "Tactical node"]),
        ("GL.iNet (U5)", ["USB-C3, 15W", "Router"]),
        ("Screen (U7)", ["USB-A1, 8W", "Touchscreen"]),
        ("Fan (U8R)", ["USB-A2, 2W", "120mm exhaust"]),
    ]

    for i, (title, details) in enumerate(sub_boxes):
        by = branch1_y + 55 + i * 28
        bx = anker_right + 18
        c.setStrokeColor(USB_COLOR)
        c.setLineWidth(1)
        c.line(anker_right, anker_cy, anker_right + 10, anker_cy)
        c.line(anker_right + 10, anker_cy, anker_right + 10, by + 12)
        c.line(anker_right + 10, by + 12, bx, by + 12)

        c.setFillColor(colors.HexColor("#E3F2FD"))
        c.roundRect(bx, by, 90, 24, 3, fill=1, stroke=1)
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(bx + 4, by + 13, title)
        c.setFont("Helvetica", 6)
        c.drawString(bx + 4, by + 4, details[0])

    # Outlet 2: Switch
    branch2_y = chain_y - 35
    c.setStrokeColor(PWR_COLOR)
    c.setLineWidth(1.5)
    c.line(pdu_right, pdu_cy - 10, pdu_right + 15, pdu_cy - 10)
    c.line(pdu_right + 15, pdu_cy - 10, pdu_right + 15, branch2_y + box_h/2)
    c.line(pdu_right + 15, branch2_y + box_h/2, pdu_right + 20, branch2_y + box_h/2)

    power_box(pdu_right + 20, branch2_y, "TL-SG108S (U5)", ["12V DC barrel", "3.5W constant", "PDU Outlet 2"], colors.HexColor("#C8E6C9"))

    c.setFillColor(colors.HexColor("#999999"))
    c.setFont("Helvetica", 7)
    c.drawString(pdu_right + 25, branch2_y - 12, "Outlets 3-4: spare")

    # =========================================================================
    # EMI / RF SEPARATION ANALYSIS
    # =========================================================================
    emi_y = 350
    c.setFillColor(HDR_BAR)
    c.setFont("SansBold", 12)
    c.drawString(40, emi_y, "2. EMI SEPARATION ANALYSIS")

    emi_notes = [
        ("GOOD: LoRa at U8 (top), PDU at U2 rear -- 6U (10.5\") vertical separation", "2D6A4F"),
        ("GOOD: LoRa at U8 (top), UPS at U1 -- 7U (12.25\") maximum separation", "2D6A4F"),
        ("GOOD: Power cables concentrated at U1-U2 bottom; RF at U8 top -- opposite ends", "2D6A4F"),
        ("GOOD: AC power cable is shielded (PDU 6ft cord has integral ground)", "2D6A4F"),
        ("GOOD: U.FL pigtails are < 6\" long -- minimal exposure to radiated EMI", "2D6A4F"),
        ("GOOD: 915 MHz LoRa is spread-spectrum (chirp) with ~19 dB noise immunity", "2D6A4F"),
        ("GOOD: USB data cables (Pi U4 -> LoRa U8, 3ft) route via LEFT rail -- away from power", "2D6A4F"),
        ("CAUTION: 3ft USB-C data cables traverse 4U on left rail", "E63946"),
        ("MITIGATION: Route USB data cables tightly along left rail; cross power paths at 90 deg only", "0077B6"),
    ]

    for i, (note, color) in enumerate(emi_notes):
        y = emi_y - 16 - i * 14
        marker = "V" if color == "2D6A4F" else ("!" if color == "E63946" else ">")
        c.setFillColor(colors.HexColor(f"#{color}"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(50, y, marker)
        c.setFont("Helvetica", 8)
        c.drawString(65, y, note)

    # =========================================================================
    # CABLE ROUTING RULES
    # =========================================================================
    rules_y = 175
    c.setFillColor(HDR_BAR)
    c.setFont("SansBold", 12)
    c.drawString(40, rules_y, "3. CABLE ROUTING RULES")

    rules = [
        "LEFT RAIL (rear):   Ethernet patches (6\"), HDMI (2ft, Pi U4 -> Screen U7), fan USB cables",
        "LEFT CHANNEL:       USB-C data cables (Pi#2 U4 -> LoRa boards at U8, 3ft)",
        "RIGHT CHANNEL:      USB-C power cables (Anker -> Pi#1 U4, Pi#2 U4, GL.iNet U5, Screen U7)",
        "RIGHT RAIL (rear):  AC power (PDU 6ft cord U1->U2 rear rails, ultra-short), 12V barrel adapter cable",
        "FRONT PANEL (U8):   RF only -- SMA bulkheads + antennas, OLED windows (TOP of rack)",
        "RULE: Never bundle AC power and RF cables together. Cross at 90 deg only.",
    ]
    for i, rule in enumerate(rules[:-1]):
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 8)
        c.drawString(50, rules_y - 14 - i * 12, rule)

    c.setFillColor(WARN)
    c.setFont("SansBold", 8)
    c.drawString(50, rules_y - 14 - 5 * 12, rules[-1])

    draw_footer(c, 3, "Power Chain & EMI Separation")


def draw_page3_top_down(c):
    """Page 4: Top-down view showing left/right cable separation"""

    draw_header(c, "TOP-DOWN VIEW — CABLE SEPARATION ZONES",
                "Looking down into the rack from U8  |  Data LEFT, Power RIGHT, RF FRONT (U8 top)")

    rx, ry = 80, 220
    rw, rh = 450, 390

    c.setStrokeColor(BLACK)
    c.setLineWidth(2)
    c.rect(rx, ry, rw, rh)

    c.setFillColor(BLACK)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(rx + rw/2, ry + rh + 12, "<- FRONT OF RACK ->")
    c.drawCentredString(rx + rw/2, ry - 15, "<- REAR OF RACK ->")

    c.saveState()
    c.translate(rx - 15, ry + rh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "LEFT RAIL")
    c.restoreState()
    c.saveState()
    c.translate(rx + rw + 15, ry + rh/2)
    c.rotate(-90)
    c.drawCentredString(0, 0, "RIGHT RAIL")
    c.restoreState()

    # Zone: LEFT -- Data cables (teal/green)
    zone_w = 80
    c.setFillColor(colors.HexColor("#E0F7FA"))
    c.rect(rx + 5, ry + 5, zone_w, rh - 10, fill=1, stroke=0)
    c.setStrokeColor(USB_COLOR)
    c.setLineWidth(1)
    c.setDash([4, 2])
    c.rect(rx + 5, ry + 5, zone_w, rh - 10, fill=0, stroke=1)
    c.setDash([])
    c.setFillColor(USB_COLOR)
    c.setFont("Helvetica-Bold", 9)
    c.saveState()
    c.translate(rx + 40, ry + rh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "DATA ZONE")
    c.restoreState()
    c.setFont("Helvetica", 7)
    c.saveState()
    c.translate(rx + 55, ry + rh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "Ethernet / HDMI / USB data (3ft to U8) / Fan USB")
    c.restoreState()

    # Zone: CENTER -- Components
    cz_x = rx + zone_w + 15
    cz_w = rw - 2 * zone_w - 30
    c.setFillColor(colors.HexColor("#F5F5F5"))
    c.rect(cz_x, ry + 5, cz_w, rh - 10, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#999999"))
    c.setLineWidth(0.5)
    c.rect(cz_x, ry + 5, cz_w, rh - 10, fill=0, stroke=1)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cz_x + cz_w/2, ry + rh/2 + 5, "COMPONENTS")
    c.setFont("Helvetica", 7)
    c.drawCentredString(cz_x + cz_w/2, ry + rh/2 - 8, "UPS (U1) / PDU (U2 rear) / Pi nodes (U4) / Switch (U5)")
    c.drawCentredString(cz_x + cz_w/2, ry + rh/2 - 20, "Screen (U6-7) / LoRa + Fan (U8)")

    # Zone: RIGHT -- Power cables (red)
    pz_x = rx + rw - zone_w - 5
    c.setFillColor(colors.HexColor("#FFEBEE"))
    c.rect(pz_x, ry + 5, zone_w, rh - 10, fill=1, stroke=0)
    c.setStrokeColor(PWR_COLOR)
    c.setLineWidth(1)
    c.setDash([4, 2])
    c.rect(pz_x, ry + 5, zone_w, rh - 10, fill=0, stroke=1)
    c.setDash([])
    c.setFillColor(PWR_COLOR)
    c.setFont("Helvetica-Bold", 9)
    c.saveState()
    c.translate(pz_x + 40, ry + rh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "POWER ZONE")
    c.restoreState()
    c.setFont("Helvetica", 7)
    c.saveState()
    c.translate(pz_x + 55, ry + rh/2)
    c.rotate(90)
    c.drawCentredString(0, 0, "PDU cable (U1-U2 rear) / USB-C power / 12V barrel")
    c.restoreState()

    # FRONT zone -- RF at U8
    rf_h = 50
    c.setFillColor(colors.HexColor("#FFF3E0"))
    c.rect(rx + 5, ry + rh - rf_h - 5, rw - 10, rf_h, fill=1, stroke=0)
    c.setStrokeColor(RF_COLOR)
    c.setLineWidth(1.5)
    c.setDash([4, 2])
    c.rect(rx + 5, ry + rh - rf_h - 5, rw - 10, rf_h, fill=0, stroke=1)
    c.setDash([])
    c.setFillColor(RF_COLOR)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(rx + rw/2, ry + rh - 25, "RF ZONE (FRONT PANEL U8 -- TOP OF RACK)")
    c.setFont("Helvetica", 7)
    c.drawCentredString(rx + rw/2, ry + rh - 38, "SMA bulkheads + 915 MHz antennas + U.FL pigtails -- MAX DISTANCE FROM POWER (U1-U2)")

    for ax in [rx + 120, rx + rw - 120]:
        c.setStrokeColor(RF_COLOR)
        c.setLineWidth(2)
        c.line(ax, ry + rh - 5, ax, ry + rh + 30)
        c.setFillColor(RF_COLOR)
        c.circle(ax, ry + rh + 30, 4, fill=1)

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(rx + 120, ry + rh + 40, "ANT 1 — LEFT (RNode)")
    c.drawCentredString(rx + rw - 120, ry + rh + 40, "ANT 2 — RIGHT (Mesh)")

    # REAR zone
    c.setFillColor(colors.HexColor("#ECEFF1"))
    c.rect(rx + 5, ry + 5, rw - 10, 40, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(rx + rw/2, ry + 28, "REAR (120mm fan U8, 80mm fans U4-U3, switch ports, PDU U2 rear rails)")
    c.setFont("Helvetica", 7)
    c.drawCentredString(rx + rw/2, ry + 15, "120mm fan (U8) / 80mm fans (U4-U3) / Ethernet ports / PDU (U2, outlets inward)")

    # Key insight box — height expanded for bottom padding
    box_y = 95
    box_h_key = 92
    c.setFillColor(colors.HexColor("#FFF9C4"))
    c.roundRect(40, box_y, W - 80, box_h_key, 8, fill=1, stroke=1)
    c.setFillColor(BLACK)
    c.setFont("SansBold", 10)
    c.drawString(55, box_y + 73, "KEY ROUTING PRINCIPLE:")
    c.setFont("Sans", 9)
    c.drawString(55, box_y + 57, "Data cables (Ethernet, HDMI, USB data) run on the LEFT rail/channel only.")
    c.drawString(55, box_y + 43, "Power cables (AC + USB-C power) run on the RIGHT rail/channel only.")
    c.drawString(55, box_y + 29, "RF paths (U.FL pigtails, SMA bulkheads, antennas) stay at the FRONT panel, U8 (TOP of rack).")
    c.setFillColor(WARN)
    c.setFont("SansBold", 9)
    c.drawString(55, box_y + 15, "Power at U1-U2, RF at U8 = 6U (10.5\") separation. Excellent EMI isolation.")

    draw_footer(c, 4, "Top-Down View — Cable Separation")


def main():
    c = canvas.Canvas(OUTPUT, pagesize=letter)
    c.setTitle("M2 Community Node — Rack Wiring Diagram")

    draw_cover_page(c)
    c.showPage()
    draw_page1_front_side(c)
    c.showPage()
    draw_page2_power_chain(c)
    c.showPage()
    draw_page3_top_down(c)
    c.showPage()

    c.save()
    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"[OK] Generated: {OUTPUT}")
    print(f"     Size: {size_kb:.0f} KB, 3 pages")
    print(f"     Page 1: Front view + side cross-section with cable routing")
    print(f"     Page 2: Power chain diagram + EMI analysis")
    print(f"     Page 3: Top-down view -- cable separation zones")


if __name__ == "__main__":
    main()
