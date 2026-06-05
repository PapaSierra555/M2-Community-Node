"""
Batch configurator for CCC26 T3S3 personal devices (PS-01, PS-02, PS-03).

Configures 3 LilyGo T3S3 (ESP32-S3) personal system devices with the CCC26
channel and PSK. WiFi disabled. No GPS config (T3S3 uses external GPS on
pins 47/48, not controlled here).

Devices stay named PS-01/02/03 across events — the channel flash is what
switches them between ODSA and CCC contexts.

Usage:
  pip install meshtastic pyserial
  python meshtastic/scripts/config_ccc_t3s3.py

BEFORE RUNNING:
  CHANNEL_PSK_B64 must exactly match config_ccc_t114.py and gen_ccc_channel_qr.py.
  All three files are rotated together. Save the key to M2_SECRETS.md.

T3S3 bootloader entry (required before flash, not needed for config):
  Hold BOOT + tap RESET, release both. Device appears as USB serial.
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

# Must match config_ccc_t114.py and gen_ccc_channel_qr.py exactly.
CHANNEL_PSK_B64 = "WQz1nnlaQN4kGwIlTTSlRQ=="  # ROTATE before every event

NODE_NAMES = [
    ("PS-01", "PS01"),
    ("PS-02", "PS02"),
    ("PS-03", "PS03"),
]

REGION       = config_pb2.Config.LoRaConfig.RegionCode.US
MODEM_PRESET = config_pb2.Config.LoRaConfig.ModemPreset.LONG_FAST
ROLE         = config_pb2.Config.DeviceConfig.Role.CLIENT
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

    print("  Role: CLIENT | Timezone: Eastern")
    iface.localNode.localConfig.device.role = ROLE
    iface.localNode.localConfig.device.tzdef = TIMEZONE
    iface.localNode.writeConfig("device")

    print("  Display: 30s screen timeout")
    iface.localNode.localConfig.display.screen_on_secs = 30
    iface.localNode.writeConfig("display")

    print("  Network: WiFi disabled")
    iface.localNode.localConfig.network.wifi_enabled = False
    iface.localNode.writeConfig("network")

    print("  Bluetooth: enabled / no PIN")
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
    print("CCC26 Personal Devices — T3S3 Batch Configurator")
    print(f"Channel: {CHANNEL_NAME}  |  US  |  LONG_FAST  |  CLIENT")
    print(f"PSK (b64): {CHANNEL_PSK_B64}")
    print("=" * 58)
    print()

    configured = 0
    total = len(NODE_NAMES)

    for i, (long_name, short_name) in enumerate(NODE_NAMES):
        print(f"[{i+1}/{total}] {long_name}")
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

        input("  Unplug. Press Enter to continue...\n")

    print(f"\nConfiguration complete: {configured}/{total} devices.")
    if configured == total:
        print("Next steps:")
        print("  1. Verify each device in the Meshtastic app via Bluetooth")
        print(f"  2. Confirm channel '{CHANNEL_NAME}' is visible")
        print("  3. Run: python meshtastic/scripts/gen_ccc_channel_qr.py")


if __name__ == "__main__":
    main()
