"""
Instance configuration loader for M2 Community Node generation scripts.

Reads instance.conf from the project root if it exists.
Falls back to the reference implementation defaults if not found.

Usage in any script:
    from instance_config import cfg
    url = cfg["ELEMENT_LAN_URL"]
"""

import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR   = os.path.dirname(_SCRIPT_DIR)
_CONF_FILE  = os.path.join(_ROOT_DIR, "instance.conf")

# Reference implementation defaults — matches yourdomain.com / 192.168.8.x build
_DEFAULTS = {
    # Network
    "NODE1_IP":               "192.168.8.10",
    "NODE2_IP":               "192.168.8.20",
    "GATEWAY_IP":             "192.168.8.1",
    "SUBNET":                 "192.168.8.0/24",

    # WiFi
    "WIFI_SSID":              "CommunityNode",
    "WIFI_SECURITY":          "WPA",
    "WIFI_PASSWORD":          "",   # Set in M2_SECRETS.md or instance.conf

    # Domain
    "BASE_DOMAIN":            "yourdomain.com",
    "ELEMENT_DOMAIN":         "element.yourdomain.com",
    "TAK_DOMAIN":             "tak.yourdomain.com",
    "HEADSCALE_DOMAIN":       "m2vpn.yourdomain.com",
    "ATAK_ENROLL_DOMAIN":     "atakenroll.yourdomain.com",

    # Service URLs (LAN)
    "ELEMENT_LAN_URL":        "http://192.168.8.10:8080",
    "COMMUNITY_PAGE_URL":     "http://192.168.8.10:8081",
    "ATAK_ENROLL_URL":        "https://atakenroll.yourdomain.com:8447/atak-connect.html",
    "MUMBLE_HOST":            "192.168.8.20",
    "MUMBLE_PORT":            "64738",
    "MONERO_RPC_HOST":        "192.168.8.20",
    "MONERO_RPC_PORT":        "18089",

    # Tor hidden services — set in instance.conf after running tor + hostname gen
    "TOR_ELEMENT_ONION":      "YOUR_ELEMENT_ONION.onion",
    "TOR_MATRIX_ONION":       "YOUR_MATRIX_ONION.onion",
    "TOR_COMMUNITY_ONION":    "YOUR_COMMUNITY_ONION.onion",

    # ATAK / OpenTAKServer
    "ATAK_TRUSTSTORE_PASS":   "atakatak",   # OTS vendor default — change if rotated
    "ATAK_ENROLL_USER":       "CHANGE_ME",  # OTS enrollment username
    "ATAK_ENROLL_PASS":       "CHANGE_ME",  # OTS enrollment password

    # Event
    "EVENT_NAME":             "YOUR_EVENT_NAME",
    "EVENT_FULL_NAME":        "Your Event Full Name",
    "EVENT_DATE":             "Month DD-DD, YYYY",
    "EVENT_LOCATION":         "City, State",
}


def _load_conf(path):
    """Parse a KEY=VALUE config file. Ignores comments and blank lines."""
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            # Strip inline comments
            if " #" in val:
                val = val[:val.index(" #")].strip()
            values[key] = val
    return values


def _build_cfg():
    overrides = _load_conf(_CONF_FILE)
    merged = dict(_DEFAULTS)
    merged.update(overrides)

    # Derived values (built from base keys so they auto-update if base changes)
    n1 = merged["NODE1_IP"]
    n2 = merged["NODE2_IP"]
    edom = merged["ELEMENT_DOMAIN"]
    adom = merged["ATAK_ENROLL_DOMAIN"]

    if "ELEMENT_LAN_URL" not in overrides:
        merged["ELEMENT_LAN_URL"] = f"http://{n1}:8080"
    if "COMMUNITY_PAGE_URL" not in overrides:
        merged["COMMUNITY_PAGE_URL"] = f"http://{n1}:8081"
    if "ATAK_ENROLL_URL" not in overrides:
        merged["ATAK_ENROLL_URL"] = f"https://{adom}:8447/atak-connect.html"
    if "MUMBLE_HOST" not in overrides:
        merged["MUMBLE_HOST"] = n2
    if "MONERO_RPC_HOST" not in overrides:
        merged["MONERO_RPC_HOST"] = n2

    # Full onion URLs (with http:// prefix)
    merged["TOR_ELEMENT_URL"]   = f"http://{merged['TOR_ELEMENT_ONION']}"
    merged["TOR_MATRIX_URL"]    = f"http://{merged['TOR_MATRIX_ONION']}"
    merged["TOR_COMMUNITY_URL"] = f"http://{merged['TOR_COMMUNITY_ONION']}"

    # WiFi string for QR codes
    merged["WIFI_QR_STRING"] = (
        f"WIFI:T:{merged['WIFI_SECURITY']};"
        f"S:{merged['WIFI_SSID']};"
        f"P:{merged['WIFI_PASSWORD']};;"
    )

    if overrides:
        print(f"  Config: instance.conf ({len(overrides)} overrides)")
    else:
        print(f"  Config: defaults (no instance.conf found — using reference build values)")

    return merged


cfg = _build_cfg()
