#!/usr/bin/env python3
"""generate-status.py — Build status.json for the kiosk dashboard.

Checks Docker containers on Pi #1 (local) and Pi #2 (via SSH).
Collects system vitals from BOTH Pis: uptime, public IP, DDNS match,
Monero sync, Headscale peers, NVMe disk, CPU temp, RAM.

Output: /opt/community-node/data/community-web/status.json
Schedule: every minute via crontab for user pi on Pi #1
  * * * * * /usr/bin/python3 /usr/local/bin/generate-status.py

Requires:
  - pi user in docker group on both Pis
  - SSH key from pi@Pi1 -> pi@Pi2 (passwordless, ed25519)
"""

import json
import subprocess
import os
import time

# --- Configuration ---------------------------------------------------------
# Override with environment variables if your IPs differ from the reference build.
OUT = os.environ.get("M2_STATUS_OUT", "/opt/community-node/data/community-web/status.json")
PI2_IP = os.environ.get("M2_TACTICAL_IP", "192.168.8.20")
PI2_SSH = f"ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -o BatchMode=yes ps@{PI2_IP}"
MONERO_RPC = f"http://{PI2_IP}:18089/get_info"
HEADSCALE_DOMAIN = os.environ.get("M2_HEADSCALE_DOMAIN", "m2vpn.yourdomain.com")


