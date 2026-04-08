#!/usr/bin/env python3
"""Generate Cricut-ready vinyl cut SVGs for M2 Community Node rack labels.

Requirements:
    pip install fonttools qrcode shapely

Font: Uses Roboto-Black.ttf (place in scripts/) or WorkSans-Bold.ttf from canvas-fonts.
      Modify FONT_CANDIDATES if you have a different font available.

Outputs (written to ../svg/):
    vinyl-word-labels.svg    -- white vinyl: word labels, 1 copy (duplicate in Cricut)
    vinyl-qr-white-1.svg     -- white vinyl: QR bases + ID labels, sheet 1 of 2
    vinyl-qr-white-2.svg     -- white vinyl: QR bases + ID labels, sheet 2 of 2
    vinyl-qr-black-1.svg     -- black vinyl: QR modules (shapely-unioned paths), sheet 1
    vinyl-qr-black-2.svg     -- black vinyl: QR modules (shapely-unioned paths), sheet 2

Assembly for QR stickers:
    1. Apply white base squares to surface (clean with IPA first).
    2. Align and apply black modules on top -- match outer edges for registration.
    Both layers are exactly QR_SIZE_MM x QR_SIZE_MM; edge alignment = correct position.

Cricut Design Space notes:
    - Delete or hide the 'preview-bg' rect before cutting.
    - Assign white layer to white permanent vinyl.
    - Assign black layer to black permanent vinyl.
    - Each QR code is one unified path object (shapely union) -- no Weld needed.
"""

import os
import sys
from datetime import datetime

RUN_TS = datetime.now().strftime("%Y%m%d-%H%M%S")

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
except ImportError:
    print("ERROR: pip install fonttools")
    sys.exit(1)

try:
    import qrcode
    import qrcode.constants
except ImportError:
    print("ERROR: pip install qrcode")
    sys.exit(1)

try:
    from shapely.geometry import box as shapely_box
    from shapely.ops import unary_union
    from shapely.geometry import MultiPolygon, Polygon
except ImportError:
    print("ERROR: pip install shapely")
    sys.exit(1)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)
SVG_DIR    = os.path.join(ROOT_DIR, "svg")

from instance_config import cfg

CANVAS_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_CANDIDATES = [
    os.path.join(SCRIPT_DIR, "Roboto-Black.ttf"),
    os.path.join(SCRIPT_DIR, "Roboto-Bold.ttf"),
    os.path.join(CANVAS_FONTS, "WorkSans-Bold.ttf"),
    os.path.join(CANVAS_FONTS, "InstrumentSans-Bold.ttf"),
    os.path.join(CANVAS_FONTS, "BigShoulders-Bold.ttf"),
]


# ── Label configuration ───────────────────────────────────────────────────────

WORD_LABELS = [
    "MESHTASTIC",
    "RETICULUM",
    "WIFI",
    "ATAK",
    "M2 COMMUNITY NODE",
    "COMMUNITY INFO",
]

LABEL_CAP_MM       = 10.0   # capital letter height
LABEL_COPY_GAP_MM  =  3.0   # gap between copy 1 and copy 2 of same label
LABEL_GROUP_GAP_MM =  6.0   # gap between different label groups
MARGIN_MM          =  5.0


# ── QR configuration (mirrors generate_qr.py) ────────────────────────────────

QR_ITEMS = [
    ("WIFI",          cfg["WIFI_QR_STRING"]),
    ("ELEMENT LAN",   cfg["ELEMENT_LAN_URL"]),
    ("ELEMENT WEB",   f"https://{cfg['ELEMENT_DOMAIN']}"),
    ("TOR ELEMENT",   cfg["TOR_ELEMENT_URL"]),
    ("TOR MATRIX",    cfg["TOR_MATRIX_URL"]),
    ("TOR COMMUNITY", cfg["TOR_COMMUNITY_URL"]),
    ("ATAK ANDROID",  "https://play.google.com/store/apps/details?id=com.atakmap.app.civ"),
    ("ITAK IOS",      "https://apps.apple.com/us/app/itak/id1558773892"),
    ("MESHTASTIC",    "https://github.com/meshtastic/ATAK-Plugin/releases"),
    ("MUMLA",         "https://play.google.com/store/apps/details?id=se.lublin.mumla"),
    ("COMMUNITY",     cfg["COMMUNITY_PAGE_URL"]),
    ("ATAK CONNECT",  cfg["ATAK_ENROLL_URL"]),
]

