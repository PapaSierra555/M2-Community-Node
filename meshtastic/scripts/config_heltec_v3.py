"""
Batch configurator for Heltec LoRa V3 Meshtastic nodes — M2 Community Node.

Configures 2 rack-mounted infrastructure nodes. Sets: CommunityNode channel,
AES-128 PSK, ROUTER role, US/LONG_FAST, Eastern timezone, 30s screen timeout.
WiFi disabled — nodes communicate via USB serial and MQTT bridge on Pi 2.
No GPS configuration (Heltec V3 has no built-in GPS).

Usage:
  pip install meshtastic pyserial
  python scripts/config_heltec_v3.py

Run before every event (PSK rotation). Update CHANNEL_PSK_B64 below AND in
scripts/gen_m2_channel_qr.py before running. Save the new PSK to M2_SECRETS.md.
"""

import sys
import time
import base64

try:
    import serial.tools.list_ports
    from meshtastic.serial_interface import SerialInterface
    from meshtastic.protobuf import config_pb2, channel_pb2
except ImportError:
    print("ERROR: Missing dependencies.")
    print("Run: pip install meshtastic pyserial")
    sys.exit(1)

# ── CONFIG ────────────────────────────────────────────────────────────────────
CHANNEL_NAME = "CommunityNode"

# 16-byte AES-128 key, base64 encoded. Must match gen_m2_channel_qr.py exactly.
# Generate a new key before each event:
#   python -c "import os,base64; print(base64.b64encode(os.urandom(16)).decode())"
# Save the result to M2_SECRETS.md before pasting it here.
CHANNEL_PSK_B64 = "+aVLpPfwX/SfD0j8Xe56cg=="  # REPLACE before every event

NODE_NAMES = [
    ("M2 Community Node 01", "M2-1"),
    ("M2 Community Node 02", "M2-2"),
]

REGION       = config_pb2.Config.LoRaConfig.RegionCode.US
MODEM_PRESET = config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
ROLE         = config_pb2.Config.DeviceConfig.Role.ROUTER
TIMEZONE     = "EST5EDT,M3.2.0,M11.1.0"
# ─────────────────────────────────────────────────────────────────────────────


def find_port():
    KEYWORDS = ["CP210", "CH340", "FTDI", "USB SERIAL", "SILICON", "CDC"]
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if any(kw in (p.description or "").upper() for kw in KEYWORDS):
            return p.device
    return ports[0].device if ports else None


def configure_node(port, long_name, short_name):
    print(f"  Connecting to {port}...")
    iface = SerialInterface(devPath=port)
    time.sleep(3)

    print(f"  Owner: {long_name} / {short_name}")
    iface.localNode.setOwner(long_name=long_name, short_name=short_name)

    print("  LoRa: US / LONG_FAST")
    iface.localNode.localConfig.lora.region = REGION
    iface.localNode.localConfig.lora.modem_preset = MODEM_PRESET
    iface.localNode.writeConfig("lora")

    print("  Role: ROUTER | Timezone: Eastern")
    iface.localNode.localConfig.device.role = ROLE
    iface.localNode.localConfig.device.tzdef = TIMEZONE
    iface.localNode.writeConfig("device")

    print("  Display: 30s screen timeout")
    iface.localNode.localConfig.display.screen_on_secs = 30
    iface.localNode.writeConfig("display")

    print("  Network: WiFi disabled (MQTT via Pi 2 serial bridge)")
    iface.localNode.localConfig.network.wifi_enabled = False
    iface.localNode.writeConfig("network")

    print(f"  Channel: {CHANNEL_NAME} (private PSK)")
    psk_bytes = base64.b64decode(CHANNEL_PSK_B64)
    iface.localNode.channels[0].settings.name = CHANNEL_NAME
    iface.localNode.channels[0].settings.psk = psk_bytes
    iface.localNode.channels[0].role = channel_pb2.Channel.Role.PRIMARY
    try:
        iface.localNode.writeChannel(0)
    except Exception as e:
        err = str(e)
        if "PermissionError" in err or "ClearCommError" in err or "disconnect" in err.lower():
            print("  Device rebooted after config push (expected).")
        else:
            raise
    finally:
        try:
            iface.close()
        except Exception:
            pass

    print(f"  [OK] {long_name} configured.")


def main():
    print("=" * 55)
    print("M2 Community Node — Heltec V3 Batch Configurator")
    print(f"Channel: {CHANNEL_NAME}  |  US  |  LONG_FAST  |  ROUTER")
    print(f"PSK (base64): {CHANNEL_PSK_B64}")
    print("!! Save this PSK in M2_SECRETS.md before continuing !!")
    print("=" * 55)
    print()

    if CHANNEL_PSK_B64 == "AAAAAAAAAAAAAAAAAAAAAA==":
        print("WARNING: Using null placeholder PSK. Generate a real key:")
        print('  python -c "import os,base64; print(base64.b64encode(os.urandom(16)).decode())"')
        cont = input("Continue anyway? (y/n): ").strip().lower()
        if cont != "y":
            sys.exit(0)
        print()

    configured = 0
    total = len(NODE_NAMES)

    for i, (long_name, short_name) in enumerate(NODE_NAMES):
        print(f"[{i+1}/{total}] Plug in node for: {long_name}")
        print("  (USB-C data cable from node to this machine — not the rack USB hub)")
        input("  Press Enter when connected and booted... ")

        port = find_port()
        if not port:
            print("  No serial port detected. Check USB cable and drivers.")
            retry = input("  Retry? (y/n): ").strip().lower()
            if retry == "y":
                port = find_port()
            if not port:
                skip = input("  Still nothing. Skip this node? (y/n): ").strip().lower()
                if skip == "y":
                    continue
                sys.exit(1)

        try:
            configure_node(port, long_name, short_name)
            configured += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            cont = input("  Continue to next node? (y/n): ").strip().lower()
            if cont != "y":
                break

        print("  Unplug and return to rack mount.\n")

    print(f"\nConfiguration complete: {configured}/{total} nodes configured.")
    if configured == total:
        print("Next steps:")
        print("  1. Verify each node in the Meshtastic app via Bluetooth")
        print(f"  2. Confirm channel {CHANNEL_NAME} is visible with the correct PSK")
        print("  3. Run: python scripts/gen_m2_channel_qr.py")
        print("  4. Print the QR card and bring it to the event")


if __name__ == "__main__":
    main()
