# Mission 2 -- ATAK Server + Reticulum Mesh Networking + Tactical Communications

> **Platform:** Raspberry Pi 5 16GB -- Portable Community Node
> **Goal:** Deploy a self-contained tactical communications hub with situational awareness (ATAK), encrypted mesh networking (Reticulum), off-grid radio (LoRa), and secure VPN overlay (Tailscale/Headscale).
> **All software is open-source.**

---

## Table of Contents

1. [OpenTAK Server (OTS)](#1-opentakserver-ots)
2. [Reticulum Network Stack](#2-reticulum-network-stack)
3. [LoRa Radio Integration (Off-Grid Mesh)](#3-lora-radio-integration-off-grid-mesh)
4. [Tailscale Mesh VPN](#4-tailscale-mesh-vpn)
5. [Meshtastic Integration](#5-meshtastic-integration)
6. [Docker Compose Stack](#6-docker-compose-stack)
7. [Hardware Add-ons BOM](#7-hardware-add-ons-bom)
8. [Integration Architecture](#8-integration-architecture)

---

## 1. OpenTAK Server (OTS)

### 1.1 What is OpenTAKServer?

OpenTAKServer (OTS) is an open-source TAK (Team Awareness Kit) server providing the server-side infrastructure for ATAK (Android Team Awareness Kit), WinTAK, and iTAK clients. It enables shared situational awareness through Cursor on Target (CoT) data exchange, with a built-in React web UI featuring a live Leaflet map, MIL-STD-2525C symbology, certificate auto-generation, and native Meshtastic gateway support.

- **Repository:** `github.com/brian7704/OpenTAKServer`
- **Website:** `opentakserver.io`
- **Current Version:** v1.7.9
- **License:** GPL-3.0

### 1.2 Core Features

| Feature | Description |
|---------|-------------|
| **CoT Streaming** | Real-time Cursor-on-Target data exchange (position, markers, routes) |
| **React Web UI** | Built-in browser-based admin with live Leaflet map and MIL-STD-2525C symbology |
| **Certificate Management** | Auto-generation of client/server certificates — no manual PKI workflow |
| **Geo-Chat** | Text messaging between all connected TAK clients |
| **Data Packages** | File sharing (maps, overlays, mission data) between clients |
| **Mission API** | Server-side mission management (ExCheck checklists, data sync) |
| **Meshtastic Gateway** | Built-in serial bridge — mesh nodes appear on web map |
| **Mumble Integration** | Built-in Mumble auth for push-to-talk voice via Mumla app |
| **Video Streaming** | MediaMTX integration for H.265/AV1 video feeds |
| **SSL/TLS** | Encrypted client-server connections with auto-generated certificates |
| **Offline Maps** | PMTiles served via built-in nginx — street-level maps with zero extra processes |

### 1.3 Default Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 8088 | TCP | CoT Streaming (client connections) |
| 8089 | TCP | CoT Streaming over TLS (encrypted) |
| 8080 | TCP | Web UI (HTTP) |
| 8443 | TCP | Web UI (HTTPS) |
| 8446 | TCP | Certificate enrollment |

### 1.4 Resource Requirements on Raspberry Pi 5

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 300 MB (OTS) + 200 MB (RabbitMQ) | 600 MB + 256 MB |
| Storage | 2 GB | ~4 GB (with FL PMTiles + DTED2 + data packages) |
| CPU | 1 core | 2 cores |
| Network | Any IP connectivity | Static IP or DHCP reservation |

OTS runs natively under systemd on the Pi 5 — no Docker container overhead. RabbitMQ runs alongside for message queuing. Total footprint is ~500-800 MB RAM typical.

### 1.5 Client Connectivity

- **ATAK (Android):** Free on Google Play. Connect to OTS IP:8088 (TCP) or IP:8089 (TLS). Certificate enrollment at IP:8446. Supports plugins.
- **WinTAK (Windows):** Available from tak.gov (free registration required). Same CoT protocol.
- **iTAK (iOS):** Connects via TAK server; can receive forwarded Meshtastic PLI via server relay.
- **Web UI:** Built-in React web UI at IP:8080 — live Leaflet map, no client install needed. Map shows connected clients only — create a static marker via `POST /api/markers` at install time so the kiosk map always shows the node's location (see Build Guide Phase 5B, Step 11).

### 1.6 ATAK/OTS Plugin Inventory

#### Tier 1 — Deploy Now (Core M2 Capabilities)

| Plugin | Source | What | Server-side |
|---|---|---|---|
| **Meshtastic ATAK Plugin** | GitHub meshtastic/ATAK-Plugin (446 stars) | Bridges ATAK CoT over LoRa mesh — PLI, GeoChat, file transfer, voice memos | Optional |
| **OTS Meshtastic Gateway** | Built into OTS | Server-side mesh-to-TAK bridge — mesh nodes appear on web map | Yes |
| **OpenTAK ICU** | GitHub brian7704/OpenTAK_ICU | Video streaming H.265/AV1, audio, encryption, background | Yes (MediaMTX) |
| **DTED.org** | snstac/DTED.org | 30m terrain data via QR scan — elevation, LOS, slope analysis | No |
| **ATAK-Maps** | GitHub joshuafuller/ATAK-Maps (MIT) | MOBAC XML sources — USGS topo, satellite, OpenTopo for offline caching | No |
| **Mumla** (standalone app) | [Play Store](https://play.google.com/store/apps/details?id=se.lublin.mumla) | Push-to-talk voice via Mumble server | Yes (Mumble) |

#### Tier 2 — High Value, Easy Setup

| Plugin | Source | What | Server-side |
|---|---|---|---|
| **ATAK Weather Plugin** | GitHub Hellikandra/ATAK-Weather-Plugin (MIT) | Open-Meteo weather data, no API key | No |
| **TAKWatch / TAKWatch-IQ** | GitHub TDF-PL/TAKWatch (GPL-3.0) | Garmin smartwatch bridge — heart rate, nav, emergency panic button | No |
| **APRSTAK** | GitHub niccellular/aprstak (GPL-3.0) | APRS ham radio positions in ATAK (many SAR teams use APRS) | No |
| **ADSBCOT** | GitHub snstac/adsbcot (Apache-2.0) | Aircraft tracking — rescue helicopters, search aircraft on map | Gateway on Pi |
| **TAK-CAD** | GitHub raytheonbbn/tak-cad (GPL-3.0) | Computer-aided dispatch for multi-team SAR operations | No |
| **OpenAthena** | Play Store (free, closed source) | Drone photo geolocation via terrain raycast — pinpoint ground coords | No |
| **WiFi2COT** | GitHub niccellular/wifi2cot (GPL-3.0) | WiFi signal mapping — locate survivors' devices in disaster areas | No |

#### Tier 3 — Specialized / As-Needed

| Plugin | Source | What | Hardware Required |
|---|---|---|---|
| **UAS Tool** | CivTAK built-in plugin | DJI drone telemetry + video | DJI drone |
| **Kraken-to-TAK** | GitHub Krakenberry/Kraken-to-TAK | Radio direction finding on TAK map | KrakenSDR (~$300-500) |
| **INRCOT** | GitHub snstac/inrcot (Apache-2.0) | Garmin inReach satellite positions | inReach + subscription |
| **BobTAK** | GitHub sniporbob/BobTAK (MIT) | HF radio CoT bridge — true beyond-LOS fallback | HF radio setup |
| **PulseCOT** | GitHub snstac/pulsecot (Apache-2.0) | 911 dispatch data on TAK map | Internet |
| **HyteraTAK** | GitHub kortel-systems/hyteratak | Hytera DMR radio GPS positions on TAK | Hytera radios |
| **ZelloCOT** | GitHub snstac/zellocot (Apache-2.0) | Zello PTT user positions on TAK | Zello accounts |
| **AISCOT** | GitHub snstac/aiscot (Apache-2.0) | Maritime vessel tracking for coastal SAR | Optional AIS receiver |

#### Built-in ATAK Capabilities (No Plugins Needed)

- **Reporting:** 9-line MEDEVAC, CasEvac, SALUTE, SITREP — all built-in
- **SAR tools:** Track logging, drawing/markup, POI markers, geofencing/alerts
- **ExCheck:** Collaborative checklists (server-synced via OTS Mission API)
- **GeoChat:** Georeferenced text messaging
- **Image sharing:** Geotagged photos as data packages
- **Weather tools:** Wind/hazmat plume modeling (manual input)
- **Elevation profile:** Line-of-sight and slope analysis (requires DTED loaded)

### 1.7 Offline Maps & Terrain Data

#### PMTiles (Kiosk Offline Map)

Extract your region from Protomaps daily builds:
```
pmtiles extract "https://build.protomaps.com/YYYYMMDD.pmtiles" region.pmtiles --bbox=WEST,SOUTH,EAST,NORTH --maxzoom=14
```

Replace `WEST,SOUTH,EAST,NORTH` with the bounding box for your deployment area (decimal degrees). Use [bboxfinder.com](http://bboxfinder.com) to get coordinates for your region. Replace `region.pmtiles` with a descriptive filename.

- Source: Protomaps daily builds (free, no account, streams only needed tiles)
- z0-14 provides street-level detail; file size varies by region (roughly 300 MB–1 GB for a US state)
- Served by OTS nginx at `/tiles/region.pmtiles` as a static file with byte-range support
- Rendered in browser by protomaps-leaflet (dark theme) — zero server-side rendering
- Kiosk location picker uses this for fully offline map display
- Falls back to online OSM raster tiles if PMTiles file is missing

> PMTiles contains **vector** tiles (MVT format). ATAK requires **raster** tiles and cannot use PMTiles directly. ATAK users should pre-cache tiles on-device when connected to WiFi, or use the ATAK-Maps plugin with MOBAC XML sources.

#### DTED2 (Elevation/Terrain for ATAK)

- Source: CivTAK OneDrive — pre-packaged SRTM by US state (manual browser download)
  - US by regions: `https://1drv.ms/u/s!AovJpJOFK1Vbgc8rtrMIBH_oXiqmAA?e=LIVl95`
  - Backup: USGS EarthExplorer (free account, select DTED output format)
- Resolution: ~30m (SRTM 1 arc-second, equivalent to DTED2); file size varies by region (~1–2 GB per US state)
- ATAK auto-loads from `/sdcard/atak/DTED/` at launch
- Pre-load on devices before deployment (multi-GB over mesh is impractical)
- OTS can distribute via data packages for WiFi-connected devices

Total storage: approximately 1.5–3 GB for a typical US state (PMTiles + DTED2) on 1TB NVMe. Trivial.

### 1.8 Native Install (systemd — not Docker)

OTS runs natively under systemd on Raspberry Pi 5. The OTS Docker ARM64 image is alpha-quality; the native Pi installer is production-ready.

```bash
# Install OpenTAKServer via the official Pi installer
# See BUILD_GUIDE.md Phase 5B for full step-by-step instructions
# including nginx port config, RabbitMQ, Meshtastic, and Mumble setup
```

> **Important:** OTS is NOT in the Docker compose file. It runs as a systemd service alongside the Docker stack. Check status with `systemctl status opentakserver`.

---

## 2. Reticulum Network Stack

### 2.1 Overview

Reticulum is a cryptography-based networking stack created by Mark Qvist. It is designed for building resilient, encrypted, hardware-agnostic communication networks that work over any medium -- LoRa radio, packet radio, WiFi, serial links, TCP/IP, I2P, or anything else that can carry data.

- **Repository:** `github.com/markqvist/Reticulum`
- **Current Version:** 1.1.3
- **License:** MIT
- **Install:** `pip install rns`

### 2.2 Key Properties

- **End-to-end encrypted** by default (X25519 + AES-256 + HMAC-SHA256)
- **No IP addresses required** -- identity-based addressing using Ed25519 keys
- **Delay/disruption tolerant** -- messages queue and forward when links are available
- **Hardware agnostic** -- runs on any transport medium
- **Minimal resources** -- runs on microcontrollers through to servers
- **Self-configuring** -- auto-discovers peers on local networks

### 2.3 Reticulum Applications

#### NomadNet (Nomad Network)

Terminal-based communications platform over Reticulum:
- Text messaging (LXMF-based)
- Distributed bulletin board / page system (like BBS over mesh)
- Node hosting -- serve pages to other NomadNet users
- File sharing
- Install: `pip install nomadnet`
- Run as daemon: `nomadnet --daemon`

#### LXMF (Lightweight Extensible Message Format)

The messaging protocol built on Reticulum:
- Store-and-forward message delivery
- Works across any Reticulum transport
- Supports text, binary data, attachments
- Delay-tolerant -- messages propagate when routes become available
- Install: `pip install lxmf`

#### Sideband (Mobile Client)

Full-featured Reticulum client for Android, Linux, macOS, and Windows:
- Graphical messaging interface
- Voice messages, image sharing, file transfers
- Real-time voice calls over Reticulum
- Distributed telemetry system with mapping
- Plugin extensibility
- Android APK available from `github.com/markqvist/Sideband`
- Also available on F-Droid

#### MeshChat (Web-based Client)

- Web-based LXMF client by Liam Cottle
- User-friendly browser interface
- Image/voice messages, file transfers
- Repository: `github.com/liamcottle/reticulum-meshchat`

### 2.4 Reticulum Interfaces

Reticulum supports multiple simultaneous interfaces. A single node can bridge between all of them.

| Interface Type | Transport Medium | Use Case |
|---------------|-----------------|----------|
| `AutoInterface` | Local network (UDP broadcast) | Auto-peer with LAN devices |
| `TCPServerInterface` | TCP/IP | Accept connections from remote nodes |
| `TCPClientInterface` | TCP/IP | Connect to remote Reticulum nodes |
| `RNodeInterface` | LoRa radio (via RNode) | Off-grid radio mesh |
| `SerialInterface` | RS-232 / USB serial | Direct cable or packet radio TNC |
| `KISSInterface` | Serial KISS TNC | Packet radio (AX.25 compatible) |
| `I2PInterface` | I2P overlay network | Anonymous transport |
| `PipeInterface` | Unix pipes | Inter-process communication |

### 2.5 Reticulum Node Configuration on Pi 5

> **Note:** This configuration was valid as of Reticulum v1.1.3. Interface names, available transports, and configuration syntax may change between versions. Always verify interface availability and current syntax against the official documentation (`rnsd --exampleconfig`) before deploying. Check `github.com/markqvist/Reticulum` for the current stable release.

The configuration file lives at `~/.reticulum/config`. Below is a community node configuration:

```ini
# Reticulum Configuration for Community Node
# ~/.reticulum/config

[reticulum]
  enable_transport = True
  share_instance = True
  shared_instance_port = 37428
  instance_control_port = 37429
  panic_on_interface_error = No

[logging]
  loglevel = 4

[interfaces]
  # Auto-discover peers on local network
  [[Default Interface]]
    type = AutoInterface
    enabled = yes

  # Accept incoming TCP connections from remote Reticulum nodes
  [[TCP Server]]
    type = TCPServerInterface
    enabled = yes
    listen_ip = 0.0.0.0
    listen_port = 4242

  # Connect to a public Reticulum transport node
  [[RNS Testnet Frankfurt]]
    type = TCPClientInterface
    enabled = yes
    target_host = frankfurt.connect.reticulum.network
    target_port = 4965

  # LoRa radio interface via RNode USB transceiver
  [[RNode LoRa]]
    type = RNodeInterface
    enabled = no
    port = /dev/ttyUSB0
    frequency = 915000000
    bandwidth = 125000
    spreadingfactor = 8
    codingrate = 5
    txpower = 17
    flow_control = True

  # Serial interface for packet radio TNC
  [[Packet Radio]]
    type = KISSInterface
    enabled = no
    port = /dev/serial/by-id/usb-FTDI_FT230X-if00-port0
    speed = 115200
    databits = 8
    parity = none
    stopbits = 1
    preamble = 150
    txtail = 10
    persistence = 200
    slottime = 20
```

### 2.6 Running Reticulum

```bash
# Install Reticulum stack
pip install rns nomadnet lxmf

# Run Reticulum daemon (background transport node)
rnsd

# Run NomadNet (interactive terminal UI)
nomadnet

# Run NomadNet as daemon (headless page/message server)
nomadnet --daemon

# Check Reticulum status
rnstatus

# Probe a Reticulum destination
rnprobe <destination_hash>

# Transfer a file
rncp <source> <destination_hash>:/path
```

---

## 3. LoRa Radio Integration (Off-Grid Mesh)

### 3.1 RNode -- Open Source LoRa Transceiver

RNode is an open-source, open-hardware LoRa transceiver designed by Mark Qvist specifically for Reticulum. It turns commodity LoRa development boards into full-featured radio interfaces.

**Supported Hardware for RNode firmware:**
- LilyGO LoRa32 v2.1 (TTGO T3 v1.6.1) -- **recommended, ~$15-25**
- LilyGO T-Beam v1.1 (with GPS) -- ~$25-35
- Heltec LoRa32 v2/v3
- RAK4631-based boards
- Any board with SX1276, SX1278, SX1262, SX1268, or SX1280 chip

**Flashing RNode firmware:**
```bash
# Install the RNode configuration utility
pip install rnodeconf

# Flash firmware to a connected board
rnodeconf --autoinstall

# The utility auto-detects the board and flashes appropriate firmware
```

**Build vs Buy:**
- DIY: Flash firmware onto a ~$20 LilyGO T3 board
- Pre-built: Available from select vendors (unsigned.io referrals)
- DIY is recommended -- it takes under 10 minutes with `rnodeconf --autoinstall`

### 3.2 Compatible LoRa HATs for Raspberry Pi 5

For direct Pi 5 integration (SPI/UART attached):

| HAT | Chip | Freq | Pi 5 Compat | Price (est.) |
|-----|------|------|-------------|-------------|
| **Waveshare SX1262 LoRa HAT** | SX1262 | 915 MHz | Yes (UART) | ~$20-25 |
| **Waveshare SX1268 LoRa HAT** | SX1268 | 868 MHz | Yes (UART) | ~$20-25 |
| **RAK2245 Pi HAT** | SX1301 | 915/868 MHz | Check (SPI) | ~$70-90 |
| **Dragino LoRa/GPS HAT** | SX1276 | 915/868 MHz | Legacy (SPI) | ~$30-40 |

**Recommendation:** For Reticulum use, a USB-connected RNode (LilyGO T3) is preferred over a Pi HAT. It is better supported, easier to position (antenna placement flexibility via USB cable), and the RNode firmware is purpose-built for Reticulum.

### 3.3 Frequency Bands and Licensing

| Region | Band | Notes |
|--------|------|-------|
| **US (FCC)** | 915 MHz ISM | License-free, 1W max EIRP |
| **EU (ETSI)** | 868 MHz ISM | License-free, duty cycle limits |
| **US (Ham)** | 70cm (420-450 MHz) | Requires amateur radio license, higher power allowed |
| **US (Ham)** | 33cm (902-928 MHz) | Requires amateur radio license |

For community deployment in the US, 915 MHz ISM band is the practical choice -- no license required.

### 3.4 Range Expectations (Reticulum over LoRa)

| Scenario | Estimated Range |
|----------|----------------|
| Urban (buildings, obstructions) | 1-3 km |
| Suburban | 3-8 km |
| Rural / clear terrain | 5-15 km |
| Elevated antenna (hilltop/tower) | 10-30+ km |
| Line of sight (mountain-to-mountain) | 30-80+ km |

Range depends heavily on antenna height, terrain, spreading factor, and bandwidth settings. Higher spreading factor = longer range but lower throughput.

**Typical Reticulum LoRa settings:**
- Bandwidth: 125 kHz
- Spreading Factor: 8 (SF8)
- Coding Rate: 4/5
- TX Power: 17 dBm (50 mW)
- Effective bitrate: ~3.1 kbps (adequate for text messaging and CoT data)

### 3.5 Meshtastic vs Reticulum over LoRa

These are **separate systems** that can coexist on different hardware:

| Aspect | Reticulum + RNode | Meshtastic |
|--------|-------------------|------------|
| **Purpose** | General encrypted mesh networking | Consumer-friendly LoRa mesh messaging |
| **Encryption** | X25519 + AES-256 (per-identity) | AES-256 (channel-based PSK) |
| **Protocol** | LXMF over Reticulum | Meshtastic protobuf |
| **ATAK Support** | Not direct (separate systems) | Native ATAK plugin |
| **Complexity** | Higher (more capable) | Lower (easier setup) |
| **Recommended Use** | Primary encrypted comms backbone | ATAK integration + backup mesh |

**Strategy:** Run both. Use Meshtastic for ATAK PLI/chat relay over LoRa. Use Reticulum for primary encrypted messaging, file transfer, and bulletin board.

### 3.6 APRS Integration

APRS (Automatic Packet Reporting System) can be integrated via:
- Reticulum `KISSInterface` connected to a TNC (Terminal Node Controller)
- Direwolf software TNC on the Pi 5 with an attached radio
- LoRa APRS iGate firmware on ESP32 boards (separate from Reticulum)

This is a secondary capability -- prioritize Reticulum and Meshtastic first.

---

## 4. Tailscale Mesh VPN

### 4.1 Overview

Tailscale creates a WireGuard-based mesh VPN (tailnet) that connects all your devices with end-to-end encrypted tunnels. It handles NAT traversal automatically, making it ideal for connecting a portable community node back to the Mission 1 home network.

### 4.2 Installation on Pi 5 (ARM64)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up

# Enable as subnet router + exit node
sudo tailscale up \
  --advertise-routes=10.50.0.0/24 \
  --advertise-exit-node \
  --accept-routes
```

Enable IP forwarding (required for subnet routing and exit node):
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

### 4.3 Key Features for Community Node

#### Subnet Routing
Advertise the community node's local subnet (e.g., `10.50.0.0/24`) to the tailnet. This lets devices on the home network (Mission 1) access services on the community node's LAN without installing Tailscale on every device.

```bash
sudo tailscale up --advertise-routes=10.50.0.0/24
```
Then approve the route in the Tailscale admin console (or Headscale CLI).

#### Exit Node
Configure the community node as a VPN exit node. Devices using it as exit node will route all internet traffic through the community node's connection.

```bash
sudo tailscale up --advertise-exit-node
```

#### Tailscale Funnel
Expose specific services to the public internet without port forwarding:
```bash
# Expose OTS Web UI publicly
tailscale funnel 8080

# Expose a specific service with HTTPS
tailscale funnel --bg https+insecure://localhost:8080
```

#### MagicDNS
Automatic DNS resolution for all devices on the tailnet:
- `community-node.tailnet-name.ts.net` resolves to the Pi's Tailscale IP
- Services accessible by hostname across the mesh

### 4.4 Integration with Mission 1 Home Network

Both the Mission 1 home server and Mission 2 community node join the **same tailnet**. This creates a seamless encrypted overlay:

```
Mission 1 (Home)                    Mission 2 (Portable)
+-----------------+    Tailscale    +------------------+
| Proxmox Host    |<-- WireGuard -->| Raspberry Pi 5   |
| 10.10.0.0/24    |    Tunnel       | 10.50.0.0/24     |
+-----------------+                 +------------------+
      |                                    |
  Home LAN                          Community LAN
  (subnet routed)                   (subnet routed)
```

### 4.5 Headscale -- Self-Hosted Control Server

Headscale is an open-source, self-hosted implementation of the Tailscale control server. It eliminates dependency on Tailscale's cloud coordination service.

- **Repository:** `github.com/juanfont/headscale`
- **Current Version:** 0.23.x
- **License:** BSD-3-Clause

**Why Headscale?**
- Full sovereignty -- no third-party coordination server
- No account limits (Tailscale free tier: 100 devices)
- Self-hosted on Mission 1 Proxmox or the community node itself
- Compatible with official Tailscale clients

**Deployment:** See Docker Compose section below.

**Headscale CLI basics:**
```bash
# Create a user
headscale users create community

# Generate auth key for nodes
headscale preauthkeys create --user community --reusable --expiration 24h

# List nodes
headscale nodes list

# Approve routes
headscale routes list
headscale routes enable --route <route-id>
```

---

## 5. Meshtastic Integration

### 5.1 Overview

Meshtastic is an open-source, off-grid mesh communication platform running on affordable LoRa hardware. It is simpler than Reticulum and has a polished mobile app experience and direct ATAK integration.

- **Website:** meshtastic.org
- **Firmware:** Runs on ESP32 + LoRa boards (LilyGO, Heltec, RAK, etc.)
- **Clients:** Android app, iOS app, web client, Python CLI

### 5.2 Hardware

Recommended Meshtastic devices (separate from Reticulum RNode):
- **Heltec V3** (~$18) -- compact, OLED display, SX1262
- **LilyGO T-Beam** (~$30) -- GPS + 18650 battery holder + SX1276
- **RAK WisBlock Starter Kit** (~$25) -- modular, low power

Each community member can carry a Meshtastic device for LoRa mesh participation.

### 5.3 ATAK Plugin Integration

The Meshtastic ATAK Plugin (v1.1.16+) bridges ATAK with the Meshtastic LoRa mesh:

**Features:**
- Sends/receives CoT (Cursor on Target) data over LoRa
- Position Location Information (PLI) sharing without internet
- Geo-chat over mesh
- Server relay: forwards PLI/chat between Meshtastic mesh and TAK server
- External GPS: use Meshtastic device GPS as ATAK GPS source
- AES-256-GCM encryption

**Setup Flow:**
1. Install Meshtastic Android app + pair Meshtastic device via Bluetooth
2. Install ATAK-CIV from Google Play
3. Install Meshtastic ATAK Plugin (sideload APK from GitHub releases)
4. Plugin auto-detects Meshtastic service
5. CoT data now flows: ATAK <-> Meshtastic App <-> LoRa Mesh

### 5.4 MQTT Bridge

Meshtastic can bridge its LoRa mesh to an MQTT broker, enabling:
- Internet-connected services to receive mesh messages
- Integration with Home Assistant, Node-RED, custom dashboards
- Cross-mesh connectivity (connect distant Meshtastic meshes via MQTT)

```
Meshtastic Node <--LoRa--> Meshtastic Node (with WiFi)
                                |
                           MQTT Broker (Mosquitto on Pi)
                                |
                     Node-RED / Home Assistant / OTS
```

### 5.5 Community Deployment Topology

```
                    [Community Node Pi 5]
                    OpenTAK Server + MQTT
                    Reticulum Transport
                    Tailscale VPN
                           |
              +------------+------------+
              |            |            |
        [Member A]    [Member B]    [Member C]
        ATAK + Mesh   ATAK + Mesh   Sideband + Mesh
        Phone + T-Beam Phone + Heltec  Phone + RNode
```

---

## 6. Docker Compose Stack

### 6.1 Complete Tactical Services Stack

```yaml
# M2 Community Node -- Tactical Communications Stack
# File: /opt/community-node/docker-compose.yml

services:
  # ============================================================
  # OpenTAK Server — Situational Awareness / TAK Server
  # ============================================================
  # OTS runs NATIVELY under systemd — NOT in Docker.
  # Install: see BUILD_GUIDE.md Phase 5B
  # Status: systemctl status opentakserver
  # Ports: 8080 (HTTP UI), 8088 (CoT TCP), 8089 (CoT SSL),
  #        8443 (HTTPS UI), 8446 (cert enrollment)
  # Web UI: http://192.168.8.20:8080

  # ============================================================
  # Reticulum Daemon (rnsd) -- Encrypted Mesh Transport Node
  # ============================================================
  reticulum:
    image: python:3.12-slim
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
      # Pass through USB LoRa device (RNode) if connected
      - /dev/ttyUSB0:/dev/ttyUSB0
    # Ports (host networking):
    #   4242  - Reticulum TCP transport
    #   37428 - Reticulum shared instance

  # ============================================================
  # NomadNet -- Terminal BBS / Messaging over Reticulum
  # ============================================================
  nomadnet:
    image: python:3.12-slim
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

  # ============================================================
  # MeshChat -- Web-based Reticulum Messenger
  # ============================================================
  # meshchat:
  #   image: ghcr.io/liamcottle/reticulum-meshchat:latest
  #   container_name: meshchat
  #   restart: unless-stopped
  #   ports:
  #     - "8338:8338"
  #   volumes:
  #     - reticulum-config:/root/.reticulum
  #     - meshchat-data:/root/.meshchat
  #   depends_on:
  #     - reticulum

  # ============================================================
  # Mosquitto MQTT Broker -- Meshtastic Bridge
  # ============================================================
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - mosquitto-config:/mosquitto/config
      - mosquitto-data:/mosquitto/data
      - mosquitto-log:/mosquitto/log

  # ============================================================
  # Headscale -- Self-Hosted Tailscale Control Server (Optional)
  # ============================================================
  headscale:
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
      - TZ=America/New_York
    profiles:
      - headscale

volumes:
  reticulum-config:
    driver: local
  nomadnet-data:
    driver: local
  mosquitto-config:
    driver: local
  mosquitto-data:
    driver: local
  mosquitto-log:
    driver: local
  headscale-config:
    driver: local
  headscale-data:
    driver: local
```

### 6.2 Deployment Commands

```bash
# Create directory structure
sudo mkdir -p /opt/community-node
cd /opt/community-node

# Copy docker-compose.yml and Reticulum config

# Start core services (without Headscale)
docker compose up -d

# Start with Headscale (self-hosted Tailscale control)
docker compose --profile headscale up -d

# View logs
# OTS: journalctl -u opentakserver -f
docker compose logs -f reticulum-node

# Verify services
docker compose ps
```

### 6.3 Mosquitto Configuration

Create `/opt/community-node/mosquitto/config/mosquitto.conf`:

```
listener 1883
allow_anonymous true
listener 9001
protocol websockets
```

### 6.4 Reticulum Configuration

Copy the configuration from Section 2.5 to the reticulum-config volume. On first run:

```bash
# Generate default config
docker exec reticulum-node rnsd --exampleconfig > /tmp/reticulum-config.example

# Copy custom config into volume
docker cp ~/.reticulum/config reticulum-node:/root/.reticulum/config

# Restart to apply
docker compose restart reticulum
```

---

## 7. Hardware Add-ons BOM

### 7.1 LoRa / Radio Hardware

| Item | Description | Est. Price | Source |
|------|-------------|-----------|--------|
| **LilyGO T3 v1.6.1 (LoRa32 v2.1)** | RNode transceiver -- SX1276, 915 MHz, ESP32, OLED, USB-C | $18-25 | AliExpress, Amazon |
| **LilyGO T-Beam v1.1** | RNode w/ GPS + 18650 battery, SX1276/SX1262 | $25-35 | AliExpress, Amazon |
| **Waveshare SX1262 LoRa HAT** | Pi 5 HAT, 915 MHz, UART interface | $20-25 | Waveshare, Amazon |
| **Heltec V3 LoRa** | Meshtastic node, SX1262, OLED, USB-C | $16-20 | AliExpress, Heltec |
| **915 MHz LoRa Antenna (SMA)** | 5 dBi omni antenna, magnetic base | $8-12 | Amazon |
| **915 MHz Yagi Antenna** | Directional, 8-12 dBi, for long range links | $25-40 | Amazon, eBay |
| **SMA pigtail / adapter** | U.FL to SMA, or SMA extension cable | $5-8 | Amazon |

### 7.2 Recommended Minimum Kit

For the community node itself:

| Item | Purpose | Price |
|------|---------|-------|
| LilyGO T3 v1.6.1 x1 | RNode for Reticulum LoRa interface | $20 |
| Heltec V3 x1 | Meshtastic node (MQTT bridge to Pi) | $18 |
| 915 MHz antenna x2 | One per radio | $20 |
| USB-A to USB-C cables x2 | Connect radios to Pi | $8 |
| **Subtotal** | | **~$66** |

### 7.3 Per-Member Kit

Each community member should carry:

| Item | Purpose | Price |
|------|---------|-------|
| Heltec V3 or T-Beam | Meshtastic personal node | $18-30 |
| 915 MHz antenna | Attached to device | $10 |
| Android phone | ATAK + Meshtastic + Sideband apps | (existing) |
| **Subtotal** | | **~$28-40** |

### 7.4 Optional / Bonus Hardware

| Item | Description | Est. Price |
|------|-------------|-----------|
| **RTL-SDR v4** | Software-defined radio dongle for ADS-B, NOAA weather, scanning | $30 |
| **1090 MHz ADS-B antenna** | For aircraft tracking with dump1090 | $15 |
| **RAK2245 Pi HAT** | Full LoRaWAN gateway concentrator (if LoRaWAN needed) | $80 |
| **Baofeng UV-5R** | Handheld VHF/UHF radio for APRS or voice backup | $25 |
| **Mobilinkd TNC4** | Bluetooth packet radio TNC for APRS integration | $70 |
| **Weatherproof enclosure** | IP67 case for outdoor/field deployment | $20-40 |

### 7.5 Total Estimated Cost (Node Radio Add-ons)

| Category | Est. Cost |
|----------|-----------|
| Minimum radio kit (node only) | ~$66 |
| Per-member kit (x5 members) | ~$150-200 |
| Optional RTL-SDR + ADS-B | ~$45 |
| Optional APRS kit | ~$95 |
| **Total (node + 5 members + extras)** | **~$360-410** |

---

## 8. Integration Architecture

### 8.1 Full System Diagram

```
                        ============================================
                        |       COMMUNITY NODE (Raspberry Pi 5)     |
                        |                                           |
  Internet/Cellular <-->| Tailscale VPN ----- Mission 1 Home Net    |
       (when avail)     |                                           |
                        |  +------------------+  +--------------+   |
                        |  | OpenTAK Server   |  | MQTT Broker  |   |
                        |  | (CoT/SA/Chat/    |  | (Mosquitto)  |   |
                        |  |  Web Map UI)     |  |              |   |
                        |  +--------+---------+  +------+-------+   |
                        |           |                    |          |
                        |  +--------+---------+  +------+-------+   |
                        |  | Reticulum (rnsd) |  | Meshtastic   |   |
                        |  | NomadNet/LXMF    |  | MQTT Bridge  |   |
                        |  +--------+---------+  +------+-------+   |
                        |           |                    |          |
                        ============|====================|==========
                                    |                    |
                              [RNode USB]          [Heltec V3 USB]
                              915 MHz LoRa         915 MHz LoRa
                                    |                    |
                        +-----------+-----------+--------+----------+
                        |                       |                   |
                  [Member A]              [Member B]          [Member C]
                  Phone: ATAK+Sideband    Phone: ATAK         Phone: Sideband
                  Radio: T-Beam           Radio: Heltec V3    Radio: T3 (RNode)
                  (Mesh + Reticulum)      (Meshtastic)        (Reticulum)
```

### 8.2 Communication PACE Plan (Tactical Layer)

| Priority | Method | Medium | Range | Dependency |
|----------|--------|--------|-------|------------|
| **Primary** | ATAK + OpenTAK Server | WiFi / Cellular / Tailscale | Global (internet) | Internet connectivity |
| **Alternate** | Meshtastic LoRa mesh | 915 MHz LoRa radio | 1-15 km | LoRa hardware, no internet needed |
| **Contingency** | Reticulum + LXMF (Sideband/NomadNet) | LoRa via RNode | 1-15 km | RNode hardware, no internet needed |
| **Emergency** | Reticulum over serial / packet radio | VHF/UHF radio + TNC | 5-50 km | Amateur radio license, TNC hardware |

### 8.3 Startup Sequence

1. Boot Pi 5 and Docker services auto-start
2. Tailscale connects to tailnet (if internet available)
3. OpenTAK Server starts accepting CoT connections on port 8088/8089, web UI on 8080
4. Reticulum daemon starts, opens TCP transport (port 4242) and RNode LoRa interface
5. NomadNet daemon starts, announces pages on Reticulum network
6. Mosquitto MQTT broker starts for Meshtastic bridge
7. Connect Meshtastic node via USB -- configure MQTT uplink to localhost:1883
8. Clients connect: ATAK to OTS, Sideband to Reticulum, Meshtastic app to mesh

### 8.4 Key Recommendations

1. **Start with Meshtastic for ATAK integration** -- it has the most mature plugin and is easiest for non-technical community members.
2. **Deploy Reticulum as the encrypted backbone** -- its identity-based encryption and delay tolerance make it superior for sensitive communications.
3. **Use separate LoRa hardware** for Meshtastic and Reticulum -- they use different protocols and cannot share a single radio.
4. **Tailscale (or Headscale) is essential** for connecting back to Mission 1 -- it handles NAT traversal automatically.
5. **RNode DIY build** is strongly recommended over buying LoRa HATs -- better Reticulum support, antenna flexibility, and lower cost.
6. **Test range before deployment** -- actual LoRa range varies dramatically with terrain. Do a walk/drive test with your specific antenna setup.
7. **Mosquitto MQTT broker** bridges Meshtastic to other services -- use it to feed Meshtastic data into Node-RED, Home Assistant, or custom dashboards.
8. **NomadNet pages** serve as an off-grid information board -- post community updates, maps, procedures accessible to anyone on the Reticulum mesh.

---

## References

- OpenTAK Server Documentation: https://opentakserver.io/
- OpenTAK Server GitHub: https://github.com/brian7704/OpenTAKServer
- Reticulum Network Stack: https://github.com/markqvist/Reticulum
- Reticulum Manual (v1.1.3): https://reticulum.network/manual/
- Reticulum Interface Configuration: https://reticulum.network/manual/interfaces.html
- Sideband App: https://github.com/markqvist/Sideband
- NomadNet: https://github.com/markqvist/NomadNet
- MeshChat: https://github.com/liamcottle/reticulum-meshchat
- RNode Firmware Install: https://unsigned.io/installing-rnode-firmware-on-supported-devices/
- Meshtastic ATAK Plugin: https://meshtastic.org/docs/software/integrations/integrations-atak-plugin/
- Meshtastic ATAK Plugin GitHub: https://github.com/meshtastic/ATAK-Plugin
- Tailscale Raspberry Pi Setup: https://tailscale.com/kb/1103/exit-nodes
- Headscale: https://github.com/juanfont/headscale
- Headscale Container Docs: https://headscale.net/stable/setup/install/container/
- Heltec WiFi LoRa 32 V3: https://heltec.org/project/wifi-lora-32-v3/
- Waveshare SX1262 LoRa HAT: https://www.waveshare.com/sx1262-868m-lora-hat.htm
- RAK Wireless Pi HATs: https://store.rakwireless.com/collections/lora-for-raspberry-pi-hats-modules-add-ons
