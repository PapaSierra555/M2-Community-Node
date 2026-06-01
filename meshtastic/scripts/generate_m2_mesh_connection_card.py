#!/usr/bin/env python3
"""
M2 Community Node — Meshtastic Device Checkout Cards
4" x 6" landscape @ 300 DPI  |  2 cards per sheet  |  2 devices (M2-1, M2-2)

Front: HOW TO USE steps (left) + GET THE APP QR codes (right) + DEVICE SIGN-OUT strip
Back:  M2 branding + large device number badge

Outputs:
  ../pdf/M2_Mesh_DeviceCard_Front.pdf
  ../pdf/M2_Mesh_DeviceCard_Back.pdf

After printing: cut on crop marks, align front+back, laminate.
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode, io, os

DPI    = 300
CW, CH = int(6 * DPI), int(4 * DPI)     # 1800 x 1200 (6"x4" landscape)
PW, PH = int(8.5 * DPI), int(11 * DPI)  # 2550 x 3300 (letter portrait)

CARD_X   = (PW - CW) // 2
CARD_GAP = int(0.5 * DPI)
CARD_Y1  = (PH - 2 * CH - CARD_GAP) // 2
CARD_Y2  = CARD_Y1 + CH + CARD_GAP

ACCENT   = (146,  18,  18)   # #921212
ACCENT_D = (100,  10,  10)
ACCENT_L = (255, 200, 200)
DARK     = ( 15,  15,  15)
WHITE    = (255, 255, 255)
GRAY     = (110, 110, 110)
RULE     = (220, 220, 220)
GRID     = (246, 246, 246)
MARK_COL = ( 35,  35,  35)

_script_dir = os.path.dirname(os.path.abspath(__file__))
FONTS       = os.path.join(_script_dir, "../../scripts/fonts")
ASSETS      = os.path.join(_script_dir, "../../community-outreach/assets")
LOGO_PATH   = os.path.join(ASSETS, "lfhi-logo.png")
OUTPUT_DIR  = os.path.join(_script_dir, "../pdf")


def ff(name, sz):
    """Load a TTF from scripts/fonts/ or fall back to Arial."""
    path_map = {
        "bold":   os.path.join(FONTS, "BigShoulders-Bold.ttf"),
        "sans":   os.path.join(FONTS, "InstrumentSans-Regular.ttf"),
        "sbold":  os.path.join(FONTS, "InstrumentSans-Bold.ttf"),
        "mono":   os.path.join(FONTS, "IBMPlexMono-Regular.ttf"),
    }
    try:
        return ImageFont.truetype(path_map[name], sz)
    except Exception:
        arial = r"C:\Windows\Fonts\arial.ttf"
        arialbd = r"C:\Windows\Fonts\arialbd.ttf"
        bold_path = arialbd if name in ("bold", "sbold") else arial
        return ImageFont.truetype(bold_path, sz)


def _logo(size):
    if os.path.exists(LOGO_PATH):
        return Image.open(LOGO_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
    return None


def make_qr(url, size):
    qr = qrcode.QRCode(version=None,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
    buf.seek(0)
    return Image.open(buf).convert("RGB").resize((size, size), Image.LANCZOS)


# ── CARD FRONT ───────────────────────────────────────────────────────────────

def draw_front(num: int) -> Image.Image:
    img = Image.new("RGB", (CW, CH), WHITE)
    d   = ImageDraw.Draw(img)

    # Dot-grid background
    for gx in range(0, CW, 72):
        d.line([(gx, 0), (gx, CH)], fill=GRID, width=1)
    for gy in range(0, CH, 72):
        d.line([(0, gy), (CW, gy)], fill=GRID, width=1)
    for gx in range(0, CW, 72):
        for gy in range(0, CH, 72):
            d.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(232, 232, 232))
    d.rectangle([0, 0, CW-1, CH-1], outline=(190, 190, 190), width=1)
    d.rectangle([4, 4, CW-5, CH-5], outline=RULE, width=1)

    # ── Header ──
    HDR_H   = 96
    BADGE_W = 114
    BADGE_H = 80
    d.rectangle([0, 0, CW, HDR_H], fill=ACCENT)
    for hy in range(4, HDR_H - 2, 5):
        d.line([(8, hy), (CW-8, hy)], fill=ACCENT_D, width=1)
    d.rectangle([0, 0, 8, HDR_H], fill=ACCENT_D)

    # Logo + title
    logo = _logo(64)
    if logo:
        img.paste(logo, (18, (HDR_H - 64) // 2), logo)
    tx = 94 if logo else 28
    d.text((tx, 14), "M2 COMMUNITY NODE", font=ff("bold", 60), fill=WHITE)
    tw = int(d.textlength("M2 COMMUNITY NODE", font=ff("bold", 60)))
    d.text((tx + tw + 20, 30), "|   Mesh Radio Device",
           font=ff("sans", 34), fill=ACCENT_L)

    # Device number badge — right side of header
    bx = CW - BADGE_W - 10
    by = (HDR_H - BADGE_H) // 2
    d.rectangle([bx, by, bx + BADGE_W, by + BADGE_H],
                fill=WHITE, outline=ACCENT_L, width=2)
    d.text((bx + BADGE_W // 2, by + BADGE_H // 2),
           f"{num:02d}", font=ff("bold", 62), fill=ACCENT, anchor="mm")

    # ── Footer ──
    FTR_H = 58
    FTR_Y = CH - FTR_H
    d.rectangle([0, FTR_Y, CW, CH], fill=DARK)
    d.line([(0, FTR_Y), (CW, FTR_Y)], fill=ACCENT_D, width=2)
    d.text((CW // 2, FTR_Y + FTR_H // 2),
           "No internet.  No cell service.  Radio only.  |  Airplane Mode OK — keep Bluetooth on.",
           font=ff("sans", 26), fill=(150, 150, 150), anchor="mm")

    # ── Body ──
    BODY_Y  = HDR_H + 12
    SPLIT_X = 1100
    LX      = 28
    QR_SZ   = 240
    RX_MID  = (SPLIT_X + CW) // 2
    qr_x    = RX_MID - QR_SZ // 2

    # Estimate where right column ends for SIGN_Y
    _ry = BODY_Y + 10 + 54 + QR_SZ + 80 + 16 + QR_SZ + 70
    SIGN_Y = _ry + 14

    # Vertical divider
    d.line([(SPLIT_X, BODY_Y + 8), (SPLIT_X, SIGN_Y - 10)], fill=RULE, width=1)

    # ── LEFT: HOW TO USE steps ──
    steps = [
        ("1.", "Install the Meshtastic app first",                                 False),
        ("2.", "Enable Bluetooth on your phone",                                   False),
        ("3.", "Pair this device — CommunityNode channel loads automatically",     False),
        ("4.", "Settings → User → set your name so others see who you are", True),
        ("5.", "Messages → tap CommunityNode to send",                        False),
    ]

    step_sz = 28
    for sz in range(80, 27, -1):
        num_ind = max(58, int(sz * 1.22))
        text_x_ = LX + num_ind
        max_tw  = SPLIT_X - text_x_ - 24
        h_ok = all(int(d.textlength(t, font=ff("sbold" if b else "sans", sz))) <= max_tw
                   for _, t, b in steps)
        if not h_ok:
            continue
        lbl_h   = int(max(26, int(sz * 0.82)) * 1.12) + int(sz * 1.0)
        v_end   = BODY_Y + 14 + lbl_h + len(steps) * int(sz * 1.8)
        if h_ok and v_end <= SIGN_Y - 12:
            step_sz = sz
            break

    num_ind = max(58, int(step_sz * 1.22))
    text_x  = LX + num_ind
    num_sz  = int(step_sz * 1.12)
    step_h  = int(step_sz * 1.8)
    ly      = BODY_Y + 14

    lbl_sz = max(26, int(step_sz * 0.82))
    d.text((LX, ly), "HOW TO USE", font=ff("sbold", lbl_sz), fill=ACCENT)
    lw = int(d.textlength("HOW TO USE", font=ff("sbold", lbl_sz)))
    d.line([(LX, ly + int(lbl_sz * 1.12)), (LX + lw, ly + int(lbl_sz * 1.12))],
           fill=ACCENT, width=2)
    ly += int(step_sz * 1.0)

    for snum, txt, bold in steps:
        d.text((LX,     ly), snum, font=ff("bold", num_sz), fill=ACCENT)
        d.text((text_x, ly), txt,  font=ff("sbold" if bold else "sans", step_sz), fill=DARK)
        ly += step_h

    # ── RIGHT: GET THE APP QR codes ──
    ry = BODY_Y + 10
    d.text((RX_MID, ry), "GET THE APP", font=ff("bold", 32), fill=ACCENT, anchor="mt")
    lw2 = int(d.textlength("GET THE APP", font=ff("bold", 32)))
    d.line([(RX_MID - lw2//2, ry + 38), (RX_MID + lw2//2, ry + 38)], fill=ACCENT, width=2)
    ry += 54

    android_qr = make_qr(
        "https://play.google.com/store/apps/details?id=com.geeksville.mesh", QR_SZ)
    iphone_qr = make_qr(
        "https://apps.apple.com/us/app/meshtastic/id1586432531", QR_SZ)

    img.paste(android_qr, (qr_x, ry))
    d.text((RX_MID, ry + QR_SZ + 8),  "Android",     font=ff("sbold", 28), fill=DARK,  anchor="mt")
    d.text((RX_MID, ry + QR_SZ + 38), "Google Play", font=ff("sans",  24), fill=GRAY,  anchor="mt")
    ry += QR_SZ + 80

    d.line([(SPLIT_X + 30, ry), (CW - 30, ry)], fill=RULE, width=1)
    ry += 16

    img.paste(iphone_qr, (qr_x, ry))
    d.text((RX_MID, ry + QR_SZ + 8),  "iPhone",    font=ff("sbold", 28), fill=DARK,  anchor="mt")
    d.text((RX_MID, ry + QR_SZ + 38), "App Store", font=ff("sans",  24), fill=GRAY,  anchor="mt")

    # ── Full-width DEVICE SIGN-OUT strip ──
    MARGIN = 20
    SBX1, SBX2 = MARGIN, CW - MARGIN
    SBY1, SBY2 = SIGN_Y, FTR_Y - 8

    d.rectangle([SBX1, SBY1, SBX2, SBY2], fill=(252, 252, 252), outline=(175, 175, 175), width=1)

    TH = 38
    d.rectangle([SBX1, SBY1, SBX2, SBY1 + TH], fill=(236, 236, 236))
    d.line([(SBX1, SBY1 + TH), (SBX2, SBY1 + TH)], fill=RULE, width=1)
    d.text((SBX1 + 16, SBY1 + TH // 2), "DEVICE SIGN-OUT",
           font=ff("sbold", 24), fill=ACCENT, anchor="lm")
    d.text((SBX2 - 16, SBY1 + TH // 2), f"M2 Community Node {num:02d}",
           font=ff("sbold", 24), fill=DARK, anchor="rm")

    inner_top = SBY1 + TH
    inner_h   = SBY2 - inner_top
    fields    = [
        (f"Device:   M2 Community Node {num:02d}  (M2-{num})", True),
        ("Borrower: _______________________________________________", False),
        ("Signature: ______________________________________________", False),
    ]
    row_h = inner_h // len(fields)
    for i, (fld, bold_it) in enumerate(fields):
        fy = inner_top + i * row_h
        d.text((SBX1 + 16, fy + row_h // 2), fld,
               font=ff("sbold" if bold_it else "sans", 26),
               fill=DARK if bold_it else GRAY, anchor="lm")
        if i < len(fields) - 1:
            d.line([(SBX1 + 8, fy + row_h), (SBX2 - 8, fy + row_h)], fill=RULE, width=1)

    return img


# ── CARD BACK ────────────────────────────────────────────────────────────────

def draw_back(num: int) -> Image.Image:
    img = Image.new("RGB", (CW, CH), ACCENT)
    d   = ImageDraw.Draw(img)

    # Texture
    for hy in range(0, CH, 6):
        d.line([(0, hy), (CW, hy)], fill=ACCENT_D, width=1)

    # Border bars
    for rect in [(0, 0, 12, CH), (CW-12, 0, CW, CH),
                 (0, 0, CW, 12), (0, CH-12, CW, CH)]:
        d.rectangle(rect, fill=ACCENT_D)

    mid_x, mid_y = CW // 2, CH // 2

    # ── Logo + title ──
    LOGO_SZ = 128
    HDR_TOP = 20
    logo = _logo(LOGO_SZ)
    logo_x = 32
    if logo:
        img.paste(logo, (logo_x, HDR_TOP), logo)

    tx = logo_x + LOGO_SZ + 22
    d.text((tx, HDR_TOP + 6), "M2 COMMUNITY", font=ff("bold", 96), fill=WHITE)

    rule_y = HDR_TOP + LOGO_SZ + 18
    d.line([(60, rule_y), (CW - 60, rule_y)], fill=ACCENT_L, width=2)
    d.text((tx, rule_y + 12), "MESH DEVICE", font=ff("bold", 52), fill=ACCENT_L)

    # ── Center: device number badge ──
    badge_r = 155
    bx, by  = mid_x, mid_y + 34
    d.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
              fill=WHITE, outline=ACCENT_L, width=5)
    d.text((bx, by), f"{num:02d}", font=ff("bold", 148), fill=ACCENT, anchor="mm")

    # ── Bottom labels ──
    d.text((mid_x, by + badge_r + 20), "Radio Communications",
           font=ff("sans", 38), fill=ACCENT_L, anchor="mt")
    d.text((mid_x, by + badge_r + 68), "M2 Community Node  —  Internal Use Only",
           font=ff("sans", 28), fill=(210, 100, 100), anchor="mt")

    return img


# ── SHEET LAYOUT ─────────────────────────────────────────────────────────────

def crop_mark(d, cx, cy, corner):
    GAP, LEN = 18, 54
    hs = -1 if corner in ('tl', 'bl') else 1
    vs = -1 if corner in ('tl', 'tr') else 1
    d.line([(cx + hs*GAP, cy), (cx + hs*(GAP+LEN), cy)], fill=MARK_COL, width=2)
    d.line([(cx, cy + vs*GAP), (cx, cy + vs*(GAP+LEN))], fill=MARK_COL, width=2)
    d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=MARK_COL)


def make_sheet(top_card, bot_card, note1="", note2=""):
    sheet = Image.new("RGB", (PW, PH), WHITE)
    ds    = ImageDraw.Draw(sheet)
    sheet.paste(top_card, (CARD_X, CARD_Y1))
    sheet.paste(bot_card, (CARD_X, CARD_Y2))

    for y in (CARD_Y1, CARD_Y2):
        crop_mark(ds, CARD_X,      y,      'tl')
        crop_mark(ds, CARD_X + CW, y,      'tr')
        crop_mark(ds, CARD_X,      y + CH, 'bl')
        crop_mark(ds, CARD_X + CW, y + CH, 'br')

    cut_y   = CARD_Y1 + CH + CARD_GAP // 2
    cut_col = (180, 180, 180)
    ds.line([(CARD_X - 80, cut_y), (CARD_X - 22, cut_y)], fill=cut_col, width=1)
    ds.line([(CARD_X+CW+22, cut_y), (CARD_X+CW+80, cut_y)], fill=cut_col, width=1)
    note_f = ff("sans", 19)
    ds.text((CARD_X - 86, cut_y), "CUT", font=note_f, fill=cut_col, anchor="rm")
    ds.text((CARD_X+CW+86, cut_y), "CUT", font=note_f, fill=cut_col, anchor="lm")

    if note1:
        ds.text((PW//2, PH - 72), note1, font=note_f, fill=(180,180,180), anchor="mm")
    if note2:
        ds.text((PW//2, PH - 46), note2, font=note_f, fill=(200,200,200), anchor="mm")

    return sheet


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_front = os.path.join(OUTPUT_DIR, "M2_Mesh_DeviceCard_Front.pdf")
    out_back  = os.path.join(OUTPUT_DIR, "M2_Mesh_DeviceCard_Back.pdf")

    pairs = [(1, 2), (3, 4), (5, 6), (7, 8)]
    front_pages = []
    back_pages  = []
    for a, b in pairs:
        front_pages.append(make_sheet(
            draw_front(a), draw_front(b),
            note1="Print at 100% / Actual Size — do not scale — 300 DPI",
            note2=f"M2 Device Cards  FRONT  |  Nodes {a:02d} & {b:02d}  |  4\" x 6\""
        ))
        back_pages.append(make_sheet(
            draw_back(b), draw_back(a),
            note1="Print at 100% / Actual Size — do not scale — 300 DPI",
            note2=f"M2 Device Cards  BACK   |  Nodes {a:02d} & {b:02d}  |  Flip short edge for duplex"
        ))

    front_pages[0].save(out_front, "PDF", resolution=DPI, save_all=True, append_images=front_pages[1:])
    back_pages[0].save(out_back,   "PDF", resolution=DPI, save_all=True, append_images=back_pages[1:])

    print(f"Front: {out_front}  (4 pages)")
    print(f"Back:  {out_back}   (4 pages)")
    print()
    print("PRINT INSTRUCTIONS:")
    print("  1. Print M2_Mesh_DeviceCard_Front.pdf  (4 pages, 2 nodes per sheet)")
    print("  2. Reload same paper — flip on SHORT edge")
    print("  3. Print M2_Mesh_DeviceCard_Back.pdf   (4 pages, matching backs)")
    print("  4. Match sheets by node number, cut on crop marks, laminate")


if __name__ == "__main__":
    main()
