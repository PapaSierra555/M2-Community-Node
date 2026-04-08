# Mission 2 - MASTER COMMUNITY NODE PLAN
## Portable, Self-Contained, Decentralized Community Support Node

> **Version:** 1.4 
> **Platform:** Raspberry Pi 5 16GB (Node #1) + Raspberry Pi 5 16GB (Node #2) in 10" Mini-Rack — Dual Pi 5 Build
> **Pricing:** All hardware prices verified Feb 2026 from live retail sources
> **Design:** Privacy-first, censorship-resistant, field-deployable, open-source only

---

## Executive Summary

This document is the consolidated master plan for a portable, self-contained, decentralized community support node built entirely from open-source software and commodity hardware. The system fits inside a 10-inch 8U mini-rack (roughly the size of a large shoebox) and provides:

- **Encrypted group communications** -- Matrix/Conduit chat server with Element Web client, accessible over clearnet, Tor, and I2P simultaneously
- **Tactical situational awareness** -- OpenTAK Server for ATAK clients with real-time position tracking, geo-chat, map sharing, and built-in web map UI
- **Off-grid mesh networking** -- Reticulum encrypted mesh over LoRa radio (RNode) and Meshtastic consumer mesh, operational with zero internet infrastructure
- **Anonymous networking** -- Tor hidden services (.onion) and I2P eepsites (.b32.i2p) for censorship-resistant access to all services
- **Financial sovereignty** -- Monero pruned node providing a community-accessible, privacy-preserving cryptocurrency endpoint
- **Secure remote management** -- Tailscale/Headscale WireGuard mesh VPN with site-to-site tunnel back to Mission 1 home network
- **Field-deployable** -- Runs on wall power, vehicle 12V, or UPS (~1-2 hour runtime on BC600R at typical load), or solar/battery for 24+ hour autonomous operation (solar/LiFePO4 kit required — not in base BOM)

**Design Principles:** Privacy-first. Censorship-resistant. Field-deployable (<15 min to operational). Open-source only. Commodity hardware (<$1,500, standard retailers).

---

## System Architecture Overview

### Full Stack Diagram

```
                    EXTERNAL CONNECTIONS
    ================================================
    |                    |                |          |
    Clearnet          Tor (.onion)    I2P (.b32)   LoRa Radio
    (Cloudflare       (Hidden          (Eepsite)   (915 MHz)
     Tunnel)           Services)                    |
    |                    |                |          |
    ================================================
                         |
    +====================================================+
    |            GL.iNet Slate AX (Gateway)               |
    |   WiFi AP | DHCP | WireGuard | Tailscale | DNS     |
    |   WAN: Internet/Cellular/WiFi Uplink                |
    |   LAN: 192.168.8.0/24                               |
    +========================|===========================+
                             |
    +========================|===========================+
    |          TP-Link TL-SG108S (8-Port Gigabit)        |
    +====|===================|===================|=======+
         |                   |                   |
    +====|=======+    +======|========+    +====(other)====+
    | Pi 5 #1    |    | Pi 5 #2      |    | Touchscreen   |
    | (Comms)    |    | (Tactical/   |    | Monitoring    |
    |            |    |  Crypto)     |    |               |
    | Conduit    |    | OpenTAKSvr   |    +===============+
    | Element    |    | (native)     |
    | Nginx      |    | Reticulum    |
    | i2pd       |    | NomadNet     |
    | Tor        |    | Monerod      |
    | Cloudflared|    | Mosquitto    |
    |            |    | Headscale    |
    | NVMe 256GB |    | Tailscale    |
    | (GeeekPi   |    | NVMe 1TB     |
    |  dual mnt) |    | (GeeekPi     |
    +============+    |  dual mnt)   |
                      | USB LoRa x2  |
                      +==============+

    BC600R UPS (rack floor, strapped) --> PDU --> All Components
```

### Node Assignment (Recommended 2-Node Build)

| Role | Node #1 — Raspberry Pi 5 16GB (Primary Comms) | Node #2 — Raspberry Pi 5 16GB (Tactical/Crypto) |
|------|-----------------------------------------------|--------------------------------------------------|
| **Services** | Conduit (Matrix), Element Web, Nginx, i2pd, Tor, Cloudflared | OpenTAK Server (native/systemd), Reticulum, NomadNet, Monerod, Mosquitto, Headscale, Mumble, Tailscale |
| **Storage** | WD SN740 256GB M.2 2230 NVMe via GeeekPi dual mount built-in PCIe adapter | Crucial P310 1TB M.2 2230 NVMe via GeeekPi dual mount built-in PCIe adapter; both Pi 5s in same 1U bracket |
| **Network** | Static IP: 192.168.8.10 | Static IP: 192.168.8.20 |
| **Hardware Add-ons** | None — NVMe via GeeekPi dual mount (no separate M.2 HAT+ needed) | Heltec V3 USB (RNode/Reticulum, $19.90) → USB 2.0 port 1 (LEFT panel position); Heltec V3 USB (Meshtastic, $19.90) → USB 2.0 port 2 (RIGHT panel position) — both identical hardware, differentiated by firmware |
| **Key advantage** | Lightweight ARM for always-on comms | Both nodes on NVMe — 3.5–7× IOPS vs USB SATA; Monero LMDB pre-sync workaround eliminates field-sync wait |

### Network Topology

```
Internet/Cell ------> [GL.iNet Slate AX :WAN] -----+
                       |  192.168.8.1               |
                       |  DHCP: 192.168.8.100-200   |
                       |  WiFi: "CommunityNode"     |
                       |  Tailscale subnet router    |
                       +----> LAN Port 1 -----> [TP-Link Switch Port 1]
                                                     |
                                  Port 2: Pi 5 #1 (Comms)  -- 192.168.8.10
                                  Port 3: Pi 5 #2 (Tactical) -- 192.168.8.20
                                  Port 4: Touchscreen (if networked)
                                  Port 5-8: Spare (field devices)
```

---

## Service Inventory

Complete table of all services across the entire stack:

| Service | Purpose | Docker Image | RAM (Typical) | RAM (Limit) | Storage | Port(s) | Privacy Layer | Node |
|---------|---------|-------------|---------------|-------------|---------|---------|---------------|------|
| **Conduit** | Matrix chat server (Rust) | `matrixconduit/matrix-conduit:v0.10.12` | 100-200 MB | 512 MB | 500 MB - 5 GB | 6167 | Clearnet, Tor, I2P | #1 | Note: matrixconduit/matrix-conduit is abandoned as of 2025. Active community fork is conduwuit. Plan migration post-CCC26. |
| **Element Web** | Matrix web client | `vectorim/element-web:v1.12.11` | 20-30 MB | 64 MB | 50 MB | 80 (via Nginx) | Clearnet, Tor, I2P | #1 |
| **Nginx** | Reverse proxy, SSL termination | `nginx:1.28.2-alpine3.23` | 20-40 MB | 128 MB | 10 MB | 80, 443, 8448, 8080, 8081 | All | #1 |
| **i2pd** | I2P router, eepsite hosting | `purplei2p/i2pd:release-2.59.0` | 60-100 MB | 256 MB | 50-200 MB | 7070, 4444, 4447, 7656 | I2P | #1 |
| **Tor** | Hidden services, SOCKS proxy | `osminogin/tor-simple:0.4.8.21` | 30-60 MB | 128 MB | 50-100 MB | 9050 | Tor | #1 |
| **Cloudflared** | Cloudflare Tunnel (clearnet) | `cloudflare/cloudflared:2026.2.0` | 30-50 MB | 128 MB | <10 MB | (outbound only) | Clearnet | #1 |
| **OpenTAK Server** | TAK/ATAK situational awareness + web map UI | Native (systemd) v1.7.9 | 300-600 MB | 1 GB | 2-5 GB | 8080, 8088, 8089, 8443, 8446 | Clearnet/VPN | #2 |
| **RabbitMQ** | Message broker for OTS | Installed with OTS | ~200 MB | 256 MB | 100 MB | 5672, 15672 | Internal | #2 |
| **Mumble** | Push-to-talk voice (OTS auth integration) | Native install | 30-50 MB | 128 MB | <50 MB | 64738 | LAN + VPN | #2 |
| **Reticulum (rnsd)** | Encrypted mesh transport daemon | `python:3.12.12-slim-bookworm` + pip | 30-80 MB | 256 MB | <50 MB | 4242, 37428 | Mesh/LoRa | #2 |
| **NomadNet** | BBS/messaging over Reticulum | `python:3.12.12-slim-bookworm` + pip | 30-50 MB | 128 MB | <10 MB | (Reticulum) | Mesh/LoRa | #2 |
| **Monerod** | Monero pruned public node | `ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5` | 1-2 GB | 4 GB | ~95 GB (pruned) | 18080 (P2P), 18089 (RPC localhost only) | Clearnet (P2P), Tor, I2P | #2 |
| **Mosquitto** | MQTT broker (Meshtastic bridge) | `eclipse-mosquitto:2.1.2` | 10-30 MB | 64 MB | <100 MB | 1883, 9001 | Internal | #2 |
| **Headscale** | Self-hosted Tailscale control | `headscale/headscale:0.28.0` | 30-50 MB | 128 MB | <100 MB | 8180, 50443 | VPN | #2 |
| **Tailscale** | WireGuard mesh VPN client | (host install) | 20-40 MB | - | <10 MB | (outbound) | VPN | #2 |

### Resource Totals by Node

| | Pi 5 #1 — Comms (192.168.8.10) | Pi 5 #2 — Tactical/Crypto (192.168.8.20) |
|---|---|---|
| **Typical RAM** | ~0.4-0.6 GB services + ~1 GB OS/Docker | ~1.8-3.2 GB services + ~1 GB OS/Docker |
| **Total Typical** | **~1.4-1.6 GB of 16 GB** | **~2.8-4.2 GB of 16 GB** |
| **Max (limits)** | ~1.2 GB (limits) + 1.2 GB (OS) = ~2.4 GB | ~6.2 GB (limits) + 1.2 GB (OS) = ~7.4 GB |
| **Headroom** | ~13.6 GB free | ~8.6 GB free |
| **Verdict** | Well within limits | Within limits; Monero sync period is the tightest |

---

## Complete Consolidated Hardware BOM

> **Full ordering reference:** See `HARDWARE_BOM.md` for the complete BOM with ASINs, verified pricing, rack layout, power budget, and thermal notes.

### Budget Build (~$889) -- Single Pi 5, Minimal Extras

> **Availability note:** RackMate T1 and 2U Touchscreen SOLD OUT at DeskPi.com (Feb 2026). Check Amazon ASINs. All prices verified Feb 2026.

| # | Category | Component | Model | Qty | Unit Price | Total | Notes |
|---|----------|-----------|-------|-----|-----------|-------|-------|
| 1 | Enclosure | 8U Rack Cabinet | GeeekPi DeskPi RackMate T1 | 1 | $119.99 | $119.99 | SOLD OUT DeskPi; Amazon B0CPLRD29P |
| 2 | Display | 2U Touchscreen | GeeekPi 7.84" 1280x400 LCD | 1 | $79.99 | $79.99 | SOLD OUT DeskPi; Amazon B0F3C5R2BZ |
| 3 | Cooling | 120mm USB Fan | GeeekPi RackMate Fan | 1 | $13 | $13 | 3-speed |
| 4 | Compute | Pi 5 16GB Board | Raspberry Pi 5 16GB | 1 | $205.00 | $205.00 | Confirmed PiShop.us Feb 2026 |
| 4a | Compute | Pi 5 Active Cooler | Official Raspberry Pi Active Cooler | 1 | $10.95 | $10.95 | Confirmed PiShop.us |
| 4b | Power | USB-C 27W PSU | USB-C PD 27W adapter | 1 | $12 | $12 | Required; 5V/5A |
| 5 | Storage | 1TB SATA SSD | Crucial BX500 CT1000BX500SSD1 | 1 | $123.99 | $123.99 | Confirmed Newegg Feb 2026 |
| 6 | Storage | USB-SATA Adapter | SABRENT EC-SSHD | 1 | $10 | $10 | USB 3.0 |
| 7 | Network | 8-Port Switch | TP-Link TL-SG108S | 1 | $27 | $27 | ~$26-28 confirmed Feb 2026 |
| 8 | Rack | 1U Switch Shelf | GeeekPi 1U Vented Shelf | 1 | $17 | $17 | Cantilever tray |
| 9 | Power | 1U Rack PDU | Tupavco TP1713 | 1 | $35 | $35 | 4 outlet, surge |
| 10 | Power | UPS | Tripp Lite INTERNET350U | 1 | $94.99 | $94.99 | Confirmed Newegg Feb 2026 |
| 11 | Network | Travel Router | GL.iNet Slate AX (AXT1800) | 1 | $119.99 | $119.99 | Confirmed GL.iNet store Feb 2026 |
| 12 | Storage | MicroSD Card | SanDisk Extreme 32GB A2 | 1 | $10 | $10 | Boot/recovery |
| 13 | Cable | Ethernet Cables | Cat6 6" 5-pack | 1 | $10 | $10 | Rack wiring |
| | | | | | **TOTAL** | **~$889** | Prices verified Feb 2026 |

### Recommended Build (~$1,385–$1,425) -- Dual Pi 5, NVMe Both Nodes, BC600R UPS Inside Rack, LabStack Panels

> **Availability note:** RackMate T1 and 2U Touchscreen SOLD OUT at DeskPi.com (Feb 2026). Check Amazon. Official Pi SSDs OUT OF STOCK — use WD SN740 (Pi #1) and Crucial P310 (Pi #2). **⚠️ Verify all prices before ordering — 2230 NVMe market is volatile.**

| # | Category | Component | Model | Qty | Est. Price | Total | Notes |
|---|----------|-----------|-------|-----|-----------|-------|-------|
| 1 | Enclosure | 8U Rack Cabinet | GeeekPi DeskPi RackMate T1 | 1 | $119.99 | $119.99 | SOLD OUT DeskPi; Amazon B0CPLRD29P |
| 2 | Display | 2U Touchscreen | GeeekPi 7.84" LCD Touch | 1 | $79.99 | $79.99 | SOLD OUT DeskPi; Amazon B0F3C5R2BZ |
| 3 | Cooling | 120mm USB Fan | GeeekPi RackMate Fan | 2 | $13 | $26 | Push-pull airflow |
| 4 | Compute | Pi 5 16GB Board #1 | Raspberry Pi 5 16GB | 1 | $205.00 | $205.00 | Node #1: Matrix, Tor, I2P; PiShop.us confirmed |
| 5 | Compute | Pi 5 Active Cooler #1 | Official Raspberry Pi Active Cooler | 1 | $10.95 | $10.95 | PiShop.us confirmed |
| 6 | Compute | Pi 5 16GB Board #2 | Raspberry Pi 5 16GB | 1 | $205.00 | $205.00 | Node #2: Monero, ATAK, Reticulum |
| 7 | Compute | Pi 5 Active Cooler #2 | Official Raspberry Pi Active Cooler | 1 | $10.95 | $10.95 | PiShop.us confirmed |
| 8 | Rack+NVMe | 1U Dual Pi 5 Mount | GeeekPi B0F7XBVV4D | 1 | ~$60 | ~$60 | Both Pi 5s in 1U; built-in PCIe NVMe adapters for each |
| 9 | Storage | Pi #1 NVMe SSD 256GB | WD SN740 256GB M.2 2230 OEM (B0C6MVP42M) | 1 | ~$40 | ~$40 | Verify price; Official Pi SSD 256GB OOS ($75) |
| 10 | Storage | Pi #2 NVMe SSD 1TB | Crucial P310 1TB M.2 2230 (CT1000P310SSD2) | 1 | ~$115-150 | ~$130 | In stock Feb 2026; verify price |
| 11 | Power | GaN Multi-Port Charger | Anker 747 GaNPrime 150W (B09W2PNLX7) | 1 | ~$65 | ~$65 | 150W pool; C1→Pi#1 (27W), C2→Pi#2 (27W), C3→GL.iNet (15W), USB-A→display; 1 PDU outlet |
| 12 | Network | 8-Port Switch | TP-Link TL-SG108S | 1 | $27 | $27 | ~$26-28 confirmed Feb 2026 |
| 13 | Rack | 1U Switch Shelf | GeeekPi 1U Vented Shelf | 1 | $17 | $17 | Switch + GL.iNet side by side |
| 14 | Power | 1U Rack PDU | Tupavco TP1713 | 1 | $35 | $35 | 4 outlet, surge |
| 15 | Power | UPS | Tripp Lite BC600R 600VA | 1 | ~$70 | ~$70 | Sits on rack floor strapped; 10.04"×7.09"×2.28" |
| 16 | Network | Travel Router | GL.iNet Slate AX (AXT1800) | 1 | $119.99 | $119.99 | Confirmed GL.iNet store Feb 2026 |
| 17 | Radio | LoRa USB — RNode | Heltec WiFi LoRa 32 V3 915MHz | 1 | $19.90 | $19.90 | LEFT panel position; flash with RNode firmware |
| 18 | Radio | LoRa USB — Mesh | Heltec WiFi LoRa 32 V3 915MHz | 1 | $19.90 | $19.90 | heltec.org confirmed; Meshtastic |
| 19 | Radio | LoRa Antennas | 915 MHz SMA, 2-pack | 1 | $12 | $12 | One per radio |
| 20 | Storage | MicroSD Card x2 | SanDisk Extreme 32GB A2 | 2 | $10 | $20 | Boot/recovery for both Pi nodes |
| 21 | Cable | Ethernet Cables | Cat6 6" 5-pack | 1 | $10 | $10 | Rack cable management |
| 22 | Cable | Micro HDMI Adapters | 2-pack | 1 | $8 | $8 | For both Pi 5 nodes |
| 23 | Cable | USB-A to USB-C Cables | 1ft, 2-pack | 1 | $8 | $8 | LoRa radios directly to Pi #2 USB 3.0 ports |
| 24 | Cable | Velcro Cable Ties | 50-pack | 1 | $6 | $6 | Cable management + BC600R floor straps |
| 25 | Rack | 1U Vented Blank | GeeekPi 1U Blank | 1 | $10 | $10 | U1 bottom intake |
| 26 | Rack | LabStack SMA Panel | 1U Mini 2x Keystone 2x SMA Right Mount (3D print) | 1 | ~$2 | ~$2 | github.com/JaredC01/LabStack; U4 front rails |
| 27 | Radio | SMA Bulkhead Connectors | SMA female chassis mount, 2-pack | 1 | ~$8 | ~$8 | Panel feedthroughs for LoRa antennas |
| 28 | Radio | SMA Jumper Cables | SMA male-to-male RG316, 6–12", 2-pack | 1 | ~$8 | ~$8 | Radio board to panel interior connection |
| 29 | Rack | LabStack Rear Fan Panel | 2U Mini 2x 80mm Fan Panel (3D print) | 1 | ~$2 | ~$2 | github.com/JaredC01/LabStack; U4-U5 rear rails |
| 30 | Cooling | 80mm USB Fans | GDSTIME / ELUTENG 80mm USB 5V, 2-pack | 1 | ~$15 | ~$15 | Rear exhaust behind Pi nodes; U4-U5 rear |
| | | | | | **TOTAL** | **~$1,385–$1,425** | ⚠️ Verify SSD prices before ordering |

### Premium Build (~$1,705–$1,785) -- Managed Switch, Second SSD, Cellular, Case

| # | Category | Component | Model | Qty | Unit Price | Total | Notes |
|---|----------|-----------|-------|-----|-----------|-------|-------|
| 1-30 | | All Recommended items | (see above) | | | ~$1,385–$1,425 | |
| 31 | Network | Switch Upgrade | TP-Link TL-SG108E (managed) | 1 | +$10 | +$10 | VLAN support, QoS, port mirroring; replaces #12 |
| 32 | Storage | Expansion USB SSD | Samsung T7 1TB USB 3.2 | 1 | ~$90 | ~$90 | Pi #2 backups/overflow via USB; no adapter needed |
| 33 | Network | USB Cellular Modem | Quectel RM520N-GL (5G) | 1 | $85 | $85 | Field cellular backhaul |
| 34 | Transport | Carrying Case | Pelican 1610 Protector Case | 1 | $180–$220 | $200 | Interior 21.78"×16.69"×10.62" — fits T1 rack (11"W×7.8"D×16"H) laid flat with UPS attached; ~2.8" depth clearance for foam |
| 35 | Transport | Kaizen Foam Insert | 2" thick, custom-cut | 1 | $20 | $20 | Shock protection; cut to rack profile |
| | | | | | **TOTAL** | **~$1,705–$1,785** | Prices verified Feb 2026 |

### Optional: LoRa Radio Add-on Kit (~$66 for node, ~$28-40 per member)

| Item | Purpose | Price |
|------|---------|-------|
| Heltec V3 × 1 | RNode for Reticulum LoRa (LEFT panel position) | $19.90 |
| Heltec V3 x1 | Meshtastic node (MQTT bridge) | $18 |
| 915 MHz antenna x2 | One per radio | $20 |
| USB-A to USB-C cables x2 | Connect radios to Pi | $8 |
| **Node radio subtotal** | | **~$66** |

Per community member: Heltec V3 or T-Beam ($18-30) + antenna ($10) = **~$28-40 each**

### Optional: Solar Field Kit (~$335-505)

| Component | Specification | Price |
|-----------|--------------|-------|
| LiFePO4 Battery | 12V 100Ah (1,280Wh) | $200-300 |
| Solar Panel | 100W monocrystalline, foldable | $80-120 |
| Solar Charge Controller | 20A MPPT | $40-60 |
| 12V to 5V DC-DC Converter | Buck converter, 10A, USB-C PD | $15-25 |
| **Solar kit subtotal** | | **~$335-505** |

---

## Docker Compose Master Stack

This is the consolidated `docker-compose.yml` combining all services from all four specialist reports into a single coherent stack. In the recommended 2-node build, this file is split across both Pi 5s. The compose file below represents the complete logical stack; deploy the appropriate services section on each node.

### Pi 5 Node #1 -- docker-compose.yml (Comms)

```yaml
# =============================================================================
# Mission 2 Community Node -- Pi 5 #1 (Primary Communications)
# File: /opt/community-node/docker-compose.yml
# =============================================================================

networks:
  community-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  tor-net:
    driver: bridge
    internal: true
  i2p-net:
    driver: bridge
    internal: true

volumes:
  conduit-data:
  i2pd-data:
  tor-data:
  element-web:

services:
  # ==== MATRIX SERVER - Conduit (Rust) ====
  conduit:
    image: matrixconduit/matrix-conduit:${CONDUIT_VERSION:-v0.10.12}
    container_name: conduit
    restart: unless-stopped
    environment:
      CONDUIT_SERVER_NAME: ${MATRIX_SERVER_NAME:-community.local}
      CONDUIT_DATABASE_BACKEND: rocksdb
      CONDUIT_DATABASE_PATH: /var/lib/conduit/db
      CONDUIT_PORT: 6167
      CONDUIT_ADDRESS: 0.0.0.0
      CONDUIT_ALLOW_REGISTRATION: "false"  # set true only for events; use registration_token
      CONDUIT_REGISTRATION_TOKEN: ${REGISTRATION_TOKEN}
      CONDUIT_ALLOW_FEDERATION: "true"
      CONDUIT_TRUSTED_SERVERS: '["matrix.org"]'
      CONDUIT_MAX_REQUEST_SIZE: 20000000
      CONDUIT_LOG: info
    volumes:
      - conduit-data:/var/lib/conduit
    networks:
      community-net:
        ipv4_address: 172.20.0.10
      tor-net:
      i2p-net:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 128M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6167/_matrix/client/versions"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ==== ELEMENT WEB - Matrix Client ====
  element-web:
    image: vectorim/element-web:${ELEMENT_VERSION:-v1.12.11}
    container_name: element-web
    restart: unless-stopped
    volumes:
      - ./config/element/element-config.json:/app/config.json:ro
    networks:
      community-net:
        ipv4_address: 172.20.0.11
    deploy:
      resources:
        limits:
          memory: 64M
        reservations:
          memory: 32M
    depends_on:
      conduit:
        condition: service_healthy

  # ==== NGINX - Reverse Proxy ====
  nginx:
    image: nginx:1.28.2-alpine3.23
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8448:8448"
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/nginx/ssl:/etc/nginx/ssl:ro
      - ./data/community-web:/var/www/community:ro
    networks:
      community-net:
        ipv4_address: 172.20.0.2
      tor-net:
      i2p-net:
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 32M
    depends_on:
      - conduit
      - element-web

  # ==== I2PD - I2P Router (C++) ====
  i2pd:
    image: purplei2p/i2pd:${I2PD_VERSION:-release-2.59.0}
    container_name: i2pd
    restart: unless-stopped
    ports:
      - "7070:7070"
      - "4444:4444"
      - "4447:4447"
      - "7656:7656"
    volumes:
      - i2pd-data:/var/lib/i2pd
      - ./config/i2pd/i2pd.conf:/etc/i2pd/i2pd.conf:ro
      - ./config/i2pd/tunnels.conf:/etc/i2pd/tunnels.conf:ro
    networks:
      community-net:
        ipv4_address: 172.20.0.20
      i2p-net:
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 64M

  # ==== TOR - Hidden Services ====
  tor:
    image: osminogin/tor-simple:0.4.8.21
    container_name: tor
    restart: unless-stopped
    volumes:
      - tor-data:/var/lib/tor
      - ./config/tor/torrc:/etc/tor/torrc:ro
    networks:
      community-net:
        ipv4_address: 172.20.0.30
      tor-net:
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 32M
    depends_on:
      - nginx

  # ==== CLOUDFLARE TUNNEL - Clearnet Access ====
  cloudflared:
    image: cloudflare/cloudflared:2026.2.0
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel run
    environment:
      TUNNEL_TOKEN: ${CLOUDFLARE_TUNNEL_TOKEN}
    volumes:
      - ./config/cloudflared/config.yml:/etc/cloudflared/config.yml:ro
    networks:
      community-net:
        ipv4_address: 172.20.0.40
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 32M
    depends_on:
      - nginx
    profiles:
      - clearnet
      - full
```

### Pi 5 Node #2 -- docker-compose.yml (Tactical/Crypto)

```yaml
# =============================================================================
# Mission 2 Community Node -- Pi 5 #2 (Tactical / Crypto)
# File: /opt/community-node/docker-compose.yml
# =============================================================================

volumes:
  reticulum-config:
  nomadnet-data:
  mosquitto-config:
  mosquitto-data:
  mosquitto-log:
  headscale-config:
  headscale-data:
  monero-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/ssd/monero/data
  monero-tor-data:
  wallet-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/ssd/monero/wallets

services:
  # ==== OpenTAK Server — Situational Awareness ====
  # OTS runs NATIVELY under systemd — NOT in Docker.
  # Install: see BUILD_GUIDE.md Phase 5B
  # Status: systemctl status opentakserver
  # Ports: 8080 (HTTP UI), 8088 (CoT TCP), 8089 (CoT SSL),
  #        8443 (HTTPS UI), 8446 (cert enrollment)

  # ==== Reticulum Daemon - Encrypted Mesh Transport ====
  # WARNING: runs pip install on every startup. In air-gap/offline mode this will fail
  # on cold start. Ensure at least one successful internet-connected startup before
  # deploying air-gap. Long-term fix: build a custom image with packages baked in.
  reticulum:
    image: python:3.12.12-slim-bookworm
    container_name: reticulum-node
    restart: unless-stopped
    network_mode: host
    command: >
      bash -c "
        pip install --quiet rns nomadnet lxmf &&
        rnsd
      "
    volumes:
      - reticulum-config:/root/.reticulum
      - nomadnet-data:/root/.nomadnetwork
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    # Ports (host): 4242, 37428

  # ==== NomadNet - Terminal BBS / Messaging ====
  nomadnet:
    image: python:3.12.12-slim-bookworm
    container_name: nomadnet
    restart: unless-stopped
    network_mode: host
    command: >
      bash -c "
        pip install --quiet nomadnet &&
        nomadnet --daemon
      "
    volumes:
      - reticulum-config:/root/.reticulum
      - nomadnet-data:/root/.nomadnetwork
    depends_on:
      - reticulum

  # ==== Mosquitto MQTT - Meshtastic Bridge ====
  mosquitto:
    image: eclipse-mosquitto:2.1.2
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - mosquitto-config:/mosquitto/config
      - mosquitto-data:/mosquitto/data
      - mosquitto-log:/mosquitto/log

  # ==== Monerod - Pruned Public Node ====
  monerod:
    image: ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5
    container_name: monerod
    restart: unless-stopped
    user: "${FIXUID:-1000}:${FIXGID:-1000}"
    volumes:
      - monero-data:/home/monero/.bitmonero
    ports:
      - "18080:18080"
      # SECURITY: RPC bound to localhost only — access via Tailscale/Headscale VPN
      # 18089 NOT exposed to Docker host; remove port mapping if network_mode: host
    command:
      - --rpc-restricted-bind-ip=127.0.0.1
      - --rpc-restricted-bind-port=18089
      # Removed: --confirm-external-bind (not needed for localhost bind)
      # Removed: --public-node (incompatible with localhost-only RPC)
      - --no-igd
      - --prune-blockchain
      - --db-sync-mode=safe:sync
      - --enable-dns-blocklist
      - --out-peers=32
      - --in-peers=64
      - --limit-rate-up=1048576
      - --limit-rate-down=1048576
      - --log-level=0
      - --max-log-file-size=10485760
      - --max-log-files=3
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
        reservations:
          memory: 1G
          cpus: "0.5"
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://127.0.0.1:18089/get_info || exit 1"]
      # 18089 = restricted RPC (the port actually bound by --rpc-restricted-bind-port)
      # 18081 = unrestricted full RPC (not opened — healthcheck was wrong)
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 300s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  # ==== Monero Tor Proxy (for anonymous tx relay) ====
  monero-tor:
    image: osminogin/tor-simple:0.4.8.21
    container_name: monero-tor
    restart: unless-stopped
    volumes:
      - monero-tor-data:/var/lib/tor
      - ./torrc-monero:/etc/tor/torrc:ro
    ports:
      - "127.0.0.1:9050:9050"
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: "0.5"
    profiles:
      - full
      - tor-monero

  # ==== Monero Wallet RPC (optional) ====
  monero-wallet-rpc:
    image: ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5
    container_name: monero-wallet-rpc
    restart: unless-stopped
    user: "${FIXUID:-1000}:${FIXGID:-1000}"
    entrypoint: monero-wallet-rpc
    volumes:
      - wallet-data:/home/monero/wallets
    ports:
      - "127.0.0.1:18082:18082"
    command:
      - --rpc-bind-port=18082
      - --rpc-bind-ip=0.0.0.0
      - --confirm-external-bind
      - --daemon-address=monerod:18081
      - --wallet-dir=/home/monero/wallets
      - --rpc-login=${WALLET_RPC_USER:-monero}:${WALLET_RPC_PASS:-changeme}
    depends_on:
      monerod:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    profiles:
      - wallet

  # ==== Headscale - Self-Hosted Tailscale Control (Optional) ====
  headscale:
    # ⚠️ Breaking changes from 0.23 to 0.28 — read release notes before upgrading
    image: headscale/headscale:0.28.0
    container_name: headscale
    restart: unless-stopped
    ports:
      - "8180:8080"
      - "50443:50443"
    volumes:
      - headscale-config:/etc/headscale
      - headscale-data:/var/lib/headscale
    command: headscale serve
    environment:
      - TZ=${TZ:-America/New_York}
    profiles:
      - headscale
      - full
```

### Compose Profiles Summary

| Profile | Services Started | Use Case |
|---------|-----------------|----------|
| (default) | All core services except profiled ones | Normal operation |
| `clearnet` | + Cloudflared | Internet-connected, public access |
| `full` | + Cloudflared + Monero Tor + Headscale | Everything running |
| `tor-monero` | + Monero Tor proxy | Anonymous Monero relay |
| `wallet` | + Monero Wallet RPC | Programmatic wallet access |
| `headscale` | + Headscale control server | Self-hosted VPN coordination |

**Launch examples:**
```bash
# Standard operation (all core, no clearnet)
docker compose up -d

# Full stack with clearnet access
docker compose --profile full up -d

# Air-gap mode (only Matrix + Element + Nginx on Node #1)
docker compose up -d conduit element-web nginx

# Tactical only (mesh on Node #2; OTS runs under systemd separately)
docker compose up -d reticulum nomadnet mosquitto
```

---

## Network Architecture Inside the Rack

### IP Address Assignments

| Device | IP Address | Role |
|--------|-----------|------|
| GL.iNet Slate AX | 192.168.8.1 | Gateway, DHCP server, WiFi AP, DNS |
| Pi 5 #1 (Comms) | 192.168.8.10 | Matrix, Tor, I2P, Nginx, Cloudflared |
| Pi 5 #2 (Tactical) | 192.168.8.20 | OTS (native), Reticulum, Monero, MQTT, Mumble |
| Touchscreen | 192.168.8.30 | Dashboard display (if networked) |
| DHCP Range | 192.168.8.100-200 | Client devices (WiFi/wired) |
| Tailscale (Pi #1) | 100.x.y.z (auto) | Mesh VPN overlay |
| Tailscale (Pi #2) | 100.x.y.w (auto) | Mesh VPN overlay |

### GL.iNet Slate AX Configuration

| Function | Configuration |
|----------|--------------|
| **DHCP Server** | Subnet: 192.168.8.0/24, Range: .100-.200 |
| **Static Leases** | Pi #1 = .10, Pi #2 = .20, Touchscreen = .30 |
| **WiFi AP** | SSID: "CommunityNode", WPA3, 5GHz preferred |
| **WireGuard Server** | Enabled for direct VPN access without Tailscale |
| **Tailscale** | Subnet router advertising 192.168.8.0/24 |
| **DNS** | AdGuard Home for ad/tracker blocking |
| **Firewall** | WAN isolation; only Cloudflare Tunnel outbound |

### DNS Configuration

- **GL.iNet runs AdGuard Home** as the DNS server for all LAN/WiFi clients
- **Upstream DNS**: Cloudflare (1.1.1.1) or Quad9 (9.9.9.9) over DNS-over-HTTPS
- **Local DNS entries**: `matrix.community.local` -> 192.168.8.10, `tak.community.local` -> 192.168.8.20
- **MagicDNS via Tailscale**: `community-node-1.tailnet.ts.net`, `community-node-2.tailnet.ts.net`

### Outbound Connectivity Paths

| Path | Method | Purpose |
|------|--------|---------|
| **Clearnet** | Cloudflare Tunnel (outbound HTTPS) | Matrix federation, public access |
| **Tailscale** | WireGuard (outbound UDP) | Remote admin, M1 integration |
| **Tor** | SOCKS proxy (outbound TCP) | Anonymous .onion services |
| **I2P** | i2pd (outbound UDP/TCP) | Anonymous .b32.i2p eepsites |
| **LoRa Mesh** | 915 MHz radio (RNode/Meshtastic) | Off-grid comms, no internet |

### Antenna Architecture

| Radio | Frequency | Antenna | Mounting |
|---|---|---|---|
| GL.iNet Slate AX — 2.4 GHz WiFi | 2400–2484 MHz | Internal PCB — no mod needed | Inside router, radiates through open-frame rack |
| GL.iNet Slate AX — 5 GHz WiFi | 5150–5850 MHz | Internal PCB — no mod needed | Inside router, radiates through open-frame rack |
| Heltec V3 LEFT (RNode/Reticulum) | 902–928 MHz (US915) | 915 MHz SMA whip, ~3 dBi | External — custom LoRa panel, U8 front, bulkhead #1 (ANT 1) |
| Heltec V3 RIGHT (Meshtastic) | 902–928 MHz (US915) | 915 MHz SMA whip, ~3 dBi | External — custom LoRa panel, U8 front, bulkhead #2 (ANT 2) |

**WiFi vs. LoRa coexistence:** No frequency conflict. The 2.4 GHz and 5 GHz WiFi bands do not overlap with the 902–928 MHz LoRa band. Internal WiFi antennas and external LoRa antennas coexist without interference regardless of physical proximity.

**RNode vs. Meshtastic coexistence:** Both LoRa radios share the US915 band. Stock firmware defaults place them on different channels (Reticulum RNode: ~915.0 MHz; Meshtastic LongFast: ~906.875 MHz) — the ~8 MHz separation prevents receiver desensitization. No configuration change needed when using defaults. If you change either radio's channel, maintain at least 5 MHz separation between the two operating frequencies.

---

## Power & Runtime Summary

### Total Power Budget

| Component | Idle (W) | Load (W) |
|-----------|---------|---------|
| Raspberry Pi 5 16GB (Node #1) | 3.5 | 10.0 |
| Raspberry Pi 5 16GB (Node #2) | 3.5 | 10.0 |
| TP-Link TL-SG108S | 3.5 | 3.5 |
| GL.iNet Slate AX | 5.0 | 7.0 |
| 7.84" Touchscreen | 6.0 | 8.0 |
| WD SN740 256GB NVMe (Pi #1 via GeeekPi mount PCIe) | 0.8 | 1.8 |
| Crucial P310 1TB NVMe (Pi #2 via GeeekPi mount PCIe) | 1.0 | 2.2 |
| 120mm USB Fan | 1.5 | 2.0 |
| 2× Heltec V3 (USB LoRa, direct to Pi #2) | 0.2 | 0.8 |
| 2× 80mm USB Fans (LabStack rear panel, U4-U5 rear) | 1.0 | 1.5 |
| **TOTAL** | **~26W** | **~48.5W** |

### UPS Runtime

| UPS Model | Capacity | Idle (26W) | Typical (35W) | Load (48.5W) |
|-----------|----------|-----------|--------------|-----------|
| Tripp Lite BC600R (~$70) *(recommended — inside rack)* | 600VA/300W (~60Wh) | ~138 min | ~103 min | ~74 min |
| Tripp Lite INTERNET350U ($94.99) *(budget — external)* | 350VA/210W (~50Wh) | ~120 min | ~91 min | ~64 min |

### Solar Field Kit -- 24-Hour Autonomous Operation

- **Typical load:** ~35W (dual Pi 5 build)
- **24h energy requirement:** 840Wh (+ 20% losses = ~1,010Wh)
- **LiFePO4 12V 100Ah battery:** 1,280Wh capacity -- covers full 24h+ even without sun
- **100W solar panel (6h effective):** Generates ~600Wh/day, extending runtime to 48h+
- **Skip the UPS** in solar deployment; the LiFePO4 battery IS the UPS

### Power-Saving Tips

- Turn off touchscreen when not needed (saves 6-8W, adds ~20 min UPS runtime)
- Set Pi 5 CPU governor to `powersave` when idle
- Disable WiFi on GL.iNet in wired-only scenarios
- Put LoRa in receive-only mode (0.1W vs 0.5W)

---

## Field Deployment Procedures

### Setup Procedure (Target: Under 15 Minutes)

**Step 1: Unpack and Place Rack (2 min)**
- Remove rack from carrying case / transport container
- Place on stable, level surface with ventilation clearance (minimum 4" on all sides)
- Verify all components seated properly (no loose cables from transport)

**Step 2: Connect Power (2 min)**
- **Wall power:** Wall outlet -> UPS -> PDU -> all components
- **Vehicle:** 12V cigarette lighter -> inverter -> UPS -> PDU
- **Solar/battery:** LiFePO4 -> DC-DC converter -> USB-C PD to each Pi; 12V to PDU for switch/router
- Verify UPS LED indicates power OK

**Step 3: Connect Network Uplink (2 min)**
- **Wired:** Ethernet from existing router/modem -> GL.iNet WAN port
- **WiFi repeater:** Configure GL.iNet to repeat existing WiFi as WAN
- **Cellular:** USB modem or phone USB tethering -> GL.iNet
- **Air-gap:** Skip this step; node operates on local WiFi only

**Step 4: Power-On Sequence (3 min)**
1. UPS -> ON
2. PDU -> ON (all outlets)
3. Wait for switch link lights (5 seconds)
4. Pi nodes auto-boot; Docker services auto-start
5. GL.iNet boots and broadcasts WiFi SSID

**Step 5: Verify Services (3 min)**
- Touchscreen should display dashboard within 60 seconds of Pi boot
- Check Docker service status: `docker compose ps` on each node (via SSH or touchscreen terminal)
- Verify Matrix: `curl -s http://192.168.8.10:6167/_matrix/client/versions`
- Verify OTS: `systemctl is-active opentakserver` or web UI at `http://192.168.8.20:8080`
- Verify Monero: `curl -s http://127.0.0.1:18089/get_info` (run from Pi #2 — RPC is bound to localhost only)

**Step 6: Connect Field Devices (3 min)**
- Connect phones/laptops to "CommunityNode" WiFi
- ATAK clients: connect to 192.168.8.20:8088 (TCP) or :8089 (TLS)
- Matrix: open Element Web at `http://192.168.8.10:8080` or use native app pointed at the server
- Remote users: join via Tailscale and access services by Tailscale IP

### Shutdown Procedure

1. Notify all connected users: "Node shutting down in 2 minutes"
2. On Node #2 (Pi 5 #2): `docker compose down` (stops Monero cleanly — important for DB integrity)
3. On Node #1 (Pi 5 #1): `docker compose down`
4. Wait for all container stop confirmations (30 seconds)
5. `sudo shutdown now` on Pi 5 #1; `sudo shutdown now` on Pi 5 #2
6. Wait for both Pi 5 activity LEDs to go dark (15-20 seconds)
7. PDU -> OFF
8. UPS -> OFF
9. Disconnect uplink and power cables
10. Pack rack into carrying case

### Emergency Air-Gap Procedure

When you need to immediately disconnect from all external networks:

1. **Physical:** Unplug the Ethernet cable from GL.iNet WAN port
2. **WiFi WAN:** In GL.iNet admin (192.168.8.1), disable repeater/WAN WiFi
3. **Tailscale:** `sudo tailscale down` on both Pi 5 nodes
4. **Cloudflare Tunnel:** `docker compose stop cloudflared` on Pi #1 (192.168.8.10)
5. **Monero P2P:** `docker compose stop monerod` on Pi #2 (192.168.8.20) (stops all peer connections)
6. **Verify isolation:** `ip route` should show no default gateway to external networks

**Remaining operational services in air-gap mode:**
- Matrix (local federation disabled, local chat still works)
- Element Web (local access via WiFi)
- NomadNet + Reticulum (works over LoRa radio, no internet needed)
- Meshtastic mesh (LoRa, fully offline)
- OTS/ATAK (local WiFi, no internet federation)

---

## Integration with Mission 1 Home Network

### WireGuard Site-to-Site Tunnel

As defined in the M1 PACE plan, a persistent WireGuard tunnel connects M2 back to M1:

```ini
# On M2 Pi (client) -- /etc/wireguard/wg-home.conf
[Interface]
PrivateKey = <MISSION2_PRIVATE_KEY>
Address = 10.10.10.2/32
DNS = 10.0.0.1

[Peer]
# Mission 1 Home Server
PublicKey = <MISSION1_PUBLIC_KEY>
Endpoint = home.example.org:51820
AllowedIPs = 10.0.0.0/24, YOUR_HOME_LAN_CIDR
PersistentKeepalive = 25
```

### Tailscale Shared Tailnet

Both M1 and M2 nodes join the same Tailscale tailnet (or Headscale instance):

```
Mission 1 (Home)                    Mission 2 (Portable)
+-----------------+    Tailscale    +------------------+
| Proxmox Host    |<-- WireGuard -->| Raspberry Pi 5   |
| 10.10.0.0/24    |    Tunnel       | 192.168.8.0/24   |
+-----------------+                 +------------------+
      |                                    |
  Home LAN                          Community LAN
  (subnet routed)                   (subnet routed)
```

- M2 Pi nodes advertise `192.168.8.0/24` as a subnet route
- M1 Proxmox advertises `10.10.0.0/24` as a subnet route
- All devices on either network can reach services on the other

### M2 Services Accessible from M1

| M2 Service | Access from M1 | Method |
|------------|---------------|--------|
| Matrix/Element | `http://community-node-1.tailnet:8080` | Tailscale MagicDNS |
| OTS Web UI | `http://community-node-2.tailnet:8080` | Tailscale MagicDNS |
| Monero RPC | `http://community-node-2.tailnet:18089` | Tailscale only (RPC is localhost on Pi #2; not LAN-accessible) |
| i2pd Console | `http://community-node-1.tailnet:7070` | Tailscale (admin) |
| SSH (both nodes) | `ssh pi@community-node-{1,2}.tailnet` | Tailscale |

### Remote Access Architecture (Non-LAN Users)

Two tiers of remote access for operators outside the CommunityNode WiFi range:

| Tier | Who | Method | What They Get |
|---|---|---|---|
| Web map (view) | Anyone with URL | Cloudflare Tunnel → `tak.yourdomain.com` | Live OTS map, markers, data packages in browser |
| Full ATAK | Approved operators | Headscale VPN → ATAK to `192.168.8.20:8088` | Complete CoT: PLI, GeoChat, ExCheck, voice, plugins |

**Cloudflare Tunnel** runs on Pi #1 (comms) as `cloudflared` container. Routes HTTP requests for `tak.yourdomain.com` to OTS web UI on Pi #2 (`http://192.168.8.20:8080`). Protected by Cloudflare Access zero-trust (email one-time PIN, free tier, 50 users). No ports opened.

**Headscale VPN** runs on Pi #2 (tactical) as `headscale` container. One public port (TCP 443) for the control plane. Remote ATAK operators install Tailscale, receive a pre-auth key, and join the encrypted WireGuard mesh. Once connected, all `192.168.8.x` services are reachable as if on local WiFi. Operator-controlled: keys are created with expiration (24h for incidents, 90d for permanent team), revoked after events.

**Use case:** Support team mobilizing from a non-impacted area begins coordination immediately — web map for situational awareness, full ATAK once Tailscale is installed. When they arrive on-site, they switch to CommunityNode WiFi for direct LAN access.

### Backup Flow: M2 -> M1 NAS

Automated backup via Tailscale tunnel:

```bash
# Cron job on M2 Pi nodes (runs daily at 03:00)
# Backs up critical configs and data to M1 NAS over Tailscale
0 3 * * * rsync -avz --delete \
  /opt/community-node/config/ \
  /opt/community-node/.env \
  /opt/community-node/data/tor/ \
  /opt/community-node/data/i2pd/ \
  pi@<m1-nas-tailscale-ip>:/backup/community-node/
```

---

## Security Hardening Checklist

- [ ] Change all default passwords (Matrix registration token, Monero wallet RPC, GL.iNet admin, Pi user accounts)
- [ ] Disable password auth on SSH -- keys only (`PasswordAuthentication no` in sshd_config)
- [ ] Bind Docker container ports to specific IPs (not 0.0.0.0)
- [ ] Monero RPC in restricted mode only (port 18089, never expose 18081)
- [ ] Monero Wallet RPC bound to localhost only (127.0.0.1:18082)
- [ ] Tor hidden service keys backed up to encrypted USB drive
- [ ] I2P tunnel keys backed up alongside Tor keys
- [ ] Matrix server registration requires token (invite-only in sensitive deployments)
- [ ] GL.iNet admin interface accessible on LAN only (not over WiFi to clients)
- [ ] Nginx rate limiting configured (10r/s general, 30r/s Matrix)
- [ ] Docker containers run with memory/CPU limits enforced
- [ ] Config files mounted read-only (`:ro`) where possible
- [ ] LUKS full-disk encryption on NVMe and SATA SSDs
- [ ] Regular software updates: `docker compose pull && docker compose up -d`
- [ ] Log rotation configured (prevent storage exhaustion)
- [ ] No Tor exit node -- hidden services and SOCKS proxy only
- [ ] Separate Matrix accounts for clearnet vs anonymous access
- [ ] DNS blocklist enabled on Monero (`--enable-dns-blocklist`)
- [ ] Firewall on GL.iNet: WAN isolation, no inbound port forwarding (Cloudflare Tunnel handles ingress)

---

## Community Operator Training Guide Outline

**Target audience:** Non-technical community members
**Duration:** 1-2 hours hands-on orientation

### 1. What This System Does and Does Not Do (15 min)
- Provides: encrypted chat, situational awareness maps, off-grid messaging, private financial transactions
- Does NOT provide: anonymity guarantees (requires operational discipline), 100% uptime, internet access for general browsing
- Threat model overview: who are we protecting against, what are the limits

### 2. Starting Up and Shutting Down (15 min)
- Power-on sequence (step by step with labels on the rack)
- How to verify services are running (touchscreen dashboard)
- Clean shutdown procedure (why it matters for Monero DB integrity)
- Emergency power-off (just unplug -- services are designed to recover)

### 3. Connecting to Matrix and TAK (20 min)
- Installing Element app (iOS/Android) and pointing at community server
- Registering a Matrix account with the community token
- Joining default rooms
- Installing ATAK and connecting to OpenTAK Server
- Understanding the map view, sending position, geo-chat

### 4. Understanding the Mesh Radio (15 min)
- What Meshtastic is and how LoRa works (plain language)
- Pairing a Meshtastic device with your phone
- Sending messages when there is no internet
- Range expectations and antenna basics

### 5. Privacy Practices -- What NOT to Do (15 min)
- Do not reuse usernames from other platforms
- Do not share .onion/.i2p addresses on clearnet social media
- Do not connect personal email to Matrix accounts
- Do not disable encryption in Matrix rooms
- Do not run the node as a Tor exit (explain why)
- Operational security basics for the deployment context

### 6. Troubleshooting Common Issues (10 min)
- "I can't connect to WiFi" -- check SSID, check GL.iNet
- "Matrix is slow" -- check internet uplink, check Pi CPU usage
- "ATAK shows no other users" -- verify OTS is running (`systemctl is-active opentakserver`), check web UI at port 8080
- "Meshtastic not connecting" -- check Bluetooth pairing, check USB connection
- "Monero sync stuck" -- normal if initial sync; check disk space

### 7. When to Contact Technical Support (5 min)
- Red flags: touchscreen shows errors, Pi won't boot, no services responding after reboot
- How to collect logs: `docker compose logs > /tmp/debug.log`
- Contact methods: Matrix room, Tailscale SSH, physical access

---

## Phased Build Plan

### Phase 1: Core Communications (Week 1-2)
**Goal:** Encrypted chat accessible locally and remotely

- Assemble rack with single Pi 5 (or both if purchased)
- Install Raspberry Pi OS, Docker, base configuration
- Deploy Conduit + Element Web + Nginx on Pi #1
- Configure GL.iNet as WiFi AP and DHCP server
- Install Tailscale on Pi and GL.iNet
- Set up Cloudflare Tunnel for clearnet Matrix federation
- **Milestone:** Users can join Matrix chat via WiFi or Tailscale

### Phase 2: Anonymity Layer (Week 2-3)
**Goal:** Services accessible via Tor and I2P

- Deploy Tor hidden services for Matrix and Element Web
- Deploy i2pd with eepsite tunnels
- Configure NomadNet pages (community bulletin board)
- Test .onion and .b32.i2p access from Tor Browser / I2P client
- **Milestone:** All comms services accessible anonymously

### Phase 3: Tactical (Week 3-4)
**Goal:** ATAK situational awareness and LoRa mesh

- Deploy OpenTAK Server (native) on Pi #2
- Flash RNode firmware on Heltec V3 (LEFT board) for Reticulum
- Flash Meshtastic firmware on Heltec V3
- Configure Mosquitto MQTT broker for Meshtastic bridge
- Configure Reticulum daemon with LoRa interface
- Test ATAK client connections and Meshtastic mesh
- **Milestone:** Field team can share positions and messages over LoRa with no internet

### Phase 4: Crypto (Week 4-6)
**Goal:** Monero pruned node operational

- **Pre-sync blockchain on x86 machine** (2-4 days on fast hardware)
- Copy LMDB database to Pi #2's 1TB NVMe (`/mnt/nvme/monero/data/`) via rsync
- Deploy monerod Docker container with pruned node configuration
- Verify sync completion and restricted RPC accessibility
- Configure Tor hidden service for Monero RPC (optional)
- Test wallet connections (Feather, Cake Wallet, Monerujo)
- **Milestone:** Community members can connect their wallets to the node

---

## Cost Summary

| Build Tier | Total | Description |
|-----------|-------|-------------|
| **Budget** | **~$889** | Single Pi 5, USB SATA storage, external UPS |
| **Recommended** | **~$1,385–$1,425** | Dual Pi 5, NVMe both nodes (GeeekPi dual mount), BC600R inside rack, USB LoRa, LabStack SMA+fan panels, Anker 747 GaN charger |
| **Premium** | **~$1,705–$1,785** | Adds managed switch upgrade, USB expansion SSD, cellular modem, Pelican 1610 transport case |
| **Premium + Solar** | **~$2,034–$2,284** | Add solar panel, LiFePO4 battery, charge controller for 24h+ autonomy |
| **Premium + Solar + Radio Kits (5 members)** | **~$2,174–$2,484** | Full system + 5 community member radio kits (~$28-40 each) |

**Context:** Comparable enterprise portable comms kits (Harris PRC-163, Persistent Systems MPU5) cost $10,000–$50,000+. This community node delivers encrypted mesh comms, tactical SA, financial sovereignty, and anonymous networking for under $1,500 in commodity hardware with $0 in software licensing.

**Price notes (verified Feb 2026):**
- **Pi 5 16GB: $205.00 confirmed** at PiShop.us — up ~40% from mid-2025 (LPDDR4 shortages)
- **⚠️ Official Pi SSDs: OUT OF STOCK** — use WD SN740 256GB OEM (~$40) for Pi #1 and Crucial P310 1TB (~$115-150) for Pi #2
- **⚠️ M.2 2230 NVMe prices are volatile** — verify before ordering
- **GL.iNet Slate AX: $119.99 confirmed** at GL.iNet official store
- **Tripp Lite BC600R: ~$70** at DigiKey; verify at Amazon
- **GeeekPi RackMate T1 + 2U Touchscreen: SOLD OUT** at DeskPi.com — check Amazon B0CPLRD29P and B0F3C5R2BZ
- Sales events (Prime Day, Black Friday) can reduce totals by 10-15%
- All software is FOSS — $0 recurring licensing; Tailscale free tier supports up to 100 devices

---

## Appendix A: Port Reference (All Services)

| Port | Protocol | Service | Node | Access |
|------|----------|---------|------|--------|
| 80 | TCP | Nginx (HTTP redirect) | #1 | LAN |
| 443 | TCP | Nginx (HTTPS / Matrix) | #1 | LAN + Cloudflare |
| 1883 | TCP | Mosquitto MQTT | #2 | LAN |
| 4242 | TCP | Reticulum TCP transport | #2 | LAN + Internet |
| 4444 | TCP | i2pd HTTP proxy | #1 | LAN |
| 4447 | TCP | i2pd SOCKS proxy | #1 | LAN |
| 5672 | TCP | RabbitMQ (OTS internal) | #2 | Internal |
| 6167 | TCP | Conduit Matrix server | #1 | Internal (via Nginx) |
| 7070 | TCP | i2pd Web Console | #1 | LAN (admin) |
| 7656 | TCP | i2pd SAM bridge | #1 | Internal |
| 8080 | TCP | Element Web (via Nginx, #1) / OTS Web UI (#2) | #1/#2 | LAN + Tor/I2P / VPN + Cloudflare |
| 8081 | TCP | Community web (via Nginx) | #1 | LAN + Tor/I2P |
| 8088 | TCP | OTS CoT streaming (TCP) | #2 | LAN + Tailscale |
| 8089 | TCP | OTS CoT streaming (SSL) | #2 | LAN + Tailscale |
| 8180 | TCP | Headscale Web | #2 | LAN (admin) |
| 8443 | TCP | OTS Web UI (HTTPS) | #2 | LAN + Tailscale |
| 8446 | TCP | OTS Certificate Enrollment | #2 | LAN + Tailscale |
| 8448 | TCP | Matrix federation | #1 | LAN + Cloudflare |
| 9001 | TCP | Mosquitto WebSocket | #2 | LAN |
| 9050 | TCP | Tor SOCKS proxy | #1/#2 | Localhost |
| 18080 | TCP | Monero P2P | #2 | Internet |
| 18081 | TCP | Monero Full RPC | #2 | Localhost ONLY |
| 18082 | TCP | Monero Wallet RPC | #2 | Localhost ONLY |
| 18089 | TCP | Monero Restricted RPC | #2 | Localhost (Pi #2) only — not LAN-accessible; access via Tailscale SSH tunnel |
| 15672 | TCP | RabbitMQ Management | #2 | LAN (admin) |
| 64738 | TCP/UDP | Mumble voice server | #2 | LAN + VPN |
| 37428 | TCP | Reticulum shared instance | #2 | Localhost |
| 50443 | TCP | Headscale gRPC | #2 | LAN (admin) |

## Appendix B: Rack Layout Diagram

### Front View

```
+==========================================+
|          GeeekPi 8U RackMate T1          |
|          (Front View, Top-Down)          |
+==========================================+
|                                          |
|  U8  [ 120mm USB Fan (exhaust)      ]   |
|                                          |
|  U7  [ ---- OPEN ----               ]   |     PDU on REAR rails
|                                          |
|  U6  [ TP-Link Switch + GL.iNet     ]   |
|      [ (side by side on 1U shelf)   ]   |
|                                          |
|  U5  [ GeeekPi 1U Dual Pi 5 Mount   ]   |
|      [ Pi #1 (Comms) | Pi #2 (TAK)  ]   |
|      [ 256GB NVMe    | 1TB NVMe     ]   |
|                                          |
|  U4  [ LabStack 1U SMA Panel (3D)    ]   |
|      [ 2x SMA bulkhead — antennas   ]   |
|                                          |
|  U3  [                               ]   |
|      [ 2U Touchscreen (7.84" LCD)    ]   |
|  U2  [                               ]   |
|                                          |
|  U1  [ Vented Panel / Intake Fan     ]   |
|                                          |
+==========================================+
|  [ Tripp Lite BC600R — rack floor    ]  |
|  [ strapped with velcro (self-cont.) ]  |
+==========================================+
```

### Rear View

```
+==========================================+
|          GeeekPi 8U RackMate T1          |
|          (Rear View, Top-Down)           |
+==========================================+
|                                          |
|  U8  [ 120mm fan motor (front mount) ]   |
|                                          |
|  U7  [ PDU (rear rails, outlets in)  ]   |     adapters rest on UPS
|                                          |
|  U6  [ Switch rear ports / GL.iNet   ]   |
|                                          |
|  U5  [ LabStack 2U 80mm Fan Panel    ]   |
|      [ Fan 1 (80mm USB 5V)           ]   |
|  U4  [ Fan 2 (80mm USB 5V) — cont.   ]   |
|      [ 2x fans exhaust Pi heat rearw.]   |
|                                          |
|  U3  [ SMA panel rear / ant. cables  ]   |
|      [ 2U Touchscreen rear (cables)  ]   |
|  U2  [                               ]   |
|                                          |
|  U1  [ Vented blank (rear open)      ]   |
|                                          |
+==========================================+
|  [ BC600R UPS rear — PDU adapters    ]  |
+==========================================+
```

> **Note:** The GeeekPi RackMate T1 is an open-frame rack — front and rear mounting at the same U positions is normal. The LabStack SMA panel (U4, front rails) and LabStack fan panel (U4-U5, rear rails) are on opposite sides of the same rails with no physical conflict. SMA bulkheads protrude ~0.75" inward, well clear of the rear-mounted fan panel.
>
> **Airflow:** Cool air enters at U1 bottom → rises through the Pi node bay → 2× 80mm rear fans (U4-U5 rear) actively exhaust Pi heat → residual rising heat exits through 120mm top fan (U8).

## Appendix C: Key File Paths

| Path | Node | Contents |
|------|------|----------|
| `/opt/community-node/` | Both | Docker Compose root, configs, data |
| `/opt/community-node/docker-compose.yml` | Both | Service definitions |
| `/opt/community-node/.env` | Both | Environment variables |
| `/opt/community-node/config/conduit/` | #1 | Conduit Matrix config |
| `/opt/community-node/config/element/` | #1 | Element Web config |
| `/opt/community-node/config/nginx/` | #1 | Nginx conf + SSL certs |
| `/opt/community-node/config/i2pd/` | #1 | i2pd.conf + tunnels.conf |
| `/opt/community-node/config/tor/` | #1 | torrc |
| `/opt/community-node/config/cloudflared/` | #1 | Cloudflare Tunnel config |
| `/opt/community-node/data/` | Both | Persistent service data |
| `/mnt/nvme/monero/data/` | #2 | Monero blockchain (LMDB) — on NVMe, not USB SATA |
| `/mnt/nvme/monero/wallets/` | #2 | Monero wallet files |
| `~/.reticulum/config` | #2 | Reticulum interface config |
| `~/.nomadnetwork/storage/pages/` | #2 | NomadNet community pages |

---

*This document consolidates the following Mission 2 specialist reports:*
- *M2_SecureComms_Matrix_I2P_Tor.md -- Matrix/Conduit, Element, i2pd, Tor, NomadNet, Cloudflare Tunnel*
- *ATAK_RETICULUM_MESH.md -- OpenTAKServer, Reticulum, LoRa, Meshtastic, Tailscale/Headscale*
- *MONERO_NODE.md -- Monero pruned node, Tor/I2P privacy, wallet infrastructure*
- *HARDWARE_BOM.md -- Hardware BOM, rack layout, power budget, thermal, field deployment*
