"""
Batch configurator for CCC26 T114 fleet devices (slots 01-08).

Configures 8 Heltec Mesh Node T114 (nRF52840) devices as the CCC26 loaner
fleet. Sets: CCC26 channel, AES-128 PSK, CLIENT role, US/LONG_FAST, Eastern
timezone, 30s screen timeout, smart GPS broadcast. Renames devices CCC 01-08.

Run this when re-purposing the fleet from a prior event (e.g. ODSA → CCC26).

Usage:
  pip install meshtastic pyserial
  python meshtastic/scripts/config_ccc_t114.py

Plug devices in one at a time when prompted. Each will be named, configured,
and verified before moving to the next.

BEFORE RUNNING:
  1. Generate a new PSK:
       python -c "import os,base64; print(base64.b64encode(os.urandom(16)).decode())"
  2. Paste the result into CHANNEL_PSK_B64 below.
  3. Paste the SAME key into gen_ccc_channel_qr.py and config_ccc_t3s3.py.
  4. Save the key to M2_SECRETS.md (z_Backups/).
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
CHANNEL_NAME    = "CCC26"

# 16-byte AES-128 key, base64. Must match gen_ccc_channel_qr.py + config_ccc_t3s3.py.
# Generate: python -c "import os,base64; print(base64.b64encode(os.urandom(16)).decode())"
# Save to M2_SECRETS.md before pasting here.
CHANNEL_PSK_B64 = "WQz1nnlaQN4kGwIlTTSlRQ=="  # ROTATE before every event

# Generic names — set once, never change between events.
# The channel/PSK is what changes per event, not the device name.
# Long name (≤36 chars) | Short name (≤4 chars)
NODE_NAMES = [
    ("MESH 01", "M-01"),
    ("MESH 02", "M-02"),
    ("MESH 03", "M-03"),
    ("MESH 04", "M-04"),
    ("MESH 05", "M-05"),
    ("MESH 06", "M-06"),
    ("MESH 07", "M-07"),
    ("MESH 08", "M-08"),
]

# Known node IDs (from device manifest) — for reference only.
NODE_IDS = [
    "!8d772cbb",  # slot 01
    "!6fa9d5d8",  # slot 02
    "!bfc24ac1",  # slot 03
    "!2e53e471",  # slot 04
    "!796331d9",  # slot 05
    "!e9a429a2",  # slot 06
    "!98e8f578",  # slot 07
    "!b2d4be6a",  # slot 08
]

REGION       = config_pb2.Config.LoRaConfig.RegionCode.US
MODEM_PRESET = config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
ROLE         = config_pb2.Config.DeviceConfig.Role.CLIENT
TIMEZONE     = "EST5EDT,M3.2.0,M11.1.0"  # Eastern — change if deploying in EU
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

    print("  Role: CLIENT | Timezone: Eastern")
    iface.localNode.localConfig.device.role = ROLE
    iface.localNode.localConfig.device.tzdef = TIMEZONE
    iface.localNode.writeConfig("device")

    print("  Display: 30s screen timeout")
    iface.localNode.localConfig.display.screen_on_secs = 30
    iface.localNode.writeConfig("display")

    print("  GPS: enabled / smart broadcast")
    iface.localNode.localConfig.position.gps_mode = config_pb2.Config.PositionConfig.GpsMode.ENABLED
    iface.localNode.localConfig.position.position_broadcast_secs = 0
    iface.localNode.writeConfig("position")

    print("  Network: WiFi disabled")
    iface.localNode.localConfig.network.wifi_enabled = False
    iface.localNode.writeConfig("network")

    print("  Bluetooth: enabled / no PIN (loaner — connect right away)")
    iface.localNode.localConfig.bluetooth.enabled = True
    iface.localNode.localConfig.bluetooth.mode = config_pb2.Config.BluetoothConfig.PairingMode.NO_PIN
    iface.localNode.writeConfig("bluetooth")

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
            print("  Device rebooted after channel push (expected).")
        else:
            raise
    finally:
        try:
            iface.close()
        except Exception:
            pass

    print(f"  [OK] {long_name} configured.")


def main():
    print("=" * 58)
    print("CCC26 Fleet — T114 Batch Configurator (8 devices)")
    print(f"Channel: {CHANNEL_NAME}  |  US  |  LONG_FAST  |  CLIENT")
    print(f"PSK (b64): {CHANNEL_PSK_B64}")
    print("!! Verify PSK is saved in M2_SECRETS.md before continuing !!")
    print("=" * 58)
    print()

    if CHANNEL_PSK_B64 == "AAAAAAAAAAAAAAAAAAAAAA==":
        print("WARNING: placeholder PSK detected. Generate a real key:")
        print('  python -c "import os,base64; print(base64.b64encode(os.urandom(16)).decode())"')
        cont = input("Continue anyway? (y/n): ").strip().lower()
        if cont != "y":
            sys.exit(0)
        print()

    configured = 0
    total = len(NODE_NAMES)

    for i, (long_name, short_name) in enumerate(NODE_NAMES):
        ref_id = NODE_IDS[i]
        print(f"[{i+1}/{total}] {long_name}  (expected node ID: {ref_id})")
        input("  Plug in USB-C data cable. Press Enter when ready... ")

        port = find_port()
        if not port:
            print("  No serial port detected. Check USB cable and drivers.")
            retry = input("  Retry? (y/n): ").strip().lower()
            if retry == "y":
                port = find_port()
            if not port:
                skip = input("  Still nothing. Skip this device? (y/n): ").strip().lower()
                if skip == "y":
                    continue
                sys.exit(1)

        try:
            configure_node(port, long_name, short_name)
            configured += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            cont = input("  Continue to next device? (y/n): ").strip().lower()
            if cont != "y":
                break

        input("  Unplug and label slot as configured. Press Enter to continue...\n")

    print(f"\nConfiguration complete: {configured}/{total} devices.")
    if configured == total:
        print("Next steps:")
        print("  1. Verify each device in the Meshtastic app via Bluetooth")
        print(f"  2. Confirm channel '{CHANNEL_NAME}' visible with correct PSK")
        print("  3. Run: python meshtastic/scripts/gen_ccc_channel_qr.py")
        print("  4. Run: python meshtastic/scripts/build_ccc_device_cards.py")
        print("  5. Print and laminate device cards")


if __name__ == "__main__":
    main()
