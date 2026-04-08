#!/usr/bin/env python3
"""Generate Cricut-ready SVGs for M2 rack side panel QR stickers.

Two-layer vinyl cut approach for white QR on black acrylic:
  Layer 1: White vinyl — full 3" square (background + quiet zone)
  Layer 2: Black vinyl — QR dark modules only, same 3" scale

Both layers use real-world dimensions (inches) for direct import
into Cricut Design Space without scaling.

Also generates a text label SVG for white vinyl cut.

Usage:
    pip install qrcode
    python generate_rack_label.py
"""

import os
import sys

try:
    import qrcode
except ImportError:
    print("ERROR: qrcode library not installed.")
    print("Run:  pip install qrcode")
    sys.exit(1)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "svg")
COMMUNITY_PAGE_URL = "http://192.168.8.10:8081"


def generate_qr_layers():
    """Generate two-layer SVGs for a 3-inch vinyl-cut QR code."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=4,
    )
    qr.add_data(COMMUNITY_PAGE_URL)
    qr.make(fit=True)

    modules = qr.modules_count  # 25 for v2
    total = modules + 8  # +4 quiet zone each side = 33
    module_inch = 3.0 / total

    print(f"  QR version: {qr.version} ({modules}x{modules} modules)")
    print(f"  Total with quiet zone: {total}x{total}")
    print(f"  Module size at 3\": {module_inch:.3f}in ({module_inch * 25.4:.2f}mm)")

    # ── Layer 1: White base (full square) ────────────────────────────
    # Cut from white vinyl. This is the background.
    white_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="3in" height="3in" viewBox="0 0 {total} {total}">\n'
        f'  <rect width="{total}" height="{total}" fill="#000000"/>\n'
        f'</svg>'
    )

    white_path = os.path.join(OUTPUT_DIR, "qr-vinyl-white-base.svg")
    with open(white_path, "w") as f:
        f.write(white_svg)
    print(f"\n  qr-vinyl-white-base.svg -> {white_path}")
    print(f"    3\" white square — cut from WHITE permanent vinyl")

    # ── Layer 2: Black modules ───────────────────────────────────────
    # Cut from black vinyl, applied on top of the white base.
    # Only the dark modules are present — everything else is cut away.
    black_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="3in" height="3in" viewBox="0 0 {total} {total}">',
    ]

    for r, row in enumerate(qr.modules):
        for c, is_dark in enumerate(row):
            if is_dark:
                black_lines.append(
                    f'  <rect x="{c + 4}" y="{r + 4}" '
                    f'width="1" height="1" fill="#000000"/>'
                )

    black_lines.append('</svg>')

    black_path = os.path.join(OUTPUT_DIR, "qr-vinyl-black-modules.svg")
    with open(black_path, "w") as f:
        f.write("\n".join(black_lines))
    print(f"  qr-vinyl-black-modules.svg -> {black_path}")
    print(f"    3\" dark modules only — cut from BLACK permanent vinyl")
    print(f"    Layer on top of the white base, aligned to edges")


def generate_label_text():
    """Generate text label SVGs for white vinyl cut — one per side panel.

    Sized to sit below the 3\" QR code on a side panel.
    Width matches QR (3\"), height ~1.25\" for two lines of text.
    """
    # viewBox units: 300 wide x 125 tall (maps to 3" x 1.25")
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="3in" height="1.25in" viewBox="0 0 300 125">
  <text x="150" y="45" text-anchor="middle" font-family="Impact, 'Arial Black', 'Helvetica Neue', sans-serif" font-size="32" font-weight="900" fill="#000000" letter-spacing="2">COMMUNITY PAGE</text>
  <text x="150" y="92" text-anchor="middle" font-family="Impact, 'Arial Black', 'Helvetica Neue', sans-serif" font-size="24" font-weight="900" fill="#000000">192.168.8.10:8081</text>
</svg>'''

    filepath = os.path.join(OUTPUT_DIR, "rack-label-text.svg")
    with open(filepath, "w") as f:
        f.write(svg)
    print(f"\n  rack-label-text.svg -> {filepath}")
    print(f"    3\" x 1.25\" — cut from WHITE permanent vinyl")
    print(f"    Place below QR code on each side panel")


def main():
    print("Generating rack side panel sticker SVGs...\n")
    generate_qr_layers()
    generate_label_text()

    print(f"\n  Assembly (same sticker for both sides):")
    print(f"  +-------------------+")
    print(f"  |                   |")
    print(f"  |   [QR 3x3\"]       |  1. White base (white vinyl)")
    print(f"  |                   |  2. Black modules on top (black vinyl)")
    print(f"  |                   |")
    print(f"  +-------------------+")
    print(f"  | COMMUNITY PAGE     |  3. Text label (white vinyl)")
    print(f"  | 192.168.8.10:8081 |")
    print(f"  +-------------------+")
    print(f"     Total: 3\" x ~4.25\"")
    print(f"\n  Cut 2 of everything (one per side)")
    print(f"  Clean acrylic with IPA before applying")


if __name__ == "__main__":
    main()