QR_SIZE_MM      = 40.0   # total sticker size including quiet zone
QR_BORDER       = 4      # quiet zone modules (QR spec minimum)
QR_COLS         = 6      # columns per row
QR_CORNER_RATIO = 0.35   # module corner radius as fraction of module size (0=square, 0.5=pill)
QR_ID_CAP_MM  = 4.0    # ID label cap height below each QR base
QR_ID_GAP_MM  = 1.5    # gap between QR base and ID label
QR_COL_GAP_MM = 5.0    # horizontal gap between cells
QR_ROW_GAP_MM = 5.0    # vertical gap between rows


# ── Font loading ──────────────────────────────────────────────────────────────

def load_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            print(f"  Font: {os.path.basename(p)}")
            return TTFont(p)
    print("ERROR: No suitable font found.")
    print("Checked:")
    for p in FONT_CANDIDATES:
        print(f"  {p}")
    sys.exit(1)


# ── QR module union to SVG path ──────────────────────────────────────────────

def modules_to_svg_path(modules, x0, y0, ms, border):
    """Union all dark QR modules into a single compound SVG path string.

    Each module is a rounded rectangle (QR_CORNER_RATIO controls rounding).
    Adjacent modules merge into connected shapes. Cricut sees one object per QR.
    """
    r = ms * QR_CORNER_RATIO
    shapes = []
    for r_i, row in enumerate(modules):
        for c_i, is_dark in enumerate(row):
            if is_dark:
                mx = x0 + (c_i + border) * ms
                my = y0 + (r_i + border) * ms
                inner = shapely_box(mx + r, my + r, mx + ms - r, my + ms - r)
                rounded = inner.buffer(r, resolution=4, join_style=1)
                shapes.append(rounded)
    if not shapes:
        return ""
    merged = unary_union(shapes)
    return _geom_to_path_d(merged)


def _ring_to_d(coords):
    pts = list(coords)
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    d = f"M{pts[0][0]:.4f},{pts[0][1]:.4f}"
    for x, y in pts[1:]:
        d += f"L{x:.4f},{y:.4f}"
    return d + "Z"


def _geom_to_path_d(geom):
    parts = []
    polys = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    for poly in polys:
        parts.append(_ring_to_d(poly.exterior.coords))
        for interior in poly.interiors:
            parts.append(_ring_to_d(interior.coords))
    return " ".join(parts)


# ── Text to SVG path data ─────────────────────────────────────────────────────

def text_to_path(font, text, cap_mm, x0=0.0, y0=0.0):
    """Convert text to SVG path 'd' attribute string.

    x0, y0: top-left corner of the cap-height bounding box in SVG mm units.
    Returns (path_d_string, total_advance_width_mm).
    """
    os2 = font['OS/2']
    # sCapHeight is optional in OS/2 — fall back to 72% of UPM
    cap_units = getattr(os2, 'sCapHeight', 0) or int(font['head'].unitsPerEm * 0.72)
    scale = cap_mm / cap_units   # mm per font unit

    cmap = font.getBestCmap()
    gset = font.getGlyphSet()
    hmtx = font['hmtx'].metrics

    parts = []
    x_cur = 0.0

    for ch in text:
        cp = ord(ch)
        if cp not in cmap:
            # Unknown / space: advance by space width or fallback
            sp_gn = cmap.get(ord(' '))
            x_cur += hmtx[sp_gn][0] * scale if sp_gn else cap_mm * 0.35
            continue

        gn = cmap[cp]
        pen = SVGPathPen(gset)
        # Font Y-up → SVG Y-down transform.
        # x_svg = x0 + x_cur + x_font * scale
        # y_svg = (y0 + cap_mm) - y_font * scale
        tp = TransformPen(pen, (scale, 0, 0, -scale, x0 + x_cur, y0 + cap_mm))
        gset[gn].draw(tp)
        d = pen.getCommands()
        if d:
            parts.append(d)
        x_cur += hmtx[gn][0] * scale

    return ' '.join(parts), x_cur


