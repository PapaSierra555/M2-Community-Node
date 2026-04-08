# Network Customization Guide

The reference build uses `192.168.8.x` with a GL.iNet AXT1800 router. If your hardware or network topology differs, this guide tells you exactly what to change and where.

---

## When Do You Need This?

You need to customize the network configuration if:

- Your router uses a different default subnet (e.g., 192.168.1.x, 10.0.0.x)
- You already have a 192.168.8.x network and need to avoid a conflict
- You are using a different router model
- You want to use a different IP address for either Pi

If you are starting fresh with a GL.iNet AXT1800, you can keep the defaults and skip this doc.

---

## Step 1 — Choose Your Addresses

Decide on your values before changing anything:

```
Router (gateway):   ___.___.___.___ (e.g., 10.0.1.1)
Pi #1 (comms):      ___.___.___.___ (e.g., 10.0.1.10)
Pi #2 (tactical):   ___.___.___.___ (e.g., 10.0.1.20)
DHCP range start:   ___.___.___.___ (e.g., 10.0.1.100)
DHCP range end:     ___.___.___.___ (e.g., 10.0.1.200)
Subnet mask:        255.255.255.0 (/24)
```

Write these into `instance.conf` before proceeding:

```ini
GATEWAY_IP=10.0.1.1
NODE1_IP=10.0.1.10
NODE2_IP=10.0.1.20
SUBNET=10.0.0.0/24
```

All generation scripts (QR codes, vinyl labels, status page) will pick up the new values automatically.

---

## Step 2 — Router Configuration

### GL.iNet AXT1800 (Reference Hardware)

1. Connect to router admin: `http://192.168.8.1` (default)
2. Navigate to **Network > LAN**
3. Change **IP Address** to your new gateway IP (e.g., `10.0.1.1`)
4. Change **Start** and **End** IP for DHCP range (e.g., `10.0.1.100` to `10.0.1.200`)
5. Save and apply

**Warning:** After changing the LAN IP, the admin panel URL changes to the new gateway IP. You will lose your current browser session. Reconnect at `http://10.0.1.1` (or your new gateway IP).

### Other Routers (OpenWrt, pfSense, etc.)

Change the same settings in your router's interface:
- LAN interface IP address
- DHCP server range (must not overlap with static IP range)
- Default gateway for DHCP clients (should be the router's own IP)

---

## Step 3 — Static IP Assignment

Assign static IPs to both Pis. Two methods:

### Method A — DHCP Reservation (Recommended)

In your router, reserve a fixed IP for each Pi's MAC address:
1. Boot Pis on DHCP first
2. Find their assigned IPs and MAC addresses in router's device list
3. Create reservations: Pi #1 MAC → your Node1 IP, Pi #2 MAC → your Node2 IP
4. Reboot Pis to apply

### Method B — Static IP on the Pi Itself

Pi OS Bookworm uses NetworkManager (not dhcpcd). Configure via `nmcli`:

```bash
# Pi #1 — set static IP on eth0
sudo nmcli con mod "Wired connection 1" ipv4.addresses 10.0.1.10/24
sudo nmcli con mod "Wired connection 1" ipv4.gateway 10.0.1.1
sudo nmcli con mod "Wired connection 1" ipv4.dns "10.0.1.1 1.1.1.1"
sudo nmcli con mod "Wired connection 1" ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

```bash
# Pi #2 — set static IP on eth0
sudo nmcli con mod "Wired connection 1" ipv4.addresses 10.0.1.20/24
sudo nmcli con mod "Wired connection 1" ipv4.gateway 10.0.1.1
sudo nmcli con mod "Wired connection 1" ipv4.dns "10.0.1.1 1.1.1.1"
sudo nmcli con mod "Wired connection 1" ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

> If the connection name differs, run `nmcli con show` first to find the exact name.

Verify: `ip addr show eth0` — should reflect the new static IP immediately.

---

## Step 4 — Files to Update

The following files contain hardcoded IP addresses that scripts do not automatically update. You must edit these manually.

### docker-compose.yml

Search for all occurrences of the old IP. Replace with your Node 1 IP:

```bash
# Find all occurrences
grep -n "192.168.8" docker-compose.yml
```

Specific known locations:
- Internal network definitions
- Service host overrides
- Environment variable defaults

### nginx.conf (inside /opt/community-node/config/nginx/)

Upstream server addresses reference the Pi #1 IP for internal routing. If you changed the internal Docker network, update those addresses.

### OTS Configuration (Pi #2)

OTS server address must be updated in:
- `/opt/opentakserver/config/opentakserver.cfg` — `OTS_IP` or equivalent
- Any client data packages (atak-connect.zip) must be regenerated

### HTML Files

`index.html`, `kiosk.html`, and `atak-connect.html` contain hardcoded IPs for LAN links. Update these:

```bash
# From project root — search all HTML files
grep -rn "192.168.8" *.html
```

Replace all occurrences with your new IPs. After editing, redeploy the HTML files to the Pi.

### Headscale Configuration

If using Headscale, update the subnet routes it advertises:
```bash
headscale routes list
headscale routes enable -r <route-id>
```

The route must match your new subnet (e.g., `10.0.0.0/24`).

---

## Step 5 — Regenerate All Artifacts

After updating `instance.conf` and the files above:

```bash
# Regenerate QR codes for document/PDF use
python scripts/generate_qr.py
```

**For vinyl cutting:** do not use the script-generated QR SVGs. Use [mini-qr](https://github.com/lyqht/mini-qr) instead — it produces organic, weedable QR codes that work reliably with Cricut Design Space. The master URL list and config for this project are in `svg/WebQrCodes/qr-url-list.csv`. See `docs/QR_CODES.md` for the full workflow.

The PDF generators (build book, runbook, field card) embed IPs from instance.conf — regenerate those too if you are distributing printed materials.

---

## Step 6 — Test Connectivity

From a device on the new network:

```bash
# Can you reach the router?
ping 10.0.1.1

# Can you reach Pi #1?
ping 10.0.1.10

# Can you reach Pi #2?
ping 10.0.1.20

# Can you reach Element Web?
curl -I http://10.0.1.10:8080

# Can you reach OTS?
curl -I http://10.0.1.20:8080
```

---

## Common Pitfalls

**AP Isolation resets after router config change.**
Every time you change WiFi settings on the GL.iNet, `ap_isolate` gets forced back to 1. Run the fix after any router change:
```bash
ssh root@10.0.1.1
hostapd_cli -i wlan0 set ap_isolate 0
hostapd_cli -i wlan1 set ap_isolate 0
```

**Docker internal network conflicts.**
Docker uses `172.20.0.0/24` internally by default (set in docker-compose.yml). This rarely conflicts with a 192.168.x.x or 10.x.x.x LAN, but if it does, change the `networks:` block in docker-compose.yml to a different 172.x.x.x range.

**Monero RPC address.**
`monerod.conf` restricts RPC to `127.0.0.1` by default (correct for security). If you move Monero to a different host, update `rpc-bind-ip` in `monerod.conf`. Do not expose Monero RPC to the public internet.

**OTS reports wrong server address to ATAK clients.**
After changing IPs, OTS may continue advertising the old IP in its data packages. Regenerate the enrollment package and reissue to all ATAK users.
