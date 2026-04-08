#!/usr/bin/env python3
"""Generate QR code SVG files for the Community Node visitor page.

Run this script whenever URLs or WiFi credentials change.
All deployment-specific values are read from instance.conf in the project root.
Copy instance.conf.template to instance.conf and fill in your values.

Usage:
    pip install qrcode
    python scripts/generate_qr.py

Output files are written to svg/ in the project root.
Deploy them alongside index.html to the Pi.
"""

import os
import sys
from instance_config import cfg

# QR code appearance
MODULE_COLOR = "#000000"
BG_COLOR     = "#ffffff"
QUIET_ZONE   = 4
SCALE        = 4

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "svg")

try:
    import qrcode
    import qrcode.image.svg
except ImportError:
    print("ERROR: qrcode library not installed.")
    print("Run:  pip install qrcode")
    sys.exit(1)


def generate_svg_qr(data, filename, box_size=SCALE, border=QUIET_ZONE):
    """Generate a QR code and save as SVG."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # SvgPathFillImage: white background rect + black path overlay.
    factory = qrcode.image.svg.SvgPathFillImage
    img = qr.make_image(image_factory=factory, fill_color=MODULE_COLOR, back_color=BG_COLOR)

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath)
    print(f"  {filename} (v{qr.version}, {qr.modules_count}x{qr.modules_count})")


def main():
    print("Generating QR code SVGs for Community Node...\n")

    generate_svg_qr(cfg["WIFI_QR_STRING"],        "qr-wifi.svg")
    generate_svg_qr(cfg["ELEMENT_LAN_URL"],        "qr-element-lan.svg")
    generate_svg_qr(f"https://{cfg['ELEMENT_DOMAIN']}", "qr-element-clearnet.svg")
    generate_svg_qr(cfg["TOR_ELEMENT_URL"],        "qr-tor-element.svg")
    generate_svg_qr(cfg["TOR_COMMUNITY_URL"],      "qr-tor-community.svg")
    generate_svg_qr("https://play.google.com/store/apps/details?id=com.atakmap.app.civ",
                                                   "qr-atak-android.svg")
    generate_svg_qr("https://apps.apple.com/us/app/itak/id1558773892",
                                                   "qr-itak-ios.svg")
    generate_svg_qr("https://github.com/meshtastic/ATAK-Plugin/releases",
                                                   "qr-meshtastic.svg")
    generate_svg_qr("https://play.google.com/store/apps/details?id=se.lublin.mumla",
                                                   "qr-mumla.svg")
    generate_svg_qr(cfg["COMMUNITY_PAGE_URL"],     "qr-community-page.svg")
    generate_svg_qr(cfg["ATAK_ENROLL_URL"],        "qr-atak-connect.svg")

    print(f"\nDone. Deploy svg/ alongside index.html to the Pi.")

    if not cfg["WIFI_PASSWORD"]:
        print("\n  WARNING: WIFI_PASSWORD is not set.")
        print("  Add WIFI_PASSWORD=yourpassword to instance.conf")


if __name__ == "__main__":
    main()
