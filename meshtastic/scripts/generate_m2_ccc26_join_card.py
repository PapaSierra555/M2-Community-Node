#!/usr/bin/env python3
"""
M2 Community Node — CCC26 Element Chat Room Join Card
4" x 6" landscape @ 300 DPI  |  2 cards per sheet

Two QR codes per card:
  LEFT  — Join the M2 server (create account or log in)
  RIGHT — Join the CCC26 event space (E2EE encrypted, any Matrix account)

Output: operational-pdfs/M2_CCC26_Element_JoinCard.pdf
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
MUTED    = (110, 110, 110)
CARD_BG  = (250, 246, 246)
RULE     = (228, 208, 208)
DIVIDER  = (210, 185, 185)
MARK_COL = ( 35,  35,  35)
STEP_BG  = (240, 225, 225)

SERVER_URL = "https://communitynode.capableenough.org"
ROOM_URL   = "https://matrix.to/#/#m2-ccc26-general:m2.capableenough.org"

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


def draw_step_block(d, img, x, y, w, step_num, heading, lines, qr_img, qr_sz, note_lines=None):
    """Draw a numbered step block with heading, instruction lines, and QR code."""
    # Step number badge
    badge_r = 28
    badge_cx = x + badge_r + 8
    badge_cy = y + badge_r + 8
    d.ellipse([badge_cx - badge_r, badge_cy - badge_r,
               badge_cx + badge_r, badge_cy + badge_r], fill=ACCENT)
    d.text((badge_cx, badge_cy), step_num,
           font=ff("bold", 34), fill=WHITE, anchor="mm")

    # Heading
    d.text((badge_cx + badge_r + 14, y + 8), heading,
           font=ff("bold", 40), fill=ACCENT)

    # Divider line under heading
    line_y = y + 60
    d.line([(x + 8, line_y), (x + w - 8, line_y)], fill=DIVIDER, width=2)

    # Instruction lines
    text_y = line_y + 18
    for line in lines:
        d.text((x + 12, text_y), line, font=ff("sans", 28), fill=DARK)
        text_y += 40

    # QR code centered in remaining space
    qr_x = x + (w - qr_sz) // 2
    qr_y = text_y + 16
    pad = 12
    d.rectangle([qr_x - pad, qr_y - pad,
                 qr_x + qr_sz + pad, qr_y + qr_sz + pad],
                fill=WHITE, outline=RULE, width=2)
    img.paste(qr_img, (qr_x, qr_y))

    # Optional note lines below QR
    if note_lines:
        note_y = qr_y + qr_sz + pad + 44
        for note in note_lines:
            d.text((x + w // 2, note_y), note,
                   font=ff("sans", 23), fill=MUTED, anchor="mm")
            note_y += 38


def draw_join_card() -> Image.Image:
    img = Image.new("RGB", (CW, CH), CARD_BG)
    d   = ImageDraw.Draw(img)

    # Card border
    d.rectangle([0, 0, CW-1, CH-1], outline=RULE, width=2)
    d.rectangle([4, 4, CW-5, CH-5], outline=RULE, width=1)

    # ── Header ───────────────────────────────────────────────────────────────
    HDR_H = 100
    d.rectangle([0, 0, CW, HDR_H], fill=ACCENT)
    for hy in range(4, HDR_H - 2, 5):
        d.line([(0, hy), (CW, hy)], fill=ACCENT_D, width=1)

    logo = _logo(68)
    logo_x = 16
    if logo:
        img.paste(logo, (logo_x, (HDR_H - 68) // 2), logo)

    tx = logo_x + 68 + 16 if logo else 24
    d.text((tx, 12), "CCC26 ELEMENT CHAT ROOM",
           font=ff("bold", 58), fill=WHITE)
    d.text((tx, 70), "M2 Community Node  —  E2EE encrypted  —  any Matrix account works",
           font=ff("sans", 26), fill=ACCENT_L)

    # ── Footer ───────────────────────────────────────────────────────────────
    FOOT_H = 210
    FTR_Y  = CH - FOOT_H
    d.rectangle([0, FTR_Y, CW, CH], fill=DARK)
    d.line([(0, FTR_Y), (CW, FTR_Y)], fill=ACCENT, width=4)

    # Fixed y positions — each line is the center of the text (anchor="mm")
    d.text((CW // 2, FTR_Y + 28),
           "Already have a Matrix account?  Skip Step 1 — scan Step 2 directly.",
           font=ff("sbold", 30), fill=WHITE, anchor="mm")

    d.line([(80, FTR_Y + 50), (CW - 80, FTR_Y + 50)], fill=(70, 70, 70), width=1)

    d.text((CW // 2, FTR_Y + 80),
           "Manual:  Server → matrix.capableenough.org  |  Explore rooms → search #ccc26",
           font=ff("sbold", 28), fill=WHITE, anchor="mm")

    d.text((CW // 2, FTR_Y + 116),
           "Federated users: log in with your home server — Step 2 QR joins CCC26 directly.",
           font=ff("sans", 27), fill=WHITE, anchor="mm")

    d.text((CW // 2, FTR_Y + 152),
           "All CCC26 rooms are end-to-end encrypted (E2EE).",
           font=ff("sbold", 27), fill=ACCENT_L, anchor="mm")

    # ── Body ─────────────────────────────────────────────────────────────────
    BODY_Y   = HDR_H + 16
    BODY_BOT = FTR_Y - 12
    BODY_H   = BODY_BOT - BODY_Y

    # Vertical divider
    MID_X = CW // 2
    d.line([(MID_X, BODY_Y + 8), (MID_X, BODY_BOT - 8)],
           fill=DIVIDER, width=2)
    d.text((MID_X, BODY_Y + BODY_H // 2), "OR\nTHEN",
           font=ff("bold", 28), fill=DIVIDER, anchor="mm", align="center")

    # Column widths
    COL_W  = MID_X - 20
    QR_SZ  = 480

    # ── LEFT: Step 1 — Join the Server ───────────────────────────────────────
    server_qr = make_qr(SERVER_URL, QR_SZ)
    draw_step_block(
        d, img,
        x=12, y=BODY_Y, w=COL_W,
        step_num="1",
        heading="JOIN THE SERVER",
        lines=[
            "Create your M2 account here.",
            "Skip if you have any Matrix account.",
        ],
        qr_img=server_qr,
        qr_sz=QR_SZ,
        note_lines=[
            "After creating your account, return to Element app.",
            "Enter m2.capableenough.org as your server to log in.",
        ],
    )

    # ── RIGHT: Step 2 — Join the Room ────────────────────────────────────────
    room_qr = make_qr(ROOM_URL, QR_SZ)
    draw_step_block(
        d, img,
        x=MID_X + 8, y=BODY_Y, w=COL_W,
        step_num="2",
        heading="JOIN THE ROOM",
        lines=[
            "Adds you to the CCC26 event space.",
            "Works with any Matrix account.",
        ],
        qr_img=room_qr,
        qr_sz=QR_SZ,
        note_lines=[
            "Browser will open — tap 'Open in Element' to join from the app.",
            "Federated account? Log in with your home server — no change needed.",
        ],
    )

    return img


def crop_mark(d, cx, cy, corner):
    GAP, LEN = 18, 54
    hs = -1 if corner in ('tl', 'bl') else 1
    vs = -1 if corner in ('tl', 'tr') else 1
    d.line([(cx + hs*GAP, cy), (cx + hs*(GAP+LEN), cy)], fill=MARK_COL, width=2)
    d.line([(cx, cy + vs*GAP), (cx, cy + vs*(GAP+LEN))], fill=MARK_COL, width=2)
    d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=MARK_COL)


def make_sheet(card):
    sheet = Image.new("RGB", (PW, PH), WHITE)
    ds    = ImageDraw.Draw(sheet)
    sheet.paste(card, (CARD_X, CARD_Y1))
    sheet.paste(card, (CARD_X, CARD_Y2))

    for cy in (CARD_Y1, CARD_Y2):
        crop_mark(ds, CARD_X,      cy,      'tl')
        crop_mark(ds, CARD_X + CW, cy,      'tr')
        crop_mark(ds, CARD_X,      cy + CH, 'bl')
        crop_mark(ds, CARD_X + CW, cy + CH, 'br')

    cut_y   = CARD_Y1 + CH + CARD_GAP // 2
    cut_col = (180, 180, 180)
    note_f  = ff("sans", 19)
    ds.line([(CARD_X-80, cut_y), (CARD_X-22, cut_y)], fill=cut_col, width=1)
    ds.line([(CARD_X+CW+22, cut_y), (CARD_X+CW+80, cut_y)], fill=cut_col, width=1)
    ds.text((CARD_X-86, cut_y), "CUT", font=note_f, fill=cut_col, anchor="rm")
    ds.text((CARD_X+CW+86, cut_y), "CUT", font=note_f, fill=cut_col, anchor="lm")
    ds.text((PW//2, PH-72),
            "Print at 100% / Actual Size — do not scale — 300 DPI",
            font=note_f, fill=(180, 180, 180), anchor="mm")
    ds.text((PW//2, PH-46),
            "M2 CCC26 Element Join Cards  |  4\" x 6\"  |  2 per sheet",
            font=note_f, fill=(200, 200, 200), anchor="mm")
    return sheet


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "M2_CCC26_Element_JoinCard.pdf")
    card  = draw_join_card()
    sheet = make_sheet(card)
    sheet.save(out_path, "PDF", resolution=DPI)
    print(f"Output: {out_path}")
    print(f"Step 1 QR: {SERVER_URL}")
    print(f"Step 2 QR: {ROOM_URL}")
    print("PRINT: 100% / Actual Size — cut on crop marks — laminate")


if __name__ == "__main__":
    main()