# ── Word label sheet ──────────────────────────────────────────────────────────

def generate_word_labels(font):
    os.makedirs(SVG_DIR, exist_ok=True)

    # Pre-measure widths for sheet sizing
    widths = {lbl: text_to_path(font, lbl, LABEL_CAP_MM)[1] for lbl in WORD_LABELS}
    sheet_w = max(widths.values()) + 2 * MARGIN_MM

    total_h = MARGIN_MM
    for i in range(len(WORD_LABELS)):
        total_h += LABEL_CAP_MM + LABEL_COPY_GAP_MM + LABEL_CAP_MM
        if i < len(WORD_LABELS) - 1:
            total_h += LABEL_GROUP_GAP_MM
    total_h += MARGIN_MM

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     width="{sheet_w:.2f}mm" height="{total_h:.2f}mm"',
        f'     viewBox="0 0 {sheet_w:.2f} {total_h:.2f}">',
        f'  <!-- M2 Community Node - Word Labels - WHITE vinyl cut -->',
        f'  <!-- {len(WORD_LABELS)} labels x 2 copies | {LABEL_CAP_MM}mm cap height -->',
        f'  <!-- DELETE preview-bg rect before sending to Cricut -->',
        f'  <rect id="preview-bg" width="{sheet_w:.2f}" height="{total_h:.2f}"'
        f' fill="#111111"/>',
    ]

    y = MARGIN_MM
    for i, lbl in enumerate(WORD_LABELS):
        d1, _ = text_to_path(font, lbl, LABEL_CAP_MM, x0=MARGIN_MM, y0=y)
        y += LABEL_CAP_MM + LABEL_COPY_GAP_MM
        d2, _ = text_to_path(font, lbl, LABEL_CAP_MM, x0=MARGIN_MM, y0=y)
        y += LABEL_CAP_MM
        if i < len(WORD_LABELS) - 1:
            y += LABEL_GROUP_GAP_MM
        lines.append(f'  <path d="{d1} {d2}" fill="#ffffff"/>')

    lines.append('</svg>')

    out = os.path.join(SVG_DIR, f"vinyl-word-labels-{RUN_TS}.svg")
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    written = os.path.getsize(out)
    if written == 0:
        print(f"  ERROR: vinyl-word-labels.svg wrote 0 bytes!")
        sys.exit(1)
    print(f"  vinyl-word-labels.svg  ({sheet_w:.1f} x {total_h:.1f} mm)  {written} bytes  -> {out}")
    return out


# ── QR code sheets ────────────────────────────────────────────────────────────

def build_qr_modules():
    results = []
    for label, data in QR_ITEMS:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=QR_BORDER,
        )
        qr.add_data(data)
        qr.make(fit=True)
        results.append({
            'label': label,
            'modules': qr.modules,
            'mc': qr.modules_count,
            'version': qr.version,
        })
    return results


