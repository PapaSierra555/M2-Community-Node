#!/usr/bin/env python3
"""
M2 Community Node — CCC26 Matrix Join Card
4" x 6" landscape @ 300 DPI  |  2 cards per sheet

QR code deep-links directly to the CCC26 space in Element Web.

Output: ../pdf/M2_CCC26_JoinCard.pdf
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode, io, os

DPI    = 300
CW, CH = int(6 * DPI), int(4 * DPI)     # 1800 x 1200
PW, PH = int(8.5 * DPI), int(11 * DPI)  # 2550 x 3300

CARD_X   = (PW - CW) // 2
CARD_GAP = int(0.5 * DPI)
CARD_Y1  = (PH - 2 * CH - CARD_GAP) // 2
CARD_Y2  = CARD_Y1 + CH + CARD_GAP

ACCENT   = (146,  18,  18)
ACCENT_D = (100,  10,  10)
ACCENT_L = (255, 200, 200)
DARK     = ( 15,  15,  15)
WHITE    = (255, 255, 255)
GRAY     = (110, 110, 110)
RULE     = (220, 220, 220)
GRID     = (246, 246, 246)
MARK_COL = ( 35,  35,  35)

JOIN_URL = ("https://communitynode.capableenough.org"
            "/#/room/!Qqpo859OnrgQ5DWg8h:m2.capableenough.org")

_script_dir = os.path.dirname(os.path.abspath(__file__))
FONTS       = os.path.join(_script_dir, "../../scripts/fonts")
ASSETS      = os.path.join(_script_dir, "../../community-outreach/assets")
LOGO_PATH   = os.path.join(ASSETS, "lfhi-logo.png")
OUTPUT_DIR  = os.path.join(_script_dir, "../../operational-pdfs")


def ff(name, sz):
    path_map = {
        "bold":  os.path.join(FONTS, "BigShoulders-Bold.ttf"),
        "sans":  os.path.join(FONTS, "InstrumentSans-Regular.ttf"),
        "sbold": os.path.join(FONTS, "InstrumentSans-Bold.ttf"),
        "mono":  os.path.join(FONTS, "IBMPlexMono-Regular.ttf"),
    }
    try:
        return ImageFont.truetype(path_map[name], sz)
    except Exception:
        arial   = r"C:\Windows\Fonts\arial.ttf"
        arialbd = r"C:\Windows\Fonts\arialbd.ttf"
        return ImageFont.truetype(arialbd if name in ("bold", "sbold") else arial, sz)


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


def draw_join_card() -> Image.Image:
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

    # ── Header (identical to DeviceCard) ──
    HDR_H = 96
    d.rectangle([0, 0, CW, HDR_H], fill=ACCENT)
    for hy in range(4, HDR_H - 2, 5):
        d.line([(8, hy), (CW-8, hy)], fill=ACCENT_D, width=1)
    d.rectangle([0, 0, 8, HDR_H], fill=ACCENT_D)

    logo = _logo(64)
    if logo:
        img.paste(logo, (18, (HDR_H - 64) // 2), logo)
    tx = 94 if logo else 28
    d.text((tx, 14), "M2 COMMUNITY NODE", font=ff("bold", 60), fill=WHITE)
    tw = int(d.textlength("M2 COMMUNITY NODE", font=ff("bold", 60)))
    d.text((tx + tw + 20, 30), "|   CCC26 Event Chat",
           font=ff("sans", 34), fill=ACCENT_L)

    # ── Footer (identical to DeviceCard) ──
    FTR_H = 58
    FTR_Y = CH - FTR_H
    d.rectangle([0, FTR_Y, CW, CH], fill=DARK)
    d.line([(0, FTR_Y), (CW, FTR_Y)], fill=ACCENT_D, width=2)
    d.text((CW // 2, FTR_Y + FTR_H // 2),
           "Connect to CommunityNode WiFi first  —  then scan to join the chat",
           font=ff("sans", 26), fill=(150, 150, 150), anchor="mm")

    # ── Body ──
    BODY_Y = HDR_H + 20
    BODY_H = FTR_Y - BODY_Y  # 1026px

    mid_x  = CW // 2
    QR_SZ  = 500

    label      = "To join the ‘M2 CCC Chat Room’, scan here:"
    label_font = ff("sbold", 40)
    label_h    = 52

    content_h = label_h + 28 + QR_SZ
    start_y   = BODY_Y + (BODY_H - content_h) // 2

    # Label
    d.text((mid_x, start_y + label_h // 2), label,
           font=label_font, fill=DARK, anchor="mm")
    lw = int(d.textlength(label, font=label_font))
    d.line([(mid_x - lw // 2, start_y + label_h),
            (mid_x + lw // 2, start_y + label_h)],
           fill=ACCENT, width=2)

    # QR code with white padded box
    qr_img = make_qr(JOIN_URL, QR_SZ)
    qr_x   = mid_x - QR_SZ // 2
    qr_y   = start_y + label_h + 28
    PAD    = 14
    d.rectangle([qr_x - PAD, qr_y - PAD,
                 qr_x + QR_SZ + PAD, qr_y + QR_SZ + PAD],
                fill=WHITE, outline=RULE, width=1)
    img.paste(qr_img, (qr_x, qr_y))

    return img


def crop_mark(d, cx, cy, corner):
    GAP, LEN = 18, 54
    hs = -1 if corner in ('tl', 'bl') else 1
    vs = -1 if corner in ('tl', 'tr') else 1
    d.line([(cx + hs*GAP, cy), (cx + hs*(GAP+LEN), cy)], fill=MARK_COL, width=2)
    d.line([(cx, cy + vs*GAP), (cx, cy + vs*(GAP+LEN))], fill=MARK_COL, width=2)
    d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=MARK_COL)


def make_sheet(card1, card2):
    sheet = Image.new("RGB", (PW, PH), WHITE)
    ds    = ImageDraw.Draw(sheet)
    sheet.paste(card1, (CARD_X, CARD_Y1))
    sheet.paste(card2, (CARD_X, CARD_Y2))

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
    ds.text((PW // 2, PH - 72),
            "Print at 100% / Actual Size — do not scale — 300 DPI",
            font=note_f, fill=(180, 180, 180), anchor="mm")
    ds.text((PW // 2, PH - 46),
            "M2 CCC26 Join Cards  |  4\" x 6\"  |  2 per sheet",
            font=note_f, fill=(200, 200, 200), anchor="mm")

    return sheet


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "M2_CCC26_JoinCard.pdf")

    card  = draw_join_card()
    sheet = make_sheet(card, card)
    sheet.save(out_path, "PDF", resolution=DPI)

    print(f"Output: {out_path}")
    print(f"QR:     {JOIN_URL}")
    print()
    print("PRINT: 100% / Actual Size — do not scale — cut on crop marks — laminate")


if __name__ == "__main__":
    main()