def run(cmd, timeout=10):
    """Run a shell command, return stdout or empty string on any failure."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def check_in_ps(keyword, ps_output):
    """Check if a keyword appears in docker ps output. Returns 'up' or 'down'."""
    return "up" if keyword.lower() in ps_output.lower() else "down"


# --- Gather Docker container status ----------------------------------------
# One local call + one remote call — avoids per-container SSH overhead.
# --format '{{.Names}}' returns ONLY container names, one per line.
# This prevents false matches on image names (e.g. "vectorim" contains "tor").
pi1_ps = run("docker ps --format '{{.Names}}'")
pi2_ps = run(PI2_SSH + " docker ps --format '{{.Names}}'")

services = {}

# Pi #1 — local containers (comms node)
services["conduit"]     = check_in_ps("conduit", pi1_ps)
services["element"]     = check_in_ps("element", pi1_ps)
services["nginx"]       = check_in_ps("nginx", pi1_ps)
services["cloudflared"] = check_in_ps("cloudflared", pi1_ps)
services["tor"]         = check_in_ps("tor", pi1_ps)

# Pi #2 — remote containers (tactical node)
services["monerod"]    = check_in_ps("monerod", pi2_ps)
services["mosquitto"]  = check_in_ps("mosquitto", pi2_ps)
services["reticulum"]  = check_in_ps("reticulum", pi2_ps)

# Headscale and OTS both run as systemd on Pi #2 (not Docker)
_hs_status = run(PI2_SSH + " systemctl is-active headscale 2>/dev/null")
services["headscale"] = "up" if _hs_status == "active" else "down"
_ots_status = run(PI2_SSH + " systemctl is-active opentakserver 2>/dev/null")
services["opentakserver"] = "up" if _ots_status == "active" else "down"


# --- System Vitals ---------------------------------------------------------

# Uptime (Pi #1 — both Pis boot together so this represents the node)
uptime_raw = run("uptime -p")
if uptime_raw.startswith("up "):
    uptime_str = uptime_raw[3:]  # strip leading "up "
else:
    uptime_str = uptime_raw or "—"

# Public IP (one external call per minute — acceptable for status dashboard)
public_ip = run("curl -s --max-time 5 ifconfig.me") or "—"

# Tunnel health — M2 uses Cloudflare Tunnel so the Pi's public IP never
# matches any DNS record. Check clearnet reachability via the VPN health
# endpoint instead. ddns_match=True means the tunnel is up and reachable.
try:
    _url = "https://" + HEADSCALE_DOMAIN + "/health"
    _code = run("curl -sk --max-time 5 -o /dev/null -w '%{http_code}' " + _url)
    ddns_match = (_code == "200")
except Exception:
    ddns_match = None

# Headscale peers — run binary directly on Pi #2 via SSH.
# Requires passwordless sudo for headscale binary (add to /etc/sudoers.d/).
hs_peers = 0
hs_raw = run(PI2_SSH + " sudo /usr/local/bin/headscale nodes list -o json 2>/dev/null", timeout=8)
if hs_raw:
    try:
        hs_peers = len(json.loads(hs_raw))
    except Exception:
        hs_peers = 0

# Monero sync — query the restricted RPC directly over LAN (no SSH needed).
# /get_info returns height, target_height, and synchronized fields.
monero_height = 0
monero_sync = 0
monero_raw = run("curl -s --max-time 5 " + MONERO_RPC)
if monero_raw:
    try:
        mi = json.loads(monero_raw)
        monero_height = mi.get("height", 0)
        target = mi.get("target_height", 0)
        if mi.get("synchronized", False):
            monero_sync = 100
        elif target > 0:
            monero_sync = round(monero_height / target * 100, 1)
    except Exception:
        pass

# NVMe disk usage (Pi #1 — /mnt/nvme)
disk_raw = run("df -h /mnt/nvme --output=pcent,avail 2>/dev/null | tail -1")
disk_parts = disk_raw.split()
disk_usage = disk_parts[0] if len(disk_parts) >= 1 else "—"
disk_free = (disk_parts[1] + " free") if len(disk_parts) >= 2 else "—"

# CPU temperature (Pi #1 — thermal zone 0 is the SoC)
temp_raw = run("cat /sys/class/thermal/thermal_zone0/temp")
if temp_raw and temp_raw.isdigit():
    cpu_temp = str(round(int(temp_raw) / 1000, 1)) + "°C"
else:
    cpu_temp = "—"

# RAM usage (Pi #1)
ram_raw = run("free -m | grep Mem")
ram_parts = ram_raw.split()
if len(ram_parts) >= 3:
    ram_usage = ram_parts[2] + " / " + ram_parts[1] + " MB"
else:
    ram_usage = "—"

# --- Pi #2 vitals (via SSH) ------------------------------------------------
# CPU temperature (Pi #2 — thermal zone 0 is the SoC)
pi2_temp_raw = run(PI2_SSH + " cat /sys/class/thermal/thermal_zone0/temp")
if pi2_temp_raw and pi2_temp_raw.isdigit():
    pi2_cpu_temp = str(round(int(pi2_temp_raw) / 1000, 1)) + "°C"
else:
    pi2_cpu_temp = "—"

# RAM usage (Pi #2)
pi2_ram_raw = run(PI2_SSH + " free -m | grep Mem")
pi2_ram_parts = pi2_ram_raw.split()
if len(pi2_ram_parts) >= 3:
    pi2_ram_usage = pi2_ram_parts[2] + " / " + pi2_ram_parts[1] + " MB"
else:
    pi2_ram_usage = "—"

# NVMe disk usage (Pi #2 — /mnt/nvme)
pi2_disk_raw = run(PI2_SSH + " df -h /mnt/nvme --output=pcent,avail 2>/dev/null | tail -1")
pi2_disk_parts = pi2_disk_raw.split()
pi2_disk_usage = pi2_disk_parts[0] if len(pi2_disk_parts) >= 1 else "—"
pi2_disk_free = (pi2_disk_parts[1] + " free") if len(pi2_disk_parts) >= 2 else "—"


# --- Write output ----------------------------------------------------------
status = {
    "generated_at": int(time.time()),
    "services": services,
    "uptime": uptime_str,
    "public_ip": public_ip,
    "ddns_match": ddns_match,
    "headscale_peers": hs_peers,
    "monero_sync": monero_sync,
    "monero_height": monero_height,
    "pi1": {
        "disk_usage": disk_usage,
        "disk_free": disk_free,
        "cpu_temp": cpu_temp,
        "ram_usage": ram_usage
    },
    "pi2": {
        "disk_usage": pi2_disk_usage,
        "disk_free": pi2_disk_free,
        "cpu_temp": pi2_cpu_temp,
        "ram_usage": pi2_ram_usage
    }
}

# Atomic write — temp file + rename prevents the kiosk from reading partial JSON
tmp = OUT + ".tmp"
with open(tmp, "w") as f:
    json.dump(status, f)
os.rename(tmp, OUT)