def generate_qr_sheets(font, qr_data):
    """Two SVG pairs (white + black), each with 6 QR codes in a single row.
    One copy per code — duplicate in Cricut Design Space before cutting.
    """
    os.makedirs(SVG_DIR, exist_ok=True)

    half = len(qr_data) // 2
    groups = [qr_data[:half], qr_data[half:]]

    for g_idx, group in enumerate(groups, start=1):
        n = len(group)
        sheet_w = MARGIN_MM + n * QR_SIZE_MM + (n - 1) * QR_COL_GAP_MM + MARGIN_MM
        sheet_h = MARGIN_MM + QR_SIZE_MM + QR_ID_GAP_MM + QR_ID_CAP_MM + MARGIN_MM

        white_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg"',
            f'     width="{sheet_w:.2f}mm" height="{sheet_h:.2f}mm"',
            f'     viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">',
            f'  <!-- QR sheet {g_idx}/2 - WHITE vinyl - 1 copy each, duplicate in Cricut -->',
            f'  <!-- DELETE preview-bg before cutting -->',
            f'  <rect id="preview-bg" width="{sheet_w:.2f}" height="{sheet_h:.2f}" fill="#111111"/>',
        ]
        black_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg"',
            f'     width="{sheet_w:.2f}mm" height="{sheet_h:.2f}mm"',
            f'     viewBox="0 0 {sheet_w:.2f} {sheet_h:.2f}">',
            f'  <!-- QR sheet {g_idx}/2 - BLACK vinyl - align to white base edges -->',
            f'  <!-- DELETE preview-bg before cutting -->',
            f'  <rect id="preview-bg" width="{sheet_w:.2f}" height="{sheet_h:.2f}" fill="#ffffff"/>',
        ]

        for col, item in enumerate(group):
            mc    = item['mc']
            total = mc + 2 * QR_BORDER
            ms    = QR_SIZE_MM / total
            x0    = MARGIN_MM + col * (QR_SIZE_MM + QR_COL_GAP_MM)
            y0    = MARGIN_MM

            # White: base square
            white_lines.append(
                f'  <rect x="{x0:.3f}" y="{y0:.3f}"'
                f' width="{QR_SIZE_MM:.3f}" height="{QR_SIZE_MM:.3f}" fill="#ffffff"/>'
            )
            # White: ID label below
            label_y = y0 + QR_SIZE_MM + QR_ID_GAP_MM
            d_id, _ = text_to_path(font, item['label'], QR_ID_CAP_MM, x0=x0, y0=label_y)
            if d_id:
                white_lines.append(f'  <path d="{d_id}" fill="#ffffff"/>')

            # Black: shapely-unioned path -- adjacent squares merged, one object in Cricut
            path_d = modules_to_svg_path(item['modules'], x0, y0, ms, QR_BORDER)
            if path_d:
                black_lines.append(
                    f'  <path d="{path_d}"'
                    f' fill="#000000" fill-rule="evenodd" stroke="none"/>'
                )

        white_lines.append('</svg>')
        black_lines.append('</svg>')

        white_out = os.path.join(SVG_DIR, f"vinyl-qr-white-{g_idx}-{RUN_TS}.svg")
        black_out = os.path.join(SVG_DIR, f"vinyl-qr-black-{g_idx}-{RUN_TS}.svg")

        with open(white_out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(white_lines))
        with open(black_out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(black_lines))

        for path in (white_out, black_out):
            size = os.path.getsize(path)
            if size == 0:
                print(f"  ERROR: {path} wrote 0 bytes!")
                sys.exit(1)
            print(f"  WROTE {size:>8} bytes -> {path}")

        labels = ', '.join(item['label'] for item in group)
        print(f"  sheet {g_idx}: {labels}  ({sheet_w:.0f} x {sheet_h:.0f} mm)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Generating Cricut vinyl cut SVGs\n  output: {SVG_DIR}\n")
    font = load_font()

    print("\nWord labels:")
    generate_word_labels(font)

    print("\nQR codes:")
    qr_data = build_qr_modules()
    for item in qr_data:
        ms = QR_SIZE_MM / (item['mc'] + 2 * QR_BORDER)
        print(f"  {item['label']:15s}  v{item['version']}"
              f" ({item['mc']}x{item['mc']})  module={ms:.2f}mm")
    generate_qr_sheets(font, qr_data)

    print("\nDone.")
    print("\nCricut Design Space workflow:")
    print("  1. Open each SVG -- delete 'preview-bg' rect before cutting")
    print("  2. vinyl-word-labels.svg    -- WHITE vinyl")
    print("  3. vinyl-qr-white-1.svg     -- WHITE vinyl (sheet 1, duplicate in Cricut)")
    print("  4. vinyl-qr-white-2.svg     -- WHITE vinyl (sheet 2, duplicate in Cricut)")
    print("  5. vinyl-qr-black-1.svg     -- BLACK vinyl (sheet 1, duplicate in Cricut)")
    print("  6. vinyl-qr-black-2.svg     -- BLACK vinyl (sheet 2, duplicate in Cricut)")
    print("  7. Apply white QR bases first, then align black modules to edges")


if __name__ == "__main__":
    main()
