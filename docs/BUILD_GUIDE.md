# Mission 2 — Community Node: Master Build Guide

> **Build Tier:** Recommended (~$1,385–$1,425) — Dual Raspberry Pi 5 16GB
> **Prerequisite:** Procurement complete. All hardware in hand.

> **⚠️ PLATFORM NOTICE:** This entire guide was developed, tested, and deployed from a **Windows 11 machine using PowerShell** as the SSH client to both Raspberry Pi nodes. All command formatting, quoting, escape sequences, and troubleshooting steps assume this specific setup. If you are building from a Linux or macOS workstation, you are responsible for adapting commands to your shell environment — particularly quoting rules, heredoc syntax, curl behavior, and SSH client differences. PowerShell aliases `curl` to `Invoke-WebRequest` (use `curl.exe` for real curl), mangles JSON escaping, and inserts hard newlines when pasting long lines into nano via SSH. None of these issues exist on Linux/macOS terminals, but other differences will. **If you are building from a different platform, consider using a Claude session to reformat the commands for your environment.** We make no guarantees about correctness on platforms other than Windows 11 + PowerShell.

---

## Table of Contents

1. [Overview & Timeline](#1-overview--timeline)
2. [Phase 0: Pre-Build (Before Hardware Arrives)](#2-phase-0-pre-build-before-hardware-arrives)
3. [Phase 1: Rack Assembly](#3-phase-1-rack-assembly)
4. [Phase 2: Network Baseline](#4-phase-2-network-baseline)
5. [Phase 3: OS & Base Config — Both Nodes](#5-phase-3-os--base-config--both-nodes)
6. [Phase 4: Node #1 — Communications Stack](#6-phase-4-node-1--communications-stack)
7. [Phase 5: Node #2 — Tactical/Crypto Stack](#7-phase-5-node-2--tacticalcrypto-stack)
8. [Phase 6: LoRa Radio Setup](#8-phase-6-lora-radio-setup)
9. [Phase 7: Integration Testing](#9-phase-7-integration-testing)
10. [Phase 8: Field Hardening](#10-phase-8-field-hardening)
11. [Phase 9: Post-Launch Improvements](#11-phase-9-post-launch-improvements)
12. [Quick Reference](#12-quick-reference)
13. [Field Operations: Power Cycle Procedure](#13-field-operations-power-cycle-procedure)
14. [Tech Verification Checklist](#14-tech-verification-checklist)

---

## 1. Overview & Timeline

### Node Assignments

| Node | Hostname | IP | Role | Services |
|---|---|---|---|---|
| Pi 5 #1 | `comms` | 192.168.8.10 | Communications | Conduit (Matrix), Element Web, Nginx, I2P, Tor, Cloudflared |
| Pi 5 #2 | `tactical` | 192.168.8.20 | Tactical/Crypto | Monero, OpenTAK Server (native), Reticulum, NomadNet, Mosquitto, Headscale, Mumble |

### Estimated Build Timeline

| Phase | Task | Time |
|---|---|---|
| Phase 0 | Monero pre-sync (x86, runs in background) | 4–7 days |
| Phase 0 | Image downloads + SD prep | 30 min |
| Phase 1 | Rack assembly | 1–2 hours |
| Phase 2 | Network baseline | 30 min |
| Phase 3 | OS on both nodes | 45 min |
| Phase 4 | Node #1 comms stack | 1–2 hours |
| Phase 5 | Node #2 tactical stack | 1–2 hours |
| Phase 6 | LoRa radio setup | 30 min |
| Phase 7 | Integration testing | 1 hour |
| Phase 8 | Field hardening | 30 min |
| **Total (excluding pre-sync)** | | **~7–10 hours** |

> **Critical path:** Start Monero pre-sync on your x86 machine the day procurement is ordered — it takes 4–7 days to sync the full blockchain and will be ready to rsync to the Pi by build day.

### Budget Swaps (if you downgraded any items)
- UPS: Tripp Lite BC600R (600VA/300W) — sits inside rack at U1; runtime at idle ~138 min (26W), typical ~103 min (35W), full load ~74 min (48.5W)
- Switch: If unmanaged (TL-SG108S) — skip VLAN config in Phase 2; assign static IPs only
- Single Pi 5 budget build — skip Node #2 phases entirely for now; they're designed to be added later
- Power: Use the Anker 747 GaNPrime 150W GaN charger (B09W2PNLX7, ~$65) instead of individual USB-C PD 27W adapters — one charger powers both Pi 5s, GL.iNet, and touchscreen from a single PDU outlet
- Transport (Premium add-on): **Pelican 1610** (~$180–$220) — interior 21.78"×16.69"×10.62". The T1 rack lays flat inside (16"L×11"W×7.8"H) with ~2.8" depth clearance for foam; BC600R is inside the rack at U1, self-contained unit. ⚠️ The Apache 4800 does NOT fit — its 7.25" interior depth is 0.55" shallower than the rack's 7.8" body depth.

---

## 2. Phase 0: Pre-Build (Before Hardware Arrives)

### 0.1 Monero Pre-Sync on x86 Machine

**Start this immediately — it takes 4–7 days.**

The Raspberry Pi 5 would take 2–4 weeks to sync the Monero blockchain natively on ARM. By syncing on a faster x86 machine first and rsyncing the LMDB database, you eliminate that wait entirely.

> **Full Windows pre-sync documentation** (including all troubleshooting, validation scripts, and recovery procedures) lives in `G:\MoneroNode\Monero_Node_Complete_Guide.md`. What follows is a summary for planning purposes.

#### ISP and Network Caveats (Confirmed in Real-World Testing)

**AT&T Fiber and other DPI-filtering ISPs:** AT&T uses Deep Packet Inspection to fingerprint and drop Monero's Levin P2P binary protocol. Symptoms: every outbound handshake times out (`LEVIN_ERROR_CONNECTION_TIMEDOUT`), node stuck at 1 peer, `target_height: 0`. **A VPN is required on AT&T.**

**VPN configuration that works (confirmed on AT&T Fiber + ProtonVPN):**
- Connect to a **regular ProtonVPN server** — NOT a P2P-labeled server (P2P servers cause the same timeouts)
- Launch monerod with **minimal flags only** — extra flags like `--db-sync-mode`, `--out-peers`, and `--add-peer` interfere with peer discovery through VPN

**What does NOT work for the pre-sync phase:**
- `--add-peer hostname:port` — crashes monerod on Windows via VPN (DNS resolution fails during p2p init)
- `--add-peer ip:port` — those nodes reject connections from VPN exit IPs
- Tor (`--proxy 127.0.0.1:9150`) — Tor exit nodes block port 18080; full blockchain sync cannot run over Tor hidden services

#### p2pstate.bin Corruption (All Environments)

Every time monerod stops, it writes a `p2pstate.bin` file. If corrupt on next start, monerod fails with `Exception in main! Failed to initialize p2p server`. **Always use the `__fix_and_launch.ps1` script** — it deletes this file before every launch automatically. Never run `monerod.exe` directly.

#### Windows Pre-Sync (Confirmed Working)

Install location: `G:\MoneroNode\` (or any drive with 120+ GB free)

```powershell
# All setup, validation, and launch is handled by scripts in G:\MoneroNode\
# See Monero_Node_Complete_Guide.md for full setup procedure.

# Standard launch (after setup):
Set-Location "G:\MoneroNode"
.\__fix_and_launch.ps1
```

**Confirmed working flags** (minimal — do not add more):
```powershell
.\monerod.exe `
    --prune-blockchain `
    --data-dir "G:\MoneroNode\data" `
    --log-level 1
```

**Monitor sync:**
```powershell
Set-Location "G:\MoneroNode"
.\check-sync.ps1
# Shows: Height / Target, Progress %, DB Size, Peer count, Status
```

**Linux pre-sync (no ISP DPI issues observed):**
```bash
./monerod --prune-blockchain --data-dir ~/monero-data --detach --log-level 0
tail -f ~/monero-data/bitmonero.log
```

**LMDB location after sync:**
```
Windows: G:\MoneroNode\data\lmdb\
Linux:   ~/monero-data/lmdb/
Size:    ~95-110 GB pruned
```

> **Do not proceed to Phase 5 until sync shows 100.0%.** Verify against [xmrchain.net](https://xmrchain.net). Keep monerod running until build day — you'll rsync the LMDB to the Pi in Phase 5.

---

### 0.2 Download Software & Images

Do this while waiting for hardware to arrive.

**Raspberry Pi OS (64-bit, Bookworm):**
```
https://www.raspberrypi.com/software/operating-systems/
Download: Raspberry Pi OS Lite (64-bit) — no desktop needed
```

**Raspberry Pi Imager:**
```
https://www.raspberrypi.com/software/
```

**Docker images to pre-pull (optional — saves time on slow connections):**

These are the pinned versions used in the compose files. Do not pull `:latest` — you'll get a different image than what the configs are tested against.

```bash
# Node #1 — Communications Stack
docker pull matrixconduit/matrix-conduit:v0.10.12
docker pull vectorim/element-web:v1.12.11
docker pull nginx:1.28.2-alpine3.23
docker pull purplei2p/i2pd:release-2.59.0
docker pull osminogin/tor-simple:0.4.8.21
docker pull cloudflare/cloudflared:2026.2.0

# Node #2 — Tactical/Crypto Stack
docker pull ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5
docker pull python:3.12.12-slim-bookworm
docker pull eclipse-mosquitto:2.0.22
docker pull headscale/headscale:0.28.0
# OpenTAK Server: native install (systemd) — no Docker image needed
```

> **Image version reference (verify current tags before deploying):**
> | Image | Pinned Tag | Notes |
> |---|---|---|
> | `matrixconduit/matrix-conduit` | `v0.10.12` | **Tech debt:** matrixconduit/matrix-conduit is abandoned as of 2025. Active community fork is conduwuit. Plan migration post-CCC26. Do NOT change the image now — document for future sprint. |
> | `vectorim/element-web` | `v1.12.11` | Latest stable |
> | `nginx` | `1.28.2-alpine3.23` | Stable branch, Alpine 3.23 |
> | `purplei2p/i2pd` | `release-2.59.0` | Latest stable, Feb 2026 |
> | `osminogin/tor-simple` | `0.4.8.21` | Mirrors Tor version |
> | `cloudflare/cloudflared` | `2026.2.0` | CalVer, update monthly |
> | `simple-monerod` | `v0.18.4.5` | Monero Fluorine Fermi |
> | `OpenTAKServer` | `v1.7.9` | Native install (systemd) — not Docker. Pi installer is production-ready. |
> | `python` | `3.12.12-slim-bookworm` | Oct 2025 patch release (Reticulum/NomadNet) |
> | `eclipse-mosquitto` | `2.0.22` | Stable 2.0.x series |
> | `headscale/headscale` | `0.28.0` | ⚠️ Breaking changes from 0.23 — read release notes |

**rnodeconf (for LoRa firmware flashing — bundled in rns package):**
```bash
pip install rns
# rnodeconf is now part of rns — do NOT install the standalone rnodeconf package (outdated)
```

---

### 0.3 Prepare microSD Cards

Flash both microSD cards before build day so first boot is instant.

1. Insert microSD card into your computer
2. Open Raspberry Pi Imager
3. **Choose Device:** Raspberry Pi 5
4. **Choose OS:** Raspberry Pi OS Lite (64-bit)
5. **Choose Storage:** your microSD card
6. **Click the gear icon (Advanced settings):**
   - Enable SSH ✓
   - Set hostname: `comms` (card 1) / `tactical` (card 2)
   - Set username: `pi` (or your preferred username)
   - Set password: use a strong password
   - Configure WiFi: optional (you'll use Ethernet)
   - Set locale/timezone
7. Write the card
8. Label each card clearly

---

### 0.4 Optional: 3D Print Rack Accessories

If GeeekPi RackMate T1 panels or trays are backordered:

- **Blank 1U/2U panels:** search Printables/Thingiverse for "10 inch rack panel 1U"
- **Pi 5 tray for 10" rack:** search "Raspberry Pi 5 rack mount 10 inch"
- **Jeff Geerling's community files:** `github.com/geerlingguy/mini-rack`
- **DeskPi STL files:** `deskpi.com` → Downloads
- Print in PETG (better heat tolerance than PLA for enclosed rack)

---

### 0.5 Hardware Validation (DOA Check — Before Rack Assembly)

**Do this before assembling anything in the rack.** A 15-minute bench test on each component saves hours of debugging inside an assembled rack.

**Raspberry Pi #1 and #2 — bare board boot test:**
```bash
# Insert pre-flashed microSD, connect USB-C power
# Find DHCP IP from your router client list, then:
ssh pi@<dhcp-ip>
uname -a                  # verify: aarch64, kernel 6.x
vcgencmd get_throttled    # must return 0x0 (no undervoltage, no throttling)
free -h                   # should show ~15.6 GB total RAM
```
> If `get_throttled` returns anything other than `0x0`, your power supply is insufficient. Stop — do not proceed.

**NVMe SSDs — verify recognition (after Phase 3.4):**
```bash
lsblk                                  # nvme0n1 must appear
sudo nvme smart-log /dev/nvme0n1       # check "Critical Warning: 0x0"
```

**GL.iNet Slate AX:**
- Power via USB-C → browse to `http://192.168.8.1` → login page appears ✓

**TP-Link TL-SG108S switch:**
- Connect any device to any port → green link LED ✓

**Tripp Lite BC600R UPS:**
- Plug in, press power button → green status LED ✓
- Self-test passes (brief beep sequence) ✓

**LoRa radios — USB serial recognition:**
```bash
# Connect each radio individually to your laptop
dmesg | tail -20    # should show: CP210x or CH343 USB converter
ls /dev/ttyUSB*     # /dev/ttyUSB0 should appear
```

**Touchscreen (if purchased):**
- Connect via HDMI + USB to any Pi → display lights on ✓

> **Stop here if anything fails.** Initiate DOA return/replacement before you build. Parts within the rack are harder to swap after assembly.

---

## 3. Phase 1: Rack Assembly

### 1.1 Inventory Check

Before starting, verify you have every item. Cross-reference HARDWARE_BOM.md recommended tier BOM.

Critical items:
- [ ] GeeekPi RackMate T1 8U chassis (B0CPLRD29P)
- [ ] Raspberry Pi 5 16GB × 2 (PiShop.us, $205 ea.)
- [ ] Pi 5 Active Cooler × 2 (PiShop.us, $10.95 ea.)
- [ ] GeeekPi 1U Dual Pi 5 Mount (B0F7XBVV4D) — **⚠️ verify on Amazon before ordering: confirm (1) 1U height, (2) 2× Pi 5 slots, (3) 2× built-in NVMe adapters, (4) clearance for Pi 5 Active Cooler. This is the critical path item for the entire layout.**
- [ ] WD SN740 256GB M.2 2230 NVMe OEM (B0C6MVP42M) — Pi #1 (~$35-45; Official Pi SSD 256GB OUT OF STOCK Feb 2026)
- [ ] Crucial P310 1TB M.2 2230 NVMe (CT1000P310SSD2) — Pi #2 (~$115-150; Official Pi SSD 1TB OUT OF STOCK Feb 2026)
  > **⚠️ NVMe Gen 3 required on both nodes:** Add `dtparam=pciex1_gen=3` to `/boot/firmware/config.txt` (Phase 3.4). GeeekPi dual mount defaults to Gen 2 without it. See BOM §1.1 for detail.
- [ ] TP-Link TL-SG108S 8-port switch (~$27) — skip Phase 2.2 VLAN config if using unmanaged
- [ ] Tripp Lite BC600R UPS (600VA/300W, ~$70)
- [ ] GL.iNet Slate AX router (AXT1800, $119.99)
- [ ] 1U Rack PDU 4-Outlet (B0FP56YSWZ) — 125V/15A, surge protection, 6ft cable
- [ ] GeeekPi 2U touchscreen (B0F3C5R2BZ)
- [ ] Anker 747 GaNPrime 150W GaN charger (B09W2PNLX7) — powers both Pi 5s + GL.iNet + display from one PDU outlet
- [ ] Heltec WiFi LoRa 32 V3 915MHz × 2 ($19.90 each, heltec.org) — LEFT=RNode, RIGHT=Meshtastic

- [ ] 915 MHz antennas × 2 — **⚠️ must be SMA MALE (NOT RP-SMA)** — verify connector type in listing photos before ordering
- [ ] USB-C to USB-C cables, 1ft, ×3 — **not included with Anker 747** (Pi #1, Pi #2, GL.iNet power)
- [ ] microSD cards × 2 (pre-flashed, from Phase 0)
- [ ] Short Ethernet patch cables (6" or 1ft, internal rack runs)
- [ ] WAN Ethernet cable (3ft or 6ft — for GL.iNet WAN to uplink; short patches are too short)
- [ ] Velcro cable ties + cable labels (both ends of every cable)
- [ ] Dust filter foam pad (120mm, open-frame intake areas)
- [ ] USB-A extension cable 12"–18" × 1 (contingency: 80mm fan cable length to Pi #2)
- [ ] Custom 1U LoRa Panel (3D print, black PETG) — 2× OLED windows, 2× SMA bulkhead holes, 2× M2 board mount positions
- [ ] SMA female bulkhead connectors × 2
- [ ] U.FL-to-SMA-male pigtail cables × 2 (6", IPEX MHF4 to SMA male)
- [ ] M2 × 8mm nylon standoffs + M2 screws (8 standoffs = 4 per board)
- [ ] LabStack 2U Mini 2x 80mm Fan Panel (3D print, github.com/JaredC01/LabStack)
- [ ] 80mm USB 5V fans × 2 (GDSTIME / ELUTENG or similar)

---

### 1.2 UPS — Initial Charge

**Do this first** — the UPS needs 8–12 hours to reach full charge from the box.

1. Unbox Tripp Lite BC600R
2. Plug into wall outlet
3. Power on UPS (press power button)
4. Let charge — you'll hear a beep when ready
5. Leave plugged in throughout the build
6. After build is complete, the BC600R sits inside the rack at U1 — secured with velcro to the rack frame. Dimensions are 10.04"×7.09"×2.28" (~1.3U height)

---

### 1.3 Rack Assembly Order

Work bottom-up — heaviest items go low.

```
FRONT VIEW                                    REAR VIEW
+==========================================+  +==========================+
|          GeeekPi 8U RackMate T1          |  |        (Rear View)       |
|          (Front View, Top-Down)          |  +==========================+
+==========================================+  |                          |
|                                          |  |  U8  [ 120mm Fan (rear)] |  <-- shares U8 with
|  U8  [ Custom 1U LoRa Panel (front) ]   |  |      [ exhaust UP      ] |     LoRa panel (front)
|      [ Heltec (L) | SMA | Heltec (R)]  |  |                          |
|                                          |  |  U7  [ screen rear     ] |
|  U7  [                               ]   |  |  U6  [ (cables)        ] |
|      [ 2U Touchscreen (7.84" LCD)    ]   |  |                          |
|  U6  [                               ]   |  |  U5  [ switch rear     ] |
|                                          |  |                          |
|  U5  [ TP-Link TL-SG108S + GL.iNet  ]   |  |  U4  [ LabStack 2U     ] |  <-- 2x 80mm fans
|      [ (side by side on 1U shelf)   ]   |  |      [ 80mm Fan Panel   ] |     pull air OUT
|                                          |  |  U3  [ (rear exhaust)  ] |     behind Pi nodes
|  U4  [ GeeekPi 1U Dual Pi 5 Mount   ]   |  |                          |
|      [ Pi #1 (left) + Pi #2 (right) ]   |  |  U2  [ PDU (rear rails)] |     outlets face inward;
|      [ 256GB NVMe    1TB NVMe       ]   |  |      [ adapters on UPS ] |     adapters rest on UPS
|                                          |  |  U1  [ UPS rear cable  ] |
|  U3  [ USB Fan Hub (velcro mount)   ]   |  |                          |
|                                          |  +==========================+
|  U2  [ ---- OPEN ----               ]   |     PDU on REAR rails
|                                          |
|  U1  [ Tripp Lite BC600R (UPS)       ]   |
|      [ 10.04"×7.09"×2.28" (~1.3U)  ]   |
|                                          |
+==========================================+
```

**Airflow path:** Cool air enters around the sides of the BC600R UPS at U1 (open-frame chassis) → flows upward through rack → Pi nodes at U4 generate heat → 2× 80mm rear fans (U4-U3 rear) pull hot air out the rear → 120mm fan at U8 rear exhausts remaining rising heat upward past the LoRa antennas. Dual exhaust at rear + top creates positive airflow through the Pi node zone.

**Note on U positions:** U8 is shared — LoRa panel on **front** rails (antennas at top for best RF, maximum distance from power at U1-U2), 120mm fan on **rear** rails (exhaust up). The LabStack 2U fan panel mounts on the **rear** rails spanning U4-U3, directly behind the Pi mount (U4 front). U3 front is open for future expansion; U3 rear is the fan panel's second U.

> The Tripp Lite BC600R sits inside the rack at U1, secured with velcro to the rack frame. PDU mounts on **rear rails** at U2 with wings flipped so outlets face inward — power adapters rest on the UPS body. Ultra-short power cable run. U2 front is open. All power infrastructure is self-contained in the rack.

**Assembly steps:**

1. Attach rack ears/rails per GeeekPi RackMate T1 instructions
2. Place Tripp Lite BC600R into U1 (bottom front) — secure with velcro to rack frame
3. Mount PDU into U2 (**rear rails**) — flip wings so outlets face inward; power adapters rest on top of UPS body at U1. 6ft cable drops down to UPS (ultra-short run). U2 front stays open.
4. Print and install LabStack 2U Mini 2x 80mm Fan Panel into U4-U3 (rear rails) — mount 2× 80mm USB fans using the fans' coarse-thread screws; orient fans to exhaust air OUT of the rack
5. Install GeeekPi 1U Dual Pi 5 Mount into U4 (front) — holds both Pi nodes with built-in NVMe adapters. Fan panel (U4-U3 rear) sits directly behind for maximum cooling.
6. Mount switch and GL.iNet router side-by-side on a 1U shelf into U5 (front)
7. Mount touchscreen into U6/U7 (front) — connect HDMI from Pi #1 and USB for touch input
8. Print and install custom 1U LoRa panel into U8 (front rails) — antennas at maximum height for best RF propagation:
   - Install 2× SMA female bulkhead connectors into SMA cutout holes, secure with nuts
   - Mount Heltec V3 (RNode) on **LEFT** M2 standoff positions (4× M2 nylon standoffs), OLED aligned behind left window cutout
   - Mount Heltec V3 (Meshtastic) on **RIGHT** M2 standoff positions (4× M2 nylon standoffs), OLED aligned behind right window cutout
   - Connect U.FL-to-SMA pigtail from LEFT Heltec V3 U.FL connector → left SMA bulkhead (interior side)
   - Connect U.FL-to-SMA pigtail from RIGHT Heltec V3 U.FL connector → right SMA bulkhead (interior side)
   - Screw 915 MHz antennas onto exterior SMA bulkheads — **verify SMA male (center pin), not RP-SMA**
9. Mount 120mm exhaust fan into U8 (rear rails) — shares U8 with LoRa panel on front rails via open-frame chassis

---

### 1.4 Attach Coolers and Storage to Pi Boards

**Before mounting Pi boards in the GeeekPi 1U Dual Pi 5 Mount, do this on a clear surface:**

**Pi #1 — attach cooler and NVMe:**
1. Attach Pi 5 Active Cooler to Pi #1 (press down firmly, connector goes to fan header)
2. Install the WD SN740 256GB M.2 2230 into the left NVMe adapter slot on the GeeekPi dual mount
3. Secure NVMe with the retention screw
4. No separate M.2 HAT+ is needed — the dual mount's built-in PCIe adapter provides NVMe connectivity

**Pi #2 — attach cooler and NVMe:**
1. Attach Pi 5 Active Cooler to Pi #2
2. Install the Crucial P310 1TB M.2 2230 into the right NVMe adapter slot on the GeeekPi dual mount
3. Secure NVMe with the retention screw

**Mount both Pi boards in the GeeekPi 1U Dual Pi 5 Mount and connect:**
- Anker 747 GaN charger → PDU outlet 1 (one outlet powers everything below)
- Anker C1 (short USB-C cable) → Pi #1
- Anker C2 (short USB-C cable) → Pi #2
- Anker C3 (short USB-C cable) → GL.iNet Slate AX
- Anker USB-A → touchscreen display
- Switch 12V adapter → PDU outlet 2
- Ethernet from switch port 1 → Pi #1
- Ethernet from switch port 2 → Pi #2
- Ethernet from switch uplink → GL.iNet LAN port
- Heltec V3 LEFT (RNode) → Pi #2 USB 2.0 port 1 via 3ft USB-C cable (board mounted on LoRa panel at U8, Pi at U4 — 4U distance; serial 115200 baud — USB 2.0 is sufficient)
- Heltec V3 RIGHT (Meshtastic) → Pi #2 USB 2.0 port 2 via 3ft USB-C cable (board mounted on LoRa panel at U8, Pi at U4 — 4U distance)
- U.FL pigtails and SMA antennas already connected during panel assembly (step 3 above)
- USB fan hub wall adapter → PDU outlet 3
- 120mm fan (U8 rear) → USB fan hub at U3
- 2× 80mm rear fans (U4-U3 rear) → USB fan hub at U3
- All 3 fans powered from hub — zero fan cables to Pi USB ports

---

### 1.5 Cable Management

- Run all Ethernet on the right side, power on the left
- Use velcro ties — never zip ties (harder to modify later)
- Keep patch cables short — measure runs before cutting/buying
- **Label both ends of every cable** (P-Touch tape or masking tape + sharpie — cable labels are in the BOM, item 24a)
- Leave 6" of slack at each device end for serviceability
- The WAN cable (item 21a) exits the rack through the rear — route it separately from internal patch cables

---

## 4. Phase 2: Network Baseline

### 2.1 GL.iNet Slate AX Router Setup

1. Connect your laptop to the GL.iNet via Ethernet or WiFi (`GL-AXT1800-XXX`)
2. Browse to `http://192.168.8.1` (default GL.iNet LAN IP)
3. Set admin password (strong — save in password manager)
4. **WAN configuration:**
   - If connecting to your home router: plug WAN port into home network switch
   - If standalone/field: configure 4G dongle or tether from phone
5. **WiFi — Two SSIDs:**

   | SSID | Band | Hidden | Password | Purpose |
   |---|---|---|---|---|
   | `NodeAdmin` | 5GHz main | No | Operator's personal password (not documented) | Operator/admin access only |
   | `CommunityNode` | 5GHz guest | No | `YOUR_EVENT_WIFI_PASSWORD` (set per event, document in `M2_SECRETS.md`) | Visitors, community members |

   - `NodeAdmin`: Wireless → 5GHz → set SSID and password, apply
   - `CommunityNode`: Guest Network → 5GHz Guest → enable, set SSID and password, leave 2.4GHz Guest disabled, apply
   - After applying, reconnect to `NodeAdmin` — Pis on ethernet are unaffected
   - Wait 60 seconds for AP isolation fix scripts to fire before testing connectivity
6. **DHCP range:** 192.168.8.100 – 192.168.8.200
7. **Static leases (MUST use ethernet MAC addresses):**
   - Pi #1 `comms`: 192.168.8.10 — ethernet MAC: `[YOUR MAC — see note below]`
   - Pi #2 `tactical`: 192.168.8.20 — ethernet MAC: `[YOUR MAC — see note below]`
   - Touchscreen: 192.168.8.30

> **Do NOT copy MACs from another build — they are burned into each device and unique to your hardware.** Using wrong MACs causes silent DHCP failure: the Pi gets a random IP and SSH to the static address will fail with no error.
>
> **You won't know the MACs until first boot.** Skip this step now. After Phase 3.1 first boot, open `http://192.168.8.1` → Clients. Each Pi will appear with its real ethernet MAC. Copy those values, create the static leases, then reboot the Pis before continuing to Phase 3.2.
>
> **CRITICAL: Use the ethernet MAC, not the WiFi MAC.** Each Pi 5 has two NICs. Look for the **wired** connection icon in the GL.iNet clients list, not the WiFi icon. If the Pis show up with unexpected IPs (e.g. .136, .141) after setting leases, delete the reservations and recreate using the MAC shown on the wired entry.

8. **Fix AP Isolation firmware bug (CRITICAL):**

> **Known bug:** The GL-AXT1800 firmware (confirmed on v4.x) silently forces `ap_isolate=1` in the hostapd config whenever repeater mode is active. This blocks WiFi clients (your laptop/phone) from reaching wired LAN clients (the Pis on the switch). The admin UI shows isolation as "off" but the running config ignores it. This must be fixed or you cannot manage the Pis from WiFi.

**[SSH — GL.iNet router]**

SSH into the router: `ssh root@192.168.8.1` (password is the admin panel password)

Create a hotplug script that automatically disables AP isolation on every network change. The script includes a 10-second delay and a retry because `wifi reload` restarts hostapd asynchronously — without the delay, the fix fires before hostapd is ready and doesn't stick:

**[SSH — root@GL.iNet router (192.168.8.1)]**

```
cd /etc/hotplug.d/iface
```

```
printf '#!/bin/sh\nsleep 10\nhostapd_cli -i wlan0 set ap_isolate 0 2>/dev/null\nhostapd_cli -i wlan1 set ap_isolate 0 2>/dev/null\nsleep 10\nhostapd_cli -i wlan0 set ap_isolate 0 2>/dev/null\nhostapd_cli -i wlan1 set ap_isolate 0 2>/dev/null\n' > 99-fix-isolation
```

```
chmod +x 99-fix-isolation
```

Expected contents of `/etc/hotplug.d/iface/99-fix-isolation`:
```
#!/bin/sh
sleep 10
hostapd_cli -i wlan0 set ap_isolate 0 2>/dev/null
hostapd_cli -i wlan1 set ap_isolate 0 2>/dev/null
sleep 10
hostapd_cli -i wlan0 set ap_isolate 0 2>/dev/null
hostapd_cli -i wlan1 set ap_isolate 0 2>/dev/null
```

Add boot-time backup to rc.local with a double-tap pattern (15s and 30s after boot):

**[SSH — root@GL.iNet router (192.168.8.1)]**

```
printf '# Put your custom commands here that should be executed once\n# the system init finished. By default this file does nothing.\n\n. /lib/functions/gl_util.sh\nremount_ubifs\n\n# Fix GL.iNet AP isolation firmware bug — double tap with delay\n(sleep 15 && hostapd_cli -i wlan0 set ap_isolate 0 && hostapd_cli -i wlan1 set ap_isolate 0) &\n(sleep 30 && hostapd_cli -i wlan0 set ap_isolate 0 && hostapd_cli -i wlan1 set ap_isolate 0) &\nexit 0\n' > /etc/rc.local
```

Expected contents of `/etc/rc.local`:
```
# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.

. /lib/functions/gl_util.sh
remount_ubifs

# Fix GL.iNet AP isolation firmware bug — double tap with delay
(sleep 15 && hostapd_cli -i wlan0 set ap_isolate 0 && hostapd_cli -i wlan1 set ap_isolate 0) &
(sleep 30 && hostapd_cli -i wlan0 set ap_isolate 0 && hostapd_cli -i wlan1 set ap_isolate 0) &
exit 0
```

Apply the fix immediately (no reboot needed):

```
hostapd_cli -i wlan0 set ap_isolate 0
```

```
hostapd_cli -i wlan1 set ap_isolate 0
```

Verify from your Windows machine: `ping 192.168.8.10` — should respond.

> **If WiFi-to-LAN stops working in the future:** SSH into the router (`ssh root@192.168.8.1`) and re-run `hostapd_cli -i wlan0 set ap_isolate 0` and `hostapd_cli -i wlan1 set ap_isolate 0`. The hotplug and rc.local scripts handle reboots and wifi reloads automatically, but a WiFi password change or firmware upgrade can still trigger the bug. If scripts are missing after a firmware upgrade, recreate them with the commands above.
>
> **Known triggers:** WiFi password changes, firmware upgrades, `wifi reload` commands, and GL.iNet admin panel changes to wireless settings all cause the firmware to rewrite hostapd config with `ap_isolate=1`. The double-tap retry pattern in the scripts handles the timing race condition where hostapd restarts asynchronously after these events.
>
> **Boot timing: After any router reboot or power cycle, allow 60 seconds before testing connectivity.** The AP isolation fix scripts run at 15s and 30s after boot. WiFi clients can associate before the fix applies, so initial pings may fail. This is normal — wait for the full 60-second startup window before troubleshooting. This applies to field deployment power-on sequences as well.

---

### 2.2 Switch Setup — TL-SG108S (Unmanaged)

The **TP-Link TL-SG108S** is an unmanaged gigabit switch — no configuration required. Plug in and go.

#### 2.2.1 Port Assignment

| Switch Port | Device | Cable Length |
|---|---|---|
| Port 1 | GL.iNet Slate AX — **LAN1** port (maps to `eth2` in OpenWrt) | 6" patch |
| Port 2 | Pi #1 `comms` (192.168.8.10) | 6" patch |
| Port 3 | Pi #2 `tactical` (192.168.8.20) | 6" patch |
| Port 4 | Touchscreen (192.168.8.30) — optional if networked | 6" patch |
| Ports 5–8 | Spare | — |

GL.iNet WAN port → your internet uplink (home router / cellular / Starlink).

#### 2.2.2 Power

Connect the switch's 12V DC barrel adapter to a PDU outlet. Link LEDs on the connected ports will light up within a few seconds of powering the GL.iNet.

> No IP address, no login, no PoE risk, no save-config step. The GL.iNet handles all routing and DHCP — the switch is just a patch panel.

---

### 2.3 GL.iNet DNS Overrides for Matrix (LAN Hairpin Fix)

LAN clients (on CommunityNode WiFi) reach Matrix at `https://m2-matrix.yourdomain.com` and the server delegation domain `m2.yourdomain.com`. Both must resolve to Pi #1's LAN IP (`192.168.8.10`) on the GL.iNet router. Without these overrides, HTTPS connections from LAN devices go via Cloudflare's edge instead of directly to the Pi, and TLS breaks because the cert is issued for the clearnet hostname. Add both dnsmasq overrides now, before deploying Matrix.

**[SSH — root@GL.iNet router (192.168.8.1)]**

```
uci add_list dhcp.@dnsmasq[0].address="/m2-matrix.yourdomain.com/192.168.8.10"
uci add_list dhcp.@dnsmasq[0].address="/m2.yourdomain.com/192.168.8.10"
```

```
uci commit dhcp && /etc/init.d/dnsmasq restart
```

Verify both overrides are active:

```
nslookup m2-matrix.yourdomain.com 192.168.8.1
nslookup m2.yourdomain.com 192.168.8.1
```

Expected: both return `192.168.8.10`. If either returns the public Cloudflare IP, the override did not apply — check `uci show dhcp | grep address` to confirm both entries are present.

> Both overrides survive router reboots. A firmware upgrade may wipe UCI customizations — re-apply if LAN Matrix access stops working after a firmware update.

---

### 2.4 Visitor Onboarding — QR Codes

Visitors connect and learn about the node via two QR codes printed on a card attached to the rack:

| QR Code | What it does | File |
|---|---|---|
| **WiFi QR** | Phone camera scans it, auto-joins `CommunityNode` WiFi | `qr-wifi.svg` |
| **Community Page QR** | Opens `http://192.168.8.10:8081` in their browser | `qr-community-page.svg` |

**Flow:** Scan WiFi QR to connect. Scan community page QR to see services, ATAK setup instructions, Element link, and app download QR codes. That's it.

> **Why not a captive portal?** Android's captive portal WebView auto-dismisses the instant the connectivity check passes — any redirect to the community page dies with it. This is a documented Android limitation (Google Issue Tracker #37046898) that affects all captive portal implementations including nodogsplash and enterprise solutions from Cisco, Fortinet, and Meraki. QR codes are simpler, more reliable, and require zero router/Pi configuration.

Regenerate QR codes if WiFi credentials or IPs change:

```bash
python generate_qr.py
```

Print both QR codes (WiFi + Community Page) on a laminated card and attach to the rack near the kiosk touchscreen. The field card (`M2_ATAK_FieldCard.pdf`) already includes the WiFi QR — add the community page QR to the next revision.

---

## 5. Phase 3: OS & Base Config — Both Nodes

**Do the following steps on BOTH Pi's.** Pi #1 (`comms`) first, then Pi #2 (`tactical`).

### 3.1 First Boot

1. Insert pre-flashed microSD card
2. Connect Ethernet (HDMI + keyboard optional — SSH is preferred)
3. Power on via USB-C
4. Wait ~60 seconds for first boot
5. SSH in:

```bash
ssh pi@192.168.8.10    # Pi #1 (once GL.iNet static lease is set)
ssh pi@192.168.8.20    # Pi #2
```

> First boot: if static leases aren't set yet, find the IP from GL.iNet's DHCP client list at `http://192.168.8.1` → Clients.

---

### 3.2 System Update & Hardening

Run on each Pi:

```bash
# Update system
sudo apt update && sudo apt full-upgrade -y

# Set hostname (should already be set from imager, verify)
hostnamectl set-hostname comms    # Pi #1
hostnamectl set-hostname tactical # Pi #2

# Set timezone
sudo timedatectl set-timezone America/Chicago   # adjust to your timezone
sudo timedatectl set-ntp true

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Configure SSH — key-based auth
# ⚠️ CRITICAL ORDER: copy your public key FIRST, then disable password auth.
# If you disable password auth before copying your key, you will lock yourself out.

# Step 1 — On your LAPTOP (not the Pi), copy your public key:
ssh-copy-id pi@192.168.8.10   # comms
ssh-copy-id pi@192.168.8.20   # tactical
# If you don't have an SSH key yet, generate one first on your laptop:
#   ssh-keygen -t ed25519 -C "m2-admin"

# Step 2 — Verify key login works BEFORE disabling password auth:
ssh pi@192.168.8.10   # should log in WITHOUT a password prompt
# Only proceed to Step 3 if key login works.

# Step 3 — Harden SSH config (on each Pi):
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Set: PermitRootLogin no
sudo systemctl restart ssh

# Configure automatic unattended security upgrades
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

### 3.3 Docker Install

Run on each Pi:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Verify
docker --version
docker compose version

# Log out and back in for group changes to take effect
exit
```

---

### 3.4 Enable Pi 5 PCIe and NVMe — Both Nodes

Run the following on **both** Pi #1 and Pi #2. Both nodes use the GeeekPi dual mount's built-in PCIe adapters, so each Pi has its NVMe SSD appear as `/dev/nvme0n1`.

```bash
# Edit boot config
sudo nano /boot/firmware/config.txt

# Add at the bottom:
# Enable PCIe Gen 3 for NVMe performance
dtparam=pciex1_gen=3

# Reboot
sudo reboot
```

After reboot, verify PCIe Gen 3 is active and NVMe is detected:

```bash
# Verify PCIe Gen 3 link speed
sudo dmesg | grep -i pcie | grep -i gen

# Confirm NVMe device is present
lsblk
# Pi #1 should show: nvme0n1 (WD SN740 256GB)
# Pi #2 should show: nvme0n1 (Crucial P310 1TB)
```

**Pi #1 — partition and mount NVMe (256GB, comms storage):**
```bash
sudo mkfs.ext4 /dev/nvme0n1
sudo mkdir -p /mnt/nvme
sudo mount /dev/nvme0n1 /mnt/nvme

# Add to fstab — use UUID for reliability
sudo blkid /dev/nvme0n1    # note the UUID value
# Replace YOUR-UUID-HERE with actual UUID from blkid output:
echo 'UUID=YOUR-UUID-HERE /mnt/nvme ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
```

**Pi #2 — partition NVMe (1TB, tactical/Monero storage):**

See Phase 5 (section 5.1) for the full Pi #2 partition layout and mount instructions.

---

### 3.5 Create Project Directory Structure

**Pi #1 (comms):**
```bash
sudo mkdir -p /opt/community-node/{config/{conduit,element,nginx/{ssl},i2pd,tor,cloudflared},data/{conduit,i2pd,tor,community-web},logs}
sudo chown -R $USER:$USER /opt/community-node
```

> The `community-web` directory must remain owned by the `ps` user so page updates can be deployed via `scp` without sudo. The `chown -R $USER` above sets this correctly at creation time. If you ever see scp updates not taking effect, re-run: `sudo chown -R ps:ps /opt/community-node/data/community-web/`

**Pi #2 (tactical):**
```bash
sudo mkdir -p /opt/tactical-node/{config/{mosquitto,headscale},data/{reticulum,nomadnet},logs}
sudo mkdir -p /mnt/nvme/monero/{data,wallets}
sudo chown -R $USER:$USER /opt/tactical-node
```

> The `/mnt/nvme` path for Monero will be set up in Phase 5 after partitioning the NVMe SSD.

---

### 3.6 Create .env Files (Before Any Deploy)

Each node needs a `.env` file in its project directory. The compose files read from these at startup. **Create these before running any `docker compose up`.**

**Pi #1 — `/opt/community-node/.env`:**
```bash
nano /opt/community-node/.env
```

```bash
# ── Image versions (pinned — update deliberately, not automatically) ──────
CONDUIT_VERSION=v0.10.12
ELEMENT_VERSION=v1.12.11
I2PD_VERSION=release-2.59.0

# ── Matrix server identity ────────────────────────────────────────────────
MATRIX_SERVER_NAME=m2.yourdomain.com

# ── Cloudflare Tunnel (only needed if using clearnet profile) ────────────
# Get this token from: dash.cloudflare.com → Zero Trust → Networks → Connectors
CLOUDFLARE_TUNNEL_TOKEN=CHANGE_ME_CLOUDFLARE_TOKEN
```

**Pi #2 — `/opt/tactical-node/.env`:**
```bash
nano /opt/tactical-node/.env
```

```bash
# ── Monero process user (must match your pi user UID/GID) ─────────────────
# Find yours with: id -u && id -g
FIXUID=1000
FIXGID=1000

# ── OpenTAK Server ────────────────────────────────────────────────────────
# OTS runs natively under systemd, not Docker.
# Admin password is set during the OTS installer — store in password manager.
# RabbitMQ password is set during OTS install.
# No .env variable needed here — OTS config is in /opt/opentakserver/
```

> Set permissions so only the `pi` user can read these files:
> ```bash
> chmod 600 /opt/community-node/.env
> chmod 600 /opt/tactical-node/.env
> ```

---

## 6. Phase 4: Node #1 — Communications Stack

All commands run on **Pi #1 (comms, 192.168.8.10)** unless noted.

### 4.1 Create the Docker Compose File

```bash
nano /opt/community-node/docker-compose.yml
```

```yaml
# /opt/community-node/docker-compose.yml
# Node #1 — Communications Stack

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

services:

  # ── Matrix homeserver ──────────────────────────────────────
  conduit:
    image: matrixconduit/matrix-conduit:${CONDUIT_VERSION:-v0.10.12}
    restart: unless-stopped
    networks:
      - community-net
    ports:
      - "127.0.0.1:6167:6167"   # localhost-only: admin tools use this; LAN clients use Nginx on :80
    volumes:
      - ./data/conduit:/var/lib/matrix-conduit
      - ./config/conduit/conduit.toml:/etc/matrix-conduit/conduit.toml:ro
    environment:
      CONDUIT_CONFIG: /etc/matrix-conduit/conduit.toml
    mem_limit: 512m
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:6167/_matrix/client/versions"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ── Element Web client ─────────────────────────────────────
  element-web:
    image: vectorim/element-web:${ELEMENT_VERSION:-v1.12.11}
    restart: unless-stopped
    networks:
      - community-net
    volumes:
      - ./config/element/element-config.json:/app/config.json:ro
    mem_limit: 64m

  # ── Nginx reverse proxy ────────────────────────────────────
  nginx:
    image: nginx:1.28.2-alpine3.23
    restart: unless-stopped
    networks:
      - community-net
    ports:
      - "80:80"
      - "443:443"
      - "8448:8448"
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/nginx/ssl:/etc/nginx/ssl:ro
      - ./data/community-web:/var/www/html:ro
    mem_limit: 128m
    depends_on:
      - conduit
      - element-web

  # ── I2P router ─────────────────────────────────────────────
  i2pd:
    image: purplei2p/i2pd:${I2PD_VERSION:-release-2.59.0}
    restart: unless-stopped
    networks:
      - community-net
      - i2p-net
    ports:
      - "7070:7070"     # web console
      - "4444:4444"     # HTTP proxy
      - "4447:4447"     # SOCKS proxy
      - "7656:7656"     # SAM bridge
    volumes:
      - ./data/i2pd:/home/i2pd/data
      - ./config/i2pd/i2pd.conf:/home/i2pd/i2pd.conf:ro
      - ./config/i2pd/tunnels.conf:/home/i2pd/tunnels.conf:ro
    mem_limit: 256m

  # ── Tor hidden services ────────────────────────────────────
  tor:
    image: osminogin/tor-simple:0.4.8.21
    restart: unless-stopped
    networks:
      - community-net
      - tor-net
    volumes:
      - ./config/tor/torrc:/etc/tor/torrc:ro
      - ./data/tor:/var/lib/tor
    mem_limit: 128m

  # ── Cloudflare Tunnel (optional — disable when air-gapped) ──
  cloudflared:
    image: cloudflare/cloudflared:2026.2.0
    restart: unless-stopped
    networks:
      - community-net
    # Token-based auth — no local credentials file needed.
    # Ingress rules are configured in the Cloudflare dashboard (Zero Trust → Networks → Connectors → Configure → Published application routes).
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    mem_limit: 128m
    profiles:
      - clearnet
      - full
```

---

### 4.1.5 Generate Security Tokens (Do This Before 4.2)

Two places in the config require strong random tokens. **Generate them now** and keep them in your password manager. You will use the same values in the config file AND in the registration curl command — if they don't match, registration will fail.

**Conduit registration token:**
```bash
openssl rand -hex 32
# Example: a3f8e1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
# Replace every instance of CHANGE_ME_STRONG_RANDOM_TOKEN with this value
```

**OpenTAK Server admin password:**
Set during the OTS native installer (Phase 5B). Store in password manager. No .env variable needed.

> Store both tokens in your password manager before proceeding. You cannot recover them — you can only regenerate and re-register.

---

### 4.2 Configure Conduit (Matrix)

> **Tech debt:** `matrixconduit/matrix-conduit` is abandoned as of 2025. The active community fork is `conduwuit`. The image pinned here is used as-is through CCC26. Plan migration to conduwuit post-event. Do not change the image or config now.

**Two-server Matrix architecture:**

The M2 node runs as a standalone federated Matrix homeserver with `server_name = "m2.yourdomain.com"`. All Matrix IDs on this node take the form `@user:m2.yourdomain.com`. A separate permanent homeserver (`yourdomain.com`) will be built on M1 as the primary identity server — that server will carry the primary operator account and the family/trusted-circle Space. The M2 server federates with M1 and with the wider Matrix network, so users on either server can join the same rooms and spaces. The M2 node is field-portable; when airgapped, its users still function locally — federation simply pauses until internet is restored.

**Access paths:**
- **LAN (at the event):** GL.iNet DNS override resolves `m2-matrix.yourdomain.com` and `m2.yourdomain.com` to `192.168.8.10` — clients reach the node directly, no Cloudflare in the path
- **Clearnet (node has internet):** Cloudflare tunnel routes `m2-matrix.yourdomain.com` and `m2.yourdomain.com` to nginx on Pi #1 — any internet-connected device can reach Matrix and Element
- **Headscale VPN (enrolled devices, including airgapped):** Headscale-enrolled devices connect directly to Pi #1's Headscale IP — use `http://<pi1-headscale-ip>` or add a MagicDNS entry `comms.m2` → Pi #1 Headscale IP for named access

```bash
nano /opt/community-node/config/conduit/conduit.toml
```

```toml
[global]
server_name = "m2.yourdomain.com"
database_path = "/var/lib/matrix-conduit/"
database_backend = "rocksdb"
port = 6167
max_request_size = 20_000_000
allow_registration = false
registration_token = "CHANGE_ME_STRONG_RANDOM_TOKEN"
allow_federation = true
allow_public_room_creation = true
log = "warn,rocket::launch=info,_=off,sled=off"
address = "0.0.0.0"
```

> Change `registration_token` to a random string before deploying. Generate one:
> ```bash
> openssl rand -hex 32
> ```

---

### 4.3 Configure Element Web

```bash
nano /opt/community-node/config/element/element-config.json
```

> ⚠️ **JSON files do not support comments.** This file must contain ONLY the JSON block below — no explanatory text, no headers, no `//` or `#` lines above or around it. Any non-JSON content will cause Element to display "Your Element is misconfigured / invalid JSON" and refuse to load. The file must start with `{` as the very first character.

```json
{
  "default_server_config": {
    "m.homeserver": {
      "base_url": "https://m2-m2-matrix.yourdomain.com",
      "server_name": "m2.yourdomain.com"
    }
  },
  "brand": "Community Node",
  "disable_custom_urls": true,
  "disable_guests": true,
  "disable_login_language_selector": true,
  "default_theme": "dark"
}
```

After saving, verify the file starts with `{` and nothing else:
```bash
head -1 /opt/community-node/config/element/element-config.json
# Must output exactly: {
```

Then restart Element Web:
```bash
cd /opt/community-node && docker compose restart element-web
```

> **Why port 80 (not 6167):** Conduit listens on port 6167 inside its Docker container — that port is internal and not exposed to the LAN. Nginx proxies external requests to Conduit on your behalf. Element Web clients connect through Nginx on port 80, so `base_url` must point to port 80 (the default HTTP port, which can be omitted from the URL). Using `:6167` here would cause Element Web to send API calls directly to a port that LAN clients can't reach.

---

### 4.4 Configure Tor Hidden Services

```bash
nano /opt/community-node/config/tor/torrc
```

```
SocksPort 0.0.0.0:9050
DataDirectory /var/lib/tor

# Matrix homeserver hidden service
HiddenServiceDir /var/lib/tor/matrix_hidden_service/
HiddenServicePort 443 nginx:443
HiddenServicePort 8448 conduit:6167
HiddenServiceVersion 3

# Element Web hidden service
HiddenServiceDir /var/lib/tor/element_hidden_service/
HiddenServicePort 80 nginx:8080
HiddenServiceVersion 3

# Community page hidden service (community-web-index.html at nginx:8081)
HiddenServiceDir /var/lib/tor/community_hidden_service/
HiddenServicePort 80 nginx:8081
HiddenServiceVersion 3
```

---

### 4.5 TLS Certificate Setup (Let's Encrypt via Cloudflare DNS)

A browser-trusted TLS certificate is required for Element Web to function correctly over HTTPS. Use Let's Encrypt with the Cloudflare DNS-01 challenge — no open inbound ports required.

**Prerequisites:**
- Domain `yourdomain.com` must be managed by Cloudflare DNS
- A Cloudflare API token with **Zone → DNS → Edit** permission for `yourdomain.com`

**Step 1 — Install certbot:**
```bash
sudo apt update && sudo apt install -y certbot python3-certbot-dns-cloudflare
```

**Step 2 — Save API token:**
```bash
sudo mkdir -p /etc/letsencrypt
sudo nano /etc/letsencrypt/cloudflare.ini
```
File contents:
```
dns_cloudflare_api_token = YOUR_TOKEN_HERE
```
Lock it down:
```bash
sudo chmod 600 /etc/letsencrypt/cloudflare.ini
```

**Step 3 — Request certificate (single-line for copy/paste):**
```bash
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini -d m2-matrix.yourdomain.com -d communitynode.yourdomain.com -d m2.yourdomain.com --agree-tos --non-interactive --email YOUR_EMAIL_HERE
```

Certbot creates DNS TXT records via the API, verifies them, then issues the cert. Files land at:
- `/etc/letsencrypt/live/m2-matrix.yourdomain.com/fullchain.pem`
- `/etc/letsencrypt/live/m2-matrix.yourdomain.com/privkey.pem`

Auto-renewal is configured automatically by certbot (systemd timer or cron).

**Step 4 — Mount certs into nginx container:**

Add to the nginx `volumes:` block in `/opt/community-node/docker-compose.yml`:
```yaml
- /etc/letsencrypt:/etc/letsencrypt:ro
```

**Step 5 — Update nginx.conf cert paths:**

In `/opt/community-node/config/nginx/nginx.conf`, replace both occurrences of the self-signed cert paths:
```
ssl_certificate /etc/letsencrypt/live/m2-matrix.yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/m2-matrix.yourdomain.com/privkey.pem;
```

**Step 6 — Recreate nginx container to pick up new volume:**
```bash
cd /opt/community-node && sudo docker compose --profile clearnet up -d nginx
```

> **Note:** Use `docker compose up -d` (not `restart`) after any docker-compose.yml volume changes — `restart` does not recreate the container with updated mounts.

> **Self-signed cert:** The original self-signed cert at `config/nginx/ssl/` is no longer used for ports 443/8448. It can be left in place — nginx.conf no longer references it.

---

### 4.5.1 Create Nginx Configuration

```bash
nano /opt/community-node/config/nginx/nginx.conf
```

```nginx
worker_processes auto;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 256;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 20M;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=matrix:10m rate=30r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

    # ── Matrix API — HTTP (LAN access by IP, CF Tunnel clearnet) ──
    server {
        listen 80;
        listen [::]:80;
        server_name _;

        limit_req zone=matrix burst=50 nodelay;

        location /.well-known/matrix/server {
            default_type application/json;
            add_header Access-Control-Allow-Origin *;
            return 200 '{"m.server":"m2-matrix.yourdomain.com:443"}';
        }

        location /.well-known/matrix/client {
            default_type application/json;
            add_header Access-Control-Allow-Origin *;
            return 200 '{"m.homeserver":{"base_url":"https://m2-matrix.yourdomain.com"}}';
        }

        location / {
            proxy_pass http://conduit:6167;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
        }
    }

    # ── Matrix API — HTTPS (local TLS, Tor hidden service) ──────
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        server_name _;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        limit_req zone=matrix burst=50 nodelay;

        location /.well-known/matrix/server {
            default_type application/json;
            add_header Access-Control-Allow-Origin *;
            return 200 '{"m.server":"m2-matrix.yourdomain.com:443"}';
        }

        location /.well-known/matrix/client {
            default_type application/json;
            add_header Access-Control-Allow-Origin *;
            return 200 '{"m.homeserver":{"base_url":"https://m2-matrix.yourdomain.com"}}';
        }

        location / {
            proxy_pass http://conduit:6167;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_buffering off;
        }
    }

    # ── Matrix Federation (port 8448) ────────────────────────────
    server {
        listen 8448 ssl;
        listen [::]:8448 ssl;
        server_name _;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://conduit:6167;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_buffering off;
        }
    }

    # ── Element Web (port 8080 — Tor/I2P access) ─────────────────
    server {
        listen 8080;
        listen [::]:8080;
        server_name _;

        limit_req zone=general burst=20 nodelay;

        location / {
            proxy_pass http://element-web:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # ── Community Web (port 8081 — static pages) ─────────────────
    server {
        listen 8081;
        listen [::]:8081;
        server_name _;

        limit_req zone=general burst=20 nodelay;

        root /var/www/html;
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }
    }
}
```

---

### 4.5.2 Create i2pd Configuration

```bash
nano /opt/community-node/config/i2pd/i2pd.conf
```

```ini
[general]
loglevel = warn
logfile = /home/i2pd/data/i2pd.log

[system]
# L = 32 KBps shared — adequate for community node, conserves Pi resources
bandwidth = L

[http]
enabled = true
address = 0.0.0.0
port = 7070

[httpproxy]
enabled = true
address = 0.0.0.0
port = 4444

[socksproxy]
enabled = true
address = 0.0.0.0
port = 4447

[sam]
enabled = true
address = 0.0.0.0
port = 7656

[ntcp2]
enabled = true
port = 0

[ssu2]
enabled = true
port = 0
```

```bash
nano /opt/community-node/config/i2pd/tunnels.conf
```

```ini
# I2P tunnel for Matrix API (routes via nginx on Docker network)
[matrix-i2p]
type = http
host = nginx
port = 80
keys = matrix-i2p.dat

# I2P eepsite for community web pages (routes via nginx on Docker network)
[community-eepsite]
type = http
host = nginx
port = 8081
keys = community-eepsite.dat
```

---

### 4.5.3 Cloudflare Tunnel Setup (Clearnet Access)

The `CLOUDFLARE_TUNNEL_TOKEN` in comms `.env` enables clearnet access to Matrix, Element, and TAK when the node has internet. No local config file is needed — all ingress routing is configured in the Cloudflare dashboard.

**Steps:**
1. Go to `dash.cloudflare.com` → Zero Trust → Networks → Connectors
2. Click **Create a connector** → name it `m2-community-node`
3. Copy the tunnel token — paste it into `/opt/community-node/.env` as `CLOUDFLARE_TUNNEL_TOKEN=<token>`
4. Click the connector name → **Configure** → **Published application routes** tab → add each route:

| Subdomain | Domain | Service |
|---|---|---|
| `matrix` | `yourdomain.com` | `http://nginx:80` |
| `m2` | `yourdomain.com` | `http://nginx:80` |
| `element` | `yourdomain.com` | `http://nginx:8080` |
| `tak` | `yourdomain.com` | `http://192.168.8.20:8080` |

5. Save — the tunnel will connect automatically when cloudflared starts with the `clearnet` profile.

> **Note:** Use container names (`nginx:80`, `nginx:8080`) for services on the **same** Docker host (Pi #1). Use the LAN IP (`192.168.8.20`) for services on Pi #2 — cloudflared can reach the LAN from inside Docker via the host's routing table.

> **TLS:** Cloudflare terminates HTTPS for clearnet traffic. The tunnel delivers plain HTTP to nginx internally. The Let's Encrypt cert handles port 443 for LAN HTTPS access (via GL.iNet hosts file override).

> **OTS Web Map access:** `https://tak.yourdomain.com` gives anyone with the URL a live view of the tactical map — team positions, markers, data packages. This is view + admin access to OTS, so protect it with Cloudflare Access (§4.5.4) before enabling in production.

---

### 4.5.4 Cloudflare Access — Zero Trust Gate (Optional)

Cloudflare Access puts a login screen in front of any tunnel route. Without it, anyone who discovers `tak.yourdomain.com` or `communitynode.yourdomain.com` can access the service directly. With it, users must authenticate before Cloudflare proxies their request.

**What it is:** Cloudflare's zero-trust reverse proxy. Runs entirely on Cloudflare's infrastructure — no software on your Pis. Free tier supports 50 users.

**Step 1 — Create the Access Application**

1. `dash.cloudflare.com` → Zero Trust → Access controls → Applications → **Add an application**
2. Select type: **Self-hosted**
3. Application name: `OTS Web Map`
4. Session Duration: `24 hours`
5. Click **+ Add public hostname** — this expands the domain fields:
   - Subdomain: `tak`
   - Domain: select `yourdomain.com` from the dropdown
6. Scroll down past Browser rendering settings (leave defaults)

**Step 2 — Create an Access Policy**

Still on the same page, scroll to **Create reusable application policies** → click the blue **Add a policy** button:

| Field | Value |
|---|---|
| Policy name | `Approved Operators` |
| Action | `Allow` |
| Include rule | Emails — add each approved operator's email |

> For quick field deployment, use **Email one-time PIN** as the identity provider. Users enter their email, get a 6-digit code, and are in. No accounts, no passwords, no OAuth setup.

7. Click **Next** through Experience settings and Advanced settings (leave defaults)
8. Click **Save**

**Step 3 — Verify the identity provider**

1. Zero Trust → Settings → Authentication → Login methods
2. Confirm **One-time PIN** is enabled (should be on by default)
3. Optionally add Google or GitHub for permanent team members

**Step 4 — Repeat for other sensitive routes**

Create separate Access applications for:

| Route | Recommended? | Why |
|---|---|---|
| `tak.yourdomain.com` | **Yes** | Full OTS admin + live map |
| `communitynode.yourdomain.com` | Optional | Element Web is already behind Matrix login |
| `m2-matrix.yourdomain.com` | No | Federation requires unauthenticated access |

> **Field tradeoff:** During an active incident, you may want to temporarily remove Access from the OTS web map so any responder can see positions without authenticating. Toggle the policy off in the dashboard — takes effect immediately.

> **Note:** Do not apply Cloudflare Access to `m2-matrix.yourdomain.com` or `m2.yourdomain.com` — federation requires unauthenticated access for server-to-server requests. Locking these routes breaks federation with external Matrix servers.

---

### 4.5.5 Verify Federation

Run this after the Cloudflare tunnel is active and Conduit is up.

**Step 1 — Confirm `.well-known` delegation resolves:**

```bash
curl -s https://m2.yourdomain.com/.well-known/matrix/server
curl -s https://m2.yourdomain.com/.well-known/matrix/client
```

Expected:
```json
{"m.server":"m2-matrix.yourdomain.com:443"}
{"m.homeserver":{"base_url":"https://m2-matrix.yourdomain.com"}}
```

**Step 2 — Run the Matrix federation tester:**

From any browser: `https://federationtester.matrix.org/#m2.yourdomain.com`

Expected: all checks green. Common failures:
- **DNS resolution failed** — `m2.yourdomain.com` Cloudflare tunnel route missing or not yet propagated
- **Connection refused on :8448** — federation is served on port 443 via `.well-known` delegation; if the tester tries 8448 directly, the `.well-known` response was not returned correctly
- **Certificate error** — cert does not cover `m2.yourdomain.com`; re-issue certbot with `-d m2.yourdomain.com` added

**Step 3 — Test a cross-server room join:**

From an account on `matrix.org` (or any other public homeserver), join a room hosted on `m2.yourdomain.com` using the full room alias. Confirm messages deliver in both directions.

---

### 4.6 Start Node #1 Stack

```bash
cd /opt/community-node

# Start core services (no Cloudflare tunnel yet)
docker compose up -d conduit element-web nginx i2pd tor

# Check logs
docker compose logs -f --tail=50

# Verify all containers are healthy
docker compose ps
```

**Wait ~2 minutes for Conduit to initialize**, then register the admin user:

```bash
curl -X POST "http://localhost:6167/_matrix/client/v3/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "STRONG_PASSWORD_HERE",
    "auth": {
      "type": "m.login.registration_token",
      "token": "CHANGE_ME_STRONG_RANDOM_TOKEN"
    }
  }'
```

**Retrieve Tor .onion addresses (after ~5 min for Tor to bootstrap):**

```bash
docker exec tor cat /var/lib/tor/matrix_hidden_service/hostname
docker exec tor cat /var/lib/tor/element_hidden_service/hostname
docker exec tor cat /var/lib/tor/community_hidden_service/hostname
```

> Record your .onion addresses — you will need them for QR codes, kiosk config, and sharing with members:
>
> | Service | .onion Address |
> |---|---|
> | Matrix API (homeserver) | *(paste output of first command above)* |
> | Element Web (chat client) | *(paste output of second command above)* |
> | Community Page (info/connect) | *(paste output of third command above)* |
>
> All three require Tor Browser. The community page onion is the recommended link to share with new members — it loads the info and connection guide. The Element Web onion is for direct chat access. Point Matrix clients (FluffyChat, Element mobile) at the Matrix API onion as the homeserver.

---

### 4.7 AdGuard DNS Setup (Split-DNS)

AdGuard runs on Pi #1 as the LAN DNS resolver. Its critical job is **split-DNS**: intercepting DNS queries from devices on the network and resolving your service domains to their LAN IPs instead of the public internet. Without this, ATAK cert enrollment, Element, and Headscale connections all leave the LAN to reach Cloudflare — which means they fail when internet is down.

**Start the container:**

```bash
# [SSH — comms-lan]
cd /opt/community-node
docker compose up -d adguard
docker compose logs adguard --tail=20
```

**First-run wizard** — open `http://192.168.8.10:3000` from a browser on the LAN:

1. Click **Get Started**
2. Leave Admin Web Interface on port `3000`
3. Leave DNS server on port `53` — this must stay as-is
4. Set an admin username and password — store in `M2_SECRETS.md`
5. Click **Next** through the remaining screens, then **Open Dashboard**

**Add DNS rewrites** — in the AdGuard dashboard, go to **Filters → DNS rewrites → Add DNS rewrite**:

| Domain | Answer |
|---|---|
| `element.yourdomain.com` | `192.168.8.10` |
| `m2-matrix.yourdomain.com` | `192.168.8.10` |
| `tak.yourdomain.com` | `192.168.8.20` |
| `m2vpn.yourdomain.com` | `192.168.8.20` |
| `atakenroll.yourdomain.com` | `192.168.8.20` |

Replace `yourdomain.com` with your actual domain. Add one entry at a time — each domain gets its own row.

**Configure the router to use AdGuard as DNS** — on the GL.iNet admin panel:

1. Go to **Network → DHCP**
2. Set **DNS Server 1** to `192.168.8.10`
3. Clear DNS Server 2 (leave blank or set to `1.1.1.1` as fallback)
4. Save and apply

Devices that reconnect to WiFi will now receive AdGuard as their DNS server. Existing connections need to reconnect or flush their DNS cache (`ipconfig /flushdns` on Windows, toggle WiFi on Android/iOS).

**Verify:**

```bash
# From a device on the LAN — should return 192.168.8.10 (not a Cloudflare IP)
nslookup element.yourdomain.com 192.168.8.10

# Should return 192.168.8.20
nslookup atakenroll.yourdomain.com 192.168.8.10
```

> **Why this matters for ATAK:** The cert enrollment page is served from `atakenroll.yourdomain.com:8447`. If DNS resolves that domain to a Cloudflare IP, ATAK's enrollment flow goes out to the internet and fails when you're offline. With the split-DNS rewrite, it resolves directly to Pi #2's LAN IP and works with no internet required.

---

## 7. Phase 5: Node #2 — Tactical/Crypto Stack

All commands run on **Pi #2 (tactical, 192.168.8.20)** unless noted.

### 5.1 Partition and Mount the 1TB NVMe SSD (Pi #2)

Pi #2's Crucial P310 1TB NVMe is already physically installed in the GeeekPi dual mount's right NVMe adapter slot and appears as `/dev/nvme0n1` after the PCIe Gen 3 configuration in Phase 3.

**Recommended approach: OS stays on microSD, NVMe is data-only.**
This is simpler, provides automatic fallback boot from microSD, and requires no EEPROM changes.

Partition layout:
```
/dev/nvme0n1p1    900GB   /mnt/nvme        (ext4, Monero + ATAK data + backups)
(~100GB unpartitioned for wear leveling)
```

```bash
# Verify NVMe is present
lsblk
# Should show: nvme0n1 (1TB NVMe)

# Create a single data partition (no boot partition needed — OS stays on microSD)
sudo fdisk /dev/nvme0n1
# Create p1: +900G  (ext4 — /mnt/nvme)
# Leave remaining ~100GB unpartitioned for wear leveling
# Write and exit

# Format the data partition
sudo mkfs.ext4 /dev/nvme0n1p1

# Mount
sudo mkdir -p /mnt/nvme
sudo mount /dev/nvme0n1p1 /mnt/nvme

# Auto-mount on boot — use UUID (more reliable than device name; name can shift if drives are added)
sudo blkid /dev/nvme0n1p1    # copy the UUID value from this output
echo 'UUID=YOUR-UUID-HERE /mnt/nvme ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
# Replace YOUR-UUID-HERE with the actual UUID from blkid output above

# Create directory structure
sudo mkdir -p /mnt/nvme/monero/{data,wallets}
sudo chown -R $USER:$USER /mnt/nvme
```

> **Optional: migrate OS to NVMe after initial build is confirmed working.** To boot from NVMe: `sudo raspi-config` → Advanced Options → Boot Order → NVMe/USB Boot. Then clone microSD to NVMe using `rpi-clone` or `dd`. Only do this after all services are running and stable — the microSD is your recovery boot until then.

> Performance note: NVMe via the GeeekPi dual mount's PCIe adapter delivers approximately 106,000–197,000 4K random IOPS (Gen 3 with `dtparam=pciex1_gen=3`), versus ~29,000 IOPS on a USB SATA adapter — a 3.5–7× improvement that benefits Monero's LMDB database performance.

---

### 5.2 Transfer Monero LMDB to Pi #2

**Your x86 pre-sync from Phase 0 must be complete before this step.**

The Monero LMDB data folder is typically ~95–110 GB pruned.

**Stop monerod on your x86 machine first** — LMDB will corrupt if copied while running.
- Windows: close the monerod window or kill the process in Task Manager
- Linux: `kill $(pgrep monerod)`

#### Option A — USB stick (recommended if on WiFi)

1. Format a 128GB+ USB stick as exFAT or NTFS
2. Copy `C:\MoneroNode\data\lmdb` folder to the root of the stick on Windows
3. Plug stick into Pi #2 front USB 3.0 port
4. On Pi #2:

```bash
# Find the USB stick device
lsblk
# It will appear as /dev/sda1 or similar

# Mount it
sudo mkdir -p /mnt/usb
sudo mount /dev/sda1 /mnt/usb

# Copy LMDB to NVMe
mkdir -p /mnt/nvme/monero/data/lmdb
cp -r /mnt/usb/lmdb/. /mnt/nvme/monero/data/lmdb/

# Unmount and remove stick
sudo umount /mnt/usb
```

> USB 3.0 stick transfers ~95GB in 15–30 minutes. Far faster than WiFi rsync.

#### Option B — Rsync over network

```bash
# From WSL on Windows:
wsl rsync -avP /mnt/c/MoneroNode/data/lmdb/ pi@192.168.8.20:/mnt/nvme/monero/data/lmdb/

# From Git Bash on Windows:
rsync -avP /c/MoneroNode/data/lmdb/ pi@192.168.8.20:/mnt/nvme/monero/data/lmdb/
```

> On gigabit wired LAN: ~15–20 minutes. On WiFi: 1–2 hours.

---

### 5.3 Create the Docker Compose File

```bash
nano /opt/tactical-node/docker-compose.yml
```

```yaml
# /opt/tactical-node/docker-compose.yml
# Node #2 — Tactical/Crypto Stack

services:

  # ── Monero node ────────────────────────────────────────────
  monerod:
    image: ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5
    restart: unless-stopped
    user: "${FIXUID:-1000}:${FIXGID:-1000}"
    network_mode: host
    volumes:
      - /mnt/nvme/monero/data:/home/monero/.bitmonero
    command:
      - --rpc-restricted-bind-ip=127.0.0.1
      - --rpc-restricted-bind-port=18089
      # SECURITY: RPC is localhost-only. Access remotely via Tailscale/Headscale VPN.
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
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
        reservations:
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://127.0.0.1:18089/get_info"]
      # 18089 = restricted RPC (the port actually bound by --rpc-restricted-bind-port)
      # 18081 = unrestricted full RPC (not opened — healthcheck was wrong)
      interval: 60s
      timeout: 15s
      retries: 3

  # ── OpenTAK Server (ATAK) ─────────────────────────────────
  # OTS runs NATIVELY under systemd — NOT in Docker.
  # Install: see Phase 5B below.
  # Status: systemctl status opentakserver
  # Ports: 8080 (HTTP UI), 8088 (CoT TCP), 8089 (CoT SSL),
  #        8443 (HTTPS UI), 8446 (cert enrollment)
  # Web UI: http://192.168.8.20:8080

  # ── Reticulum + NomadNet ───────────────────────────────────
  # WARNING: this container runs pip install on every startup.
  # In air-gap/offline mode this will fail on cold start — container will not launch
  # because pip cannot reach PyPI. Long-term fix: build a custom image with packages
  # baked in. For field deployment, ensure at least one successful startup with internet
  # access before going air-gap. Packages are also unpinned — pin them in a future sprint.
  reticulum:
    image: python:3.12.12-slim-bookworm
    restart: unless-stopped
    network_mode: host
    command: >
      bash -c "pip install --upgrade pip -q &&
               pip install --quiet rns nomadnet lxmf &&
               rnsd --config /root/.reticulum -v"
    # -v = verbose logging to stdout (captured by Docker)
    # Monitor with: docker compose logs --tail=50 reticulum
    # Live status:  docker exec tactical-node-reticulum-1 rnstatus
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0   # Heltec V3 LEFT RNode LoRa (connect in Phase 6)
    volumes:
      - ./data/reticulum:/root/.reticulum
    ports:
      - "4242:4242"     # TCP interface
      - "37428:37428"   # shared instance

  nomadnet:
    image: python:3.12.12-slim-bookworm
    restart: unless-stopped
    network_mode: host
    command: >
      bash -c "pip install --quiet nomadnet &&
               nomadnet --daemon --config /root/.nomadnetwork"
    volumes:
      - ./data/nomadnet:/root/.nomadnetwork
    depends_on:
      - reticulum

  # ── MQTT Broker ────────────────────────────────────────────
  mosquitto:
    image: eclipse-mosquitto:2.0.22
    restart: unless-stopped
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./config/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - ./data/mosquitto:/mosquitto/data
      - ./logs/mosquitto:/mosquitto/log

  # ── Headscale (Tailscale control plane) ───────────────────
  headscale:
    # ⚠️ Breaking changes between 0.23 and 0.28 — read: github.com/juanfont/headscale/releases
    # Key changes: removed `headscale nodes move`, stricter SSH policy, tags-as-identity
    image: headscale/headscale:0.28.0
    restart: unless-stopped
    ports:
      - "443:443"
      - "50443:50443"
    volumes:
      - ./config/headscale:/etc/headscale
      - ./data/headscale:/var/lib/headscale
      - /etc/letsencrypt:/etc/letsencrypt:ro
    command: serve
    profiles:
      - vpn
      - full

volumes:
  monero-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/nvme/monero/data
  wallet-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/nvme/monero/wallets
```

---

### 5.3.1 Configure Mosquitto

The Mosquitto container **will crash on startup without a config file** — it requires one at `/mosquitto/config/mosquitto.conf`. Create it before the first `docker compose up`:

```bash
mkdir -p /opt/tactical-node/config/mosquitto
nano /opt/tactical-node/config/mosquitto/mosquitto.conf
```

```
# Mosquitto 2.x minimal configuration for community node
# https://mosquitto.org/man/mosquitto-conf-5.html

# ── Persistence ──────────────────────────────────────────────────────────
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# ── Local LAN listener (unauthenticated — LAN-only, no internet exposure) ─
listener 1883 0.0.0.0
allow_anonymous true

# ── WebSocket listener (for browser-based MQTT clients) ──────────────────
listener 9001 0.0.0.0
protocol websockets
allow_anonymous true

# ── NOTES ─────────────────────────────────────────────────────────────────
# This config is intentionally open for LAN use.
# If you expose Mosquitto beyond the LAN (e.g., via Tailscale):
#   1. Set allow_anonymous false
#   2. Create a password file: mosquitto_passwd /mosquitto/config/passwd <user>
#   3. Add: password_file /mosquitto/config/passwd
#   4. Consider TLS: add certfile/keyfile/cafile directives
```

---

### 5.3.2 Configure Headscale

Headscale requires both a TLS certificate and a `config.yaml` before it will start.

**Step 1 — Issue TLS certificate for Headscale**

```bash
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-dns-cloudflare
```

```bash
sudo mkdir -p /etc/cloudflare
```

```bash
sudo sh -c 'echo "dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN" > /etc/cloudflare/cloudflare.ini'
```

```bash
sudo chmod 600 /etc/cloudflare/cloudflare.ini
```

```bash
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials /etc/cloudflare/cloudflare.ini -d m2vpn.yourdomain.com --email YOUR_EMAIL --agree-tos --non-interactive
```

Certificate saved at: `/etc/letsencrypt/live/m2vpn.yourdomain.com/fullchain.pem`

**Step 2 — Add certbot renewal hook**

```bash
sudo sh -c 'echo "#!/bin/bash" > /etc/letsencrypt/renewal-hooks/deploy/headscale.sh'
```

```bash
sudo sh -c 'echo "docker compose -f /opt/tactical-node/docker-compose.yml --profile vpn restart headscale" >> /etc/letsencrypt/renewal-hooks/deploy/headscale.sh'
```

```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/headscale.sh
```

**Step 3 — Create config.yaml**

```bash
mkdir -p /opt/tactical-node/config/headscale
nano /opt/tactical-node/config/headscale/config.yaml
```

```yaml
# Headscale 0.28.0 — Self-hosted Tailscale coordination server
  # Full reference: headscale.net/docs/ref/configuration/
  #
  # IMPORTANT: All keys in this file use 2-space indentation throughout.
  # This is intentional — do not mix indentation levels or the YAML parser will fail.
  # IMPORTANT: Headscale 0.28.0 has breaking changes from 0.23

  # ── Server identity ───────────────────────────────────────────────────────────
  server_url: "https://m2vpn.yourdomain.com"
  listen_addr: "0.0.0.0:443"
  tls_cert_path: /etc/letsencrypt/live/m2vpn.yourdomain.com/fullchain.pem
  tls_key_path: /etc/letsencrypt/live/m2vpn.yourdomain.com/privkey.pem
  metrics_listen_addr: "127.0.0.1:9090"
  grpc_listen_addr: "0.0.0.0:50443"
  grpc_allow_insecure: false

  # ── Key material ──────────────────────────────────────────────────────────────
  private_key_path: /var/lib/headscale/private.key
  noise:
    private_key_path: /var/lib/headscale/noise_private.key

  # ── VPN address pool ──────────────────────────────────────────────────────────
  prefixes:
    v4: "100.64.1.0/24"
    v6: "fd7a:115c:a1e0::/48"
  allocation: sequential

  # ── DNS ───────────────────────────────────────────────────────────────────────
  dns:
    magic_dns: true
    base_domain: vpn.community.local
    nameservers:
      global:
        - 8.8.8.8
        - 1.1.1.1

  # ── Database ──────────────────────────────────────────────────────────────────
  database:
    type: sqlite3
    sqlite:
      path: /var/lib/headscale/db.sqlite

  log:
    level: info

  # ── DERP relay servers ────────────────────────────────────────────────────────
  derp:
    server:
      enabled: false
    urls:
      - https://controlplane.tailscale.com/derpmap/default
    auto_update_enabled: true
    update_frequency: 24h
```

**Step 4 — Start Headscale and create users**

```bash
cd /opt/tactical-node && sudo docker compose --profile vpn up -d headscale
```

```bash
sudo docker exec tactical-node-headscale-1 headscale users create admin
```

```bash
sudo docker exec tactical-node-headscale-1 headscale users create community
```

```bash
sudo docker exec tactical-node-headscale-1 headscale preauthkeys create --user 1 --expiration 90d --reusable
```

**Step 5 — Connect client devices**

**[Windows — PowerShell Administrator]**
```powershell
tailscale up --login-server https://m2vpn.yourdomain.com --authkey <key> --reset
```

**Step 6 — Rename nodes**

```bash
sudo docker exec tactical-node-headscale-1 headscale nodes rename --identifier 1 mike-pc
```

> **Container name:** Always use `tactical-node-headscale-1` (not `headscale`) for `docker exec` commands.

---

### 5.3.3 Monero Wallet RPC

#### What This Is and Why You Want It

**The one-sentence pitch:** Your community can transact in Monero without trusting anyone outside the community — ever.

When a community member uses Monero — even with their own wallet on their own phone — their wallet has to ask *someone's* server "is this transaction valid?" By default, that's a random stranger's node. That stranger sees their transaction queries, can correlate addresses to IPs, and can lie about balances.

The community node's `monerod` gives members a node they trust by provenance — run by their own community, on hardware they can physically inspect. `monero-wallet-rpc` is the operator layer on top of that: it lets the community receive donations, verify payments, and manage a community fund wallet programmatically — all self-verified, no third party ever in the loop.

Running Monero without a trusted node is like running Matrix but routing your messages through Signal's servers. The node exists — wallet-rpc is what makes it *usable as an institution*, not just a relay others happen to connect to.

---

The community node runs a full Monero node (`monerod`) that stays synced to the live blockchain. That node is the foundation — but to actually USE it from a wallet, you have two options:

**Option A — Point your existing wallet at the node as its daemon (no wallet-rpc needed):**
Any Monero wallet (Feather, Cake, monero-gui) lets you specify a custom daemon address. Point it to the community node's `monerod` and your wallet software queries YOUR node instead of a random third-party node. Your private keys never leave your device — the node just answers blockchain questions. This is the privacy benefit. Anyone on the community node's Tailscale network can do this.

**Option B — Monero Wallet RPC (operator wallet on the Pi):**
`monero-wallet-rpc` is a JSON-RPC API server that wraps a wallet file on Pi #2. The wallet file lives on the Pi — it holds a set of Monero private keys and syncs its history against the local `monerod`. This is for the operator: receiving community donations, generating subaddresses for different purposes, checking balances, or automating payment verification via API. Access is SSH-tunnel-only — it is never exposed to LAN or clearnet.

**The two options are independent.** Community members use Option A (point their wallet at the daemon). The operator uses Option B for the community fund wallet. Both verify transactions against the same local `monerod` node.

> **Key point:** The wallet file created in this section is the operator's community node wallet. It is NOT a passthrough for other people's wallets. If you want to use your personal existing wallet, restore it from its 25-word seed in Step 1 below. If you want a fresh community wallet, generate a new one.

---

#### Step 1 — Create the Wallet File (interactive — SAVE THE SEED)

**[SSH — Pi #2]**

```bash
monero-wallet-cli --daemon-address=127.0.0.1:18081 --trusted-daemon --generate-new-wallet=/mnt/nvme/monero/wallets/community
```

The CLI will prompt you for:
1. **Password** — set a strong password and write it down; you'll need it for the service file
2. **Language** — choose `English` (option 1) for the 25-word seed
3. The **25-word seed phrase** will be printed — **write it down immediately and store offline**

To use your existing wallet instead of generating a new one, replace `--generate-new-wallet` with `--restore-deterministic-wallet` and enter your existing seed when prompted.

After the wallet is created, type `exit` to quit the CLI.

---

#### Step 2 — Create the RPC Credentials File

**[SSH — Pi #2]**

```bash
echo "community:REPLACE_WITH_STRONG_PASSWORD" > /mnt/nvme/monero/wallets/.rpc-login
```

```bash
chmod 600 /mnt/nvme/monero/wallets/.rpc-login
```

Replace `REPLACE_WITH_STRONG_PASSWORD` with a unique password (different from the wallet password). This is the HTTP digest auth credential used to connect to the RPC endpoint.

**Also create the wallet password file** (this is the wallet encryption password you set during `monero-wallet-cli` creation — NOT the RPC credential above):

```bash
nano /mnt/nvme/monero/wallets/.wallet-password
```

Type just the wallet password, nothing else. Save and exit.

```bash
chmod 600 /mnt/nvme/monero/wallets/.wallet-password
```

---

#### Step 3 — Create the Systemd Service

**[SSH — Pi #2]**

```bash
sudo nano /etc/systemd/system/monero-wallet-rpc.service
```

Paste the following — use **nano**, one line at a time is fine:

```ini
# monero-wallet-rpc.service
# Exposes the community Monero wallet as a JSON-RPC API on loopback only.
# Access via SSH tunnel: ssh -L 18083:localhost:18083 tactical
# Never expose port 18083 to LAN or clearnet.

[Unit]
Description=Monero Wallet RPC
After=network.target

[Service]
User=ps
# --rpc-bind-ip=127.0.0.1 — loopback only; SSH tunnel required for remote access
# --trusted-daemon — skip Monero's spam-prevention checks (safe because we control monerod)
# --password-file — wallet encryption password (different from RPC auth credentials)
# --rpc-login — HTTP digest auth for the RPC endpoint (username:password)
# Port 18083 — wallet-rpc. Monerod uses 18080 (P2P) + 18081 (RPC); wallet-rpc must use a different port.
ExecStart=/usr/local/bin/monero-wallet-rpc --daemon-address=127.0.0.1:18081 --trusted-daemon --rpc-bind-ip=127.0.0.1 --rpc-bind-port=18083 --wallet-file=/mnt/nvme/monero/wallets/community --password-file=/mnt/nvme/monero/wallets/.wallet-password --rpc-login=community:REPLACE_WITH_RPC_PASSWORD --log-level=0 --log-file=/var/log/monero-wallet-rpc.log
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable monero-wallet-rpc
```

```bash
sudo systemctl start monero-wallet-rpc
```

```bash
sudo systemctl status monero-wallet-rpc
```

Expected: `Active: active (running)`. It will take 1–2 minutes to complete the initial wallet scan against the local `monerod` blockchain.

---

#### Step 4 — Confirm Port 18083 Is Loopback Only

The service binds to `127.0.0.1` (loopback only), so it is inaccessible from the network. Confirm with:

**[SSH — Pi #2]**

```bash
ss -tlnp | grep 18083
```

Expected output includes `127.0.0.1:18083` — not `0.0.0.0:18083`. If you see `0.0.0.0`, the `--rpc-bind-ip` flag is wrong — fix it in the systemd unit.

---

#### Step 5 — Test via SSH Tunnel

**[Windows — PowerShell]**

```powershell
ssh -L 18083:localhost:18083 tactical
```

Leave that SSH session open. Test the RPC from the **Pi itself** (PowerShell mangles JSON quoting — always test from the Pi):

**[SSH — Pi #2]**

```bash
curl --digest -u community:REPLACE_WITH_RPC_PASSWORD -d '{"jsonrpc":"2.0","id":"0","method":"get_balance"}' -H "Content-Type: application/json" http://127.0.0.1:18083/json_rpc
```

Expected: JSON response containing `"balance"` and `"unlocked_balance"`. If you see a `401 Unauthorized`, the credentials don't match the `--rpc-login` value in the systemd service file.

> **Note:** monero-wallet-rpc uses HTTP **digest** auth (not basic). The `--digest` flag is required with curl. Feather Wallet handles this automatically.

---

#### Step 6 — Connect Feather Wallet via SSH Tunnel

This is how you use Feather Wallet on Windows against the community node's wallet-rpc:

**[Windows — PowerShell (keep this session open)]**

```powershell
ssh -L 18083:localhost:18083 tactical
```

In Feather Wallet:
1. **File → Settings → Node** — set to `127.0.0.1:18081` (via a separate SSH tunnel to Pi #2) or via Tailscale/Headscale VPN using the Tailscale IP `100.64.1.1:18089` (Monero RPC is bound to 127.0.0.1 on Pi #2 and is not reachable from LAN WiFi)
2. To use wallet-rpc instead: **File → Open from node** → enter `http://127.0.0.1:18083` with credentials `community` / your RPC password

> **Most users should just use Option A** (set Feather's node to `100.64.1.1:18089` via Tailscale VPN, or SSH-tunnel to `127.0.0.1:18081`) and keep their wallet file on their own machine. wallet-rpc is for the operator managing the community wallet. Note: `192.168.8.20:18089` is NOT reachable from LAN — RPC is localhost-only on Pi #2.

---

#### Wallet RPC Log and Status

**[SSH — Pi #2]**

```bash
sudo journalctl -u monero-wallet-rpc -f
```

```bash
sudo journalctl -u monero-wallet-rpc --since "10 minutes ago"
```

---

#### Community Member Access (Option A — No wallet-rpc required)

Any community member connected via Tailscale/Headscale can point their Feather Wallet at the node's restricted RPC. The RPC is bound to `127.0.0.1` on Pi #2 — it is not reachable from LAN WiFi directly. Access requires Tailscale VPN:

**Feather Wallet → File → Settings → Node:**

```
http://100.64.1.1:18089
```

> LAN WiFi clients (`192.168.8.x`) cannot reach port 18089 directly — the RPC is localhost-only on Pi #2. Tailscale VPN is required. Community members must be enrolled in Headscale VPN to use the node as their daemon.

This gives them transaction verification against the community's own node. Their wallet keys stay on their device.

---

### 5.3.4 Cloudflare Dynamic DNS for Headscale

When the community node is deployed in the field (cellular hotspot, Starlink, etc.), the public IP changes. This script detects the current public IP, compares it to the Cloudflare DNS A record for `m2vpn.yourdomain.com`, and updates it automatically via the Cloudflare API. Runs every 5 minutes via systemd timer.

Without this, every IP change would require manual DNS updates before Headscale clients can reconnect.

#### Step 1 — Create the Update Script

**[SSH — Pi #2]**

```bash
sudo nano /usr/local/bin/ddns-update.sh
```

```bash
#!/bin/bash
# ddns-update.sh — Update Cloudflare DNS A record for m2vpn.yourdomain.com
# Runs via systemd timer every 5 minutes. Logs to journalctl -u ddns-update.
# Required for field deployment where public IP changes (cellular, Starlink, etc.)

CF_TOKEN="YOUR_CLOUDFLARE_API_TOKEN"
ZONE_ID="YOUR_ZONE_ID"
RECORD_ID="YOUR_RECORD_ID"
HOSTNAME="m2vpn.yourdomain.com"

# Get current public IP from multiple sources (fallback chain)
PUBLIC_IP=$(curl -s --max-time 10 https://ifconfig.me || curl -s --max-time 10 https://api.ipify.org || curl -s --max-time 10 https://icanhazip.com)

if [ -z "$PUBLIC_IP" ]; then
    echo "ERROR: Could not determine public IP"
    exit 1
fi

# Get current DNS record value from Cloudflare
DNS_IP=$(curl -s --max-time 10 -H "Authorization: Bearer $CF_TOKEN" "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['content'])")

if [ "$PUBLIC_IP" = "$DNS_IP" ]; then
    echo "OK: IP unchanged ($PUBLIC_IP)"
    exit 0
fi

# Update the A record
RESULT=$(curl -s --max-time 10 -X PUT -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" -d "{\"type\":\"A\",\"name\":\"$HOSTNAME\",\"content\":\"$PUBLIC_IP\",\"ttl\":300,\"proxied\":false}" "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID")

SUCCESS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])")

if [ "$SUCCESS" = "True" ]; then
    echo "UPDATED: $DNS_IP -> $PUBLIC_IP"
else
    echo "ERROR: Update failed — $RESULT"
    exit 1
fi
```

> **Finding your Zone ID and Record ID:** Run these from Pi #2 with your Cloudflare API token:
> - Zone ID: `curl -s -H "Authorization: Bearer $TOKEN" "https://api.cloudflare.com/client/v4/zones?name=yourdomain.com" | python3 -m json.tool | grep '"id"' | head -1`
> - Record ID: `curl -s -H "Authorization: Bearer $TOKEN" "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=m2vpn.yourdomain.com" | python3 -m json.tool | grep -E '"id"|"type"|"content"'`

```bash
sudo chmod +x /usr/local/bin/ddns-update.sh
```

Test it manually:

```bash
sudo /usr/local/bin/ddns-update.sh
```

Expected: `OK: IP unchanged (your.current.ip)` or `UPDATED: old.ip -> new.ip`

#### Step 2 — Create Systemd Service and Timer

**[SSH — Pi #2]**

```bash
sudo nano /etc/systemd/system/ddns-update.service
```

```ini
# ddns-update.service — One-shot Cloudflare DNS update for m2vpn.yourdomain.com
# Triggered by ddns-update.timer every 5 minutes.
# Logs: journalctl -u ddns-update

[Unit]
Description=Cloudflare DDNS Update for Headscale
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ddns-update.sh
```

```bash
sudo nano /etc/systemd/system/ddns-update.timer
```

```ini
# ddns-update.timer — Run DDNS check every 5 minutes
# Ensures m2vpn.yourdomain.com stays pointed at current public IP
# Critical for field deployment on cellular/Starlink where IP changes frequently

[Unit]
Description=DDNS Update Timer for Headscale

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
AccuracySec=30s

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable ddns-update.timer
```

```bash
sudo systemctl start ddns-update.timer
```

Verify: `sudo systemctl list-timers ddns-update.timer` — should show NEXT fire time ~5 minutes out.

#### Monitoring

```bash
# Watch live updates
journalctl -u ddns-update -f

# Check recent history
journalctl -u ddns-update --since "1 hour ago"
```

---

### 5.4 Configure Reticulum

```bash
mkdir -p /opt/tactical-node/data/reticulum
nano /opt/tactical-node/data/reticulum/config
```

```ini
[reticulum]
  enable_transport = True
  share_instance = True
  shared_instance_port = 37428
  instance_control_port = 37429
  panic_on_interface_error = No

[interfaces]

  [[Default Interface]]
    type = AutoInterface
    enabled = yes

  [[TCP Server]]
    type = TCPServerInterface
    enabled = yes
    listen_ip = 0.0.0.0
    listen_port = 4242

  # Uncomment after LoRa radio is attached (Phase 6)
  #[[RNode LoRa]]
  #  type = RNodeInterface
  #  enabled = no
  #  port = /dev/ttyUSB0
  #  frequency = 915000000
  #  bandwidth = 125000
  #  spreadingfactor = 8
  #  codingrate = 5
  #  txpower = 17
```

---

### 5.5 Pull Docker Images

Pull images one at a time before starting the stack to avoid timeout failures on WiFi:

```bash
docker pull eclipse-mosquitto:2.0.22
docker pull ghcr.io/sethforprivacy/simple-monerod:v0.18.4.5
docker pull python:3.12.12-slim-bookworm
docker pull headscale/headscale:0.28.0
```

> **Note:** OpenTAK Server runs natively under systemd — no Docker pull needed. Install via the OTS Pi installer in Phase 5B.

---

### 5.6 Start Node #2 Stack

```bash
cd /opt/tactical-node

# Start core Docker services (OTS runs under systemd separately — see Phase 5B)
docker compose up -d monerod reticulum nomadnet mosquitto

# Monitor startup
docker compose logs -f monerod
# Monero will begin syncing from where the LMDB left off (should be current)
# Look for: "SYNCHRONIZED OK" in the logs

docker compose ps
```

> **Reticulum LoRa interface:** The RNode interface in `data/reticulum/config` is **commented out** at this stage — the LEFT Heltec V3 radio hasn't been configured yet. Reticulum will start and run over TCP/AutoInterface only. The LoRa interface is enabled in Phase 6 after the RNode firmware is flashed and confirmed. This is expected behavior.

**Verify Monero sync status:**
```bash
# Check sync status via RPC (localhost only after security fix)
curl -s http://127.0.0.1:18089/get_info | python3 -m json.tool | grep -E "height|status|synchronized"
# Required output:
#   "status": "OK"
#   "synchronized": true
#   "height": <current block height>

# Cross-check current block height at: xmrchain.net
# The height reported by your node should be within 1-2 blocks of the chain tip
# A gap of >100 blocks means your LMDB pre-sync was incomplete — let it catch up
```

> **Monero RPC is localhost-only** (security hardening applied above). The Quick Reference table shows port 18089 — that port is only accessible from the Pi itself or via Tailscale VPN. LAN WiFi clients cannot reach it directly. This is intentional.

**Verify OpenTAK Server:**
```bash
# OTS runs under systemd (installed in Phase 5B)
systemctl is-active opentakserver
# Should return: active

# Check OTS logs
journalctl -u opentakserver --no-pager -n 20

# ATAK Android connection:
# Server IP:   192.168.8.20
# TCP CoT:     port 8088
# SSL CoT:     port 8089 (encrypted — preferred)
# Cert enroll: port 8446

# Web UI: http://192.168.8.20:8080 — live Leaflet map with connected clients
# HTTPS UI: https://192.168.8.20:8443
```

---

### 5B. OpenTAK Server Native Install

OpenTAK Server runs natively under systemd — not Docker. The OTS Docker ARM64 image is alpha; the native Pi installer is production-ready.

**[SSH — Pi #2 tactical-lan]**

**Step 1 — Run the OTS installer:**
```bash
curl -fsSL https://opentakserver.io/install.sh | sudo bash
```

> The installer handles Python 3.10+, RabbitMQ, nginx, and all dependencies. The default admin account is `administrator` / `password` — you will change this in Step 10.

**Step 2 — Fix nginx port 443 conflict with Headscale:**

OTS installer may bind nginx to port 443. Headscale already uses 443 for the VPN control plane. Edit the OTS nginx config immediately after install:

```bash
sudo nano /etc/nginx/sites-available/ots_http
```

Remove or comment out any `listen 443` block in the OTS nginx config. OTS web UI should only listen on 8080 (HTTP) and 8443 (HTTPS). Save and restart nginx:

```bash
sudo nginx -t && sudo systemctl restart nginx
```

**Step 3 — Set RabbitMQ memory watermark:**

RabbitMQ defaults to 40% of system RAM. On a Pi with Monero's 4GB limit, constrain RabbitMQ to 256MB:

```bash
sudo rabbitmqctl set_vm_memory_high_watermark absolute 256MB
```

To make persistent across restarts:
```bash
echo 'vm_memory_high_watermark.absolute = 256MB' | sudo tee -a /etc/rabbitmq/rabbitmq.conf
```

> **RabbitMQ password bug (OTS v1.7.9):** The RabbitMQ credentials MUST remain `guest/guest`. OTS hardcodes the default RabbitMQ credentials in its internal SocketIO AMQP connection URL. Changing the RabbitMQ password will break OTS message queuing silently. Do not change RabbitMQ credentials until this is fixed upstream.

**Step 3a — Disable RabbitMQ HTTP auth backend plugin:**

The `rabbitmq_auth_backend_http` plugin causes `ACCESS_REFUSED` errors with the default guest credentials. Disable it:

```bash
sudo rabbitmq-plugins disable rabbitmq_auth_backend_http
```

```bash
sudo systemctl restart rabbitmq-server
```

**Step 3b — Add nginx no-cache header for kiosk map page:**

The OTS web map served at `/kiosk-map.html` can show stale data if the browser caches aggressively. Add a no-cache directive to the OTS nginx config:

```bash
sudo nano /etc/nginx/sites-available/ots_http
```

Inside the `server` block listening on port 8080, add:

```nginx
    # Prevent browser caching of kiosk map — always fetch fresh CoT data
    location = /kiosk-map.html {
        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0";
        add_header Pragma "no-cache";
    }
```

```bash
sudo nginx -t && sudo systemctl restart nginx
```

**Step 4 — Add udev rules for stable USB symlinks:**

`/dev/ttyUSB0` and `/dev/ttyUSB1` can swap on reboot. Create stable symlinks:

```bash
sudo nano /etc/udev/rules.d/99-lora-radios.rules
```

```
# Heltec V3 LoRa radios — stable symlinks by USB controller path
# LEFT radio (RNode/Reticulum) — USB controller 0 (upper USB port)
SUBSYSTEM=="tty", ENV{ID_PATH}=="platform-xhci-hcd.0-usb-0:2:1.0", SYMLINK+="rnode"
# RIGHT radio (Meshtastic) — USB controller 1 (lower USB port)
SUBSYSTEM=="tty", ENV{ID_PATH}=="platform-xhci-hcd.1-usb-0:2:1.0", SYMLINK+="meshtastic"
```

> Both Heltec V3 boards use CP2102 USB-UART bridges with identical serial `0001`. The `ID_PATH` matches by physical USB port instead. Find yours with `udevadm info /dev/ttyUSB0 | grep ID_PATH`.

Reload:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**Step 5 — Configure OTS Meshtastic serial gateway:**

In the OTS web UI (`http://192.168.8.20:8080`) → Settings → Meshtastic:
- Enable Meshtastic gateway
- Serial port: `/dev/meshtastic` (stable symlink from Step 4)
- Baud rate: 115200

**Step 6 — Mumble voice server setup:**

```bash
sudo apt install -y mumble-server
```

```bash
sudo dpkg-reconfigure mumble-server
```

Set the Mumble SuperUser password when prompted. ATAK users install the Mumla app (Play Store) for push-to-talk voice on this server.

**Step 7 — Offline maps (PMTiles for kiosk):**

The kiosk location picker uses Protomaps vector tiles rendered in-browser via protomaps-leaflet. This provides a fully offline dark-themed map for FL at zoom levels 0-14.

Install the `pmtiles` CLI on any machine with internet access:

```bash
curl -sL "https://github.com/protomaps/go-pmtiles/releases/latest/download/go-pmtiles_Linux_arm64.tar.gz" | tar xz pmtiles
```

Extract FL tiles from the Protomaps daily build (streams only needed tiles, ~604MB):

```bash
./pmtiles extract "https://build.protomaps.com/$(date +%Y%m%d).pmtiles" /mnt/nvme/tiles/florida.pmtiles --bbox=-87.64,24.40,-79.97,31.00 --maxzoom=14
```

> If today's build isn't available yet, try yesterday's date. The extract command streams tile data directly from the remote file — it does NOT download the full ~130GB planet file. FL z0-14 produces ~604MB covering 159,760 tiles.

Create the tiles directory and set permissions:

```bash
sudo mkdir -p /mnt/nvme/tiles
```

```bash
sudo chown ps:ps /mnt/nvme/tiles
```

Deploy kiosk JS/CSS assets (Leaflet + protomaps-leaflet, self-hosted for offline use):

```bash
sudo mkdir -p /var/www/html/opentakserver/kiosk-assets/images
```

```bash
curl -sL "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" | sudo tee /var/www/html/opentakserver/kiosk-assets/leaflet.js > /dev/null
```

```bash
curl -sL "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" | sudo tee /var/www/html/opentakserver/kiosk-assets/leaflet.css > /dev/null
```

```bash
curl -sL "https://unpkg.com/protomaps-leaflet@5.0.0/dist/protomaps-leaflet.js" | sudo tee /var/www/html/opentakserver/kiosk-assets/protomaps-leaflet.js > /dev/null
```

```bash
for f in marker-icon.png marker-icon-2x.png marker-shadow.png; do curl -sL "https://unpkg.com/leaflet@1.9.4/dist/images/$f" | sudo tee "/var/www/html/opentakserver/kiosk-assets/images/$f" > /dev/null; done
```

Add nginx location blocks for tile serving. Edit `/etc/nginx/sites-available/ots_http` and add inside the `server` block, before the `try_files` line:

```nginx
    # Serve offline PMTiles from NVMe — byte-range support required
    location /tiles/ {
        alias /mnt/nvme/tiles/;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Headers Range;
        add_header Access-Control-Expose-Headers Content-Length,Content-Range;
        add_header Cache-Control "public, max-age=604800";
        types {
            application/octet-stream pmtiles;
        }
    }

    # Serve kiosk JS/CSS assets with long cache
    location /kiosk-assets/ {
        add_header Cache-Control "public, max-age=604800";
    }
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

> The PMTiles file contains Protomaps Basemap v4 vector tiles (MVT format). protomaps-leaflet renders them in the browser on a Canvas layer. The "dark" flavor matches the kiosk theme. If the PMTiles file is missing, the location picker falls back to online OSM raster tiles.

**Step 8 — DTED2 terrain data (ATAK devices):**

DTED2 provides 30m elevation data for terrain analysis, line-of-sight calculations, and slope display in ATAK.

**Method A — DTED.org QR provisioning (preferred, requires internet):**

When DTED.org adds FL coverage (check `https://fl.dted.org`), users scan a QR code in ATAK and the app downloads FL DTED2 automatically. No manual file management needed. As of March 2026, only CA and NC are available — check `https://dted.readthedocs.io/en/latest/states/` for updates.

**Method B — OTS data package (offline fallback):**

Build the FL DTED2 data package from Copernicus 30m DEM (public, no account needed):

```bash
sudo apt install -y gdal-bin
```

```bash
sudo mkdir -p /mnt/nvme/dted-build/geotiff /mnt/nvme/dted-build/DTED && sudo chown -R ps:ps /mnt/nvme/dted-build
```

Download Copernicus 30m tiles for FL (lat 24-31N, lon 79-88W):

```bash
for lat in $(seq 24 30); do for lon in $(seq 79 87); do latpad=$(printf '%02d' $lat); lonpad=$(printf '%03d' $lon); fname="Copernicus_DSM_COG_10_N${latpad}_00_W${lonpad}_00_DEM"; curl -sf "https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/${fname}/${fname}.tif" -o "/mnt/nvme/dted-build/geotiff/N${latpad}W${lonpad}.tif" && echo "  OK: N${latpad}W${lonpad}" || echo "  Skip: N${latpad}W${lonpad} (ocean)"; done; done
```

Convert GeoTIFF to DTED2:

```bash
for tif in /mnt/nvme/dted-build/geotiff/*.tif; do base=$(basename "$tif" .tif); lat=${base:1:2}; lon=${base:4:3}; mkdir -p "/mnt/nvme/dted-build/DTED/w${lon}"; gdal_translate -of DTED -q "$tif" "/mnt/nvme/dted-build/DTED/w${lon}/n${lat}.dt2"; done
```

Build the ATAK data package ZIP with manifest:

```bash
mkdir -p /mnt/nvme/dted-build/package/MANIFEST && cp -r /mnt/nvme/dted-build/DTED /mnt/nvme/dted-build/package/
```

Create `MANIFEST/manifest.xml` inside the package directory:

```xml
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="fl-dted2-offline-pkg" />
    <Parameter name="name" value="FL_DTED2" />
    <Parameter name="onReceiveImport" value="true" />
    <Parameter name="onReceiveDelete" value="false" />
  </Configuration>
  <Contents>
    <!-- One Content entry per .dt2 file with contentType="DTED" -->
  </Contents>
</MissionPackageManifest>
```

> Generate the Content entries: `find /mnt/nvme/dted-build/package/DTED -name '*.dt2' | sort | while read f; do rel=${f#/mnt/nvme/dted-build/package/}; echo "    <Content ignore=\"false\" zipEntry=\"$rel\"><Parameter name=\"contentType\" value=\"DTED\" /></Content>"; done`

ZIP the package (store-only, DTED is already compressed):

```bash
cd /mnt/nvme/dted-build/package && zip -r -0 /mnt/nvme/dted-build/FL_DTED2.zip MANIFEST/ DTED/
```

Upload to OTS via the web UI: **Admin → Data Packages → Upload**, select `FL_DTED2.zip`. Enable the **Connection** auto-install switch so EUDs receive DTED2 on first server connection.

> **nginx upload limit:** The default `client_max_body_size` is 100MB. For the ~1.5GB DTED package, increase to 2G in both `/etc/nginx/sites-available/ots_http` and `ots_https`, then `sudo nginx -t && sudo systemctl reload nginx`.

> **How it works on the EUD:** With `onReceiveImport=true` and the Connection switch enabled, ATAK downloads and auto-imports the DTED files to `/sdcard/atak/DTED/` when the device connects to the server. No user action needed — elevation data appears in the Elevation Manager automatically.

**Manual pre-load (USB fallback):** Copy the `DTED/` folder directly to `/sdcard/atak/DTED/` via USB cable or ADB. ATAK loads elevation data at launch.

**Step 9 — Change the default admin password:**

The installer creates a default `administrator` account with password `password`. Change it immediately.

In a browser, open `http://192.168.8.20:8080` and log in with `administrator` / `password`. Navigate to **Admin → Users**, click the administrator row, and change the password. Save and verify you can log in with the new password.

> **Important:** The password change is in Admin → Users, NOT in Profile. Profile does not expose a password change option. Store the new password in your secrets worksheet (M2_SECRETS.md).

**Step 10 — Verify OTS is running:**

```bash
systemctl is-active opentakserver
```

```bash
curl -s http://127.0.0.1:8080/ | head -5
```

Open `http://192.168.8.20:8080` in a browser — the OTS web UI should display a live Leaflet map.

**Step 11 — Create static node marker:**

The OTS web map is empty when no ATAK clients are connected. Place a permanent marker at the node's deployment location so the kiosk map always shows context.

```bash
curl -s -X POST http://127.0.0.1:8080/api/markers -H 'Content-Type: application/json' -d '{"uid":"1cec9ca6-0b35-415f-9fd6-5aaf43094c79","name":"Community Node","latitude":YOUR_LAT,"longitude":YOUR_LON,"type":"a-f-G-E-S"}'
```

> Replace `YOUR_LAT` and `YOUR_LON` with the deployment site coordinates (decimal degrees). Type `a-f-G-E-S` = friendly ground equipment, sensor. The kiosk location picker also uses this UID — setting the marker from the kiosk map updates the same point. The marker persists across OTS restarts.

---

## 8. Phase 6: LoRa Radio Setup

### 6.0 Why Two LoRa Radios?

This build uses two separate LoRa radios because Reticulum and Meshtastic run **mutually exclusive firmware** — a single device cannot run both simultaneously. Each radio is permanently dedicated to one protocol.

| | Heltec V3 — LEFT (RNode) | Heltec V3 — RIGHT (Meshtastic) |
|---|---|---|
| **Hardware** | Heltec WiFi LoRa 32 V3 915MHz | Heltec WiFi LoRa 32 V3 915MHz (identical) |
| **Panel position** | **LEFT** — ANT 1 | **RIGHT** — ANT 2 |
| **Firmware** | RNode (Mark Qvist / unsigned.io) | Meshtastic |
| **Protocol** | Reticulum encrypted mesh transport | Meshtastic consumer LoRa mesh |
| **Audience** | Operators, technical users | Anyone with a $20 device or phone app |
| **Security** | Cryptographic by design — every packet authenticated and encrypted | Basic; user-managed channels |
| **Onboarding** | Requires Reticulum client config | Phone app, 2 minutes |
| **Pi #2 USB port** | USB 2.0 port 1 → `/dev/ttyUSB0` | USB 2.0 port 2 → `/dev/ttyUSB1` |

**The design intent:** one radio faces **inward** (Reticulum — secure, operator-controlled backbone), one faces **outward** (Meshtastic — accessible to anyone in the community with a cheap handheld). Together they let you maintain a private encrypted mesh between node operators while simultaneously bridging non-technical community members into the network via the Meshtastic ecosystem.

**How repeating works on both radios:**

Both radios act as dumb repeaters — no manual routing config is required on either.

- **RNode (LEFT) — Reticulum:** The RNode is purely a radio modem. It receives every LoRa packet in range and passes it to `rnsd` (the Reticulum daemon running in Docker). Reticulum handles all routing decisions automatically. Your node runs in `Full` mode (visible in `rnstatus`) which means it receives, rebroadcasts, and forwards all packets toward their destination using Reticulum's built-in mesh routing protocol. A user within LoRa range simply runs a Reticulum client — their packets hit your RNode, get picked up by `rnsd`, and are forwarded across the mesh automatically. No configuration needed on the RNode itself beyond what was set during flash.

- **Meshtastic (RIGHT) — REPEATER mode:** Set to `REPEATER` role with `ALL_SKIP_DECODING` rebroadcast mode. Every Meshtastic packet received is rebroadcast regardless of channel encryption keys. Any Meshtastic user within LoRa range is automatically served — the node extends their range by relaying their messages to other mesh nodes.

Both radios are true infrastructure repeaters — connect and go, no user setup required beyond being in range.

Dropping one is valid if you simplify the mission:
- **Drop RIGHT Heltec V3** if your community won't have Meshtastic devices — saves ~$20 and one USB port
- **Drop LEFT Heltec V3** if you only need consumer mesh and don't need encrypted Reticulum transport (also removes NomadNet BBS capability)

---

### 6.1 Flash RNode Firmware to Heltec V3 (LEFT Board)

The LEFT Heltec V3 must be flashed with RNode firmware (by Mark Qvist) to work with Reticulum. Label this board "RNode" before proceeding to avoid mixing up the two identical boards.

**On your laptop (not the Pi):**

```bash
# Install rnodeconf (now bundled inside the rns package — do NOT use standalone rnodeconf package)
pip install rns

# Connect the LEFT Heltec V3 to your laptop via USB-C
# It will appear as a serial device

# Find the port:
# Linux/Mac: ls /dev/ttyUSB* or ls /dev/ttyACM*
# Windows: check Device Manager → Ports (COM & LPT)

# Auto-install RNode firmware (interactive)
rnodeconf --autoinstall

# Select: Heltec V3 when prompted
# Select: 915 MHz (US band) or 868 MHz (EU) depending on your region
# Follow prompts to complete flash
```

**Verify flash:**
```bash
rnodeconf --info /dev/ttyUSB0    # adjust port as needed
# Should show: firmware version, frequency, and RNode status
```

**Set display timeout (run after flashing, before plugging into rack):**
```bash
# rnodeconf moved into the rns package — use rns, not the standalone rnodeconf package
pip install rns
rnodeconf /dev/ttyUSB0 -t 60
# Sets OLED sleep timeout to 60 seconds — written to EEPROM, survives power cycles
# No reboot required — takes effect immediately
```

> **Signature warning:** `rnodeconf` will warn that the device signature cannot be validated
> against this machine's key. This is expected if you flashed on a different machine.
> It is your device — proceed safely. The timeout is still written correctly.

---

### 6.2 Flash Meshtastic Firmware to Heltec V3 (RIGHT Board)

The RIGHT Heltec V3 runs Meshtastic — a separate LoRa mesh firmware for community-facing device compatibility. This is a dedicated outward-facing radio; it is not a backup for the RNode. Label this board "Meshtastic" before proceeding.

1. Flash via web flasher: `flasher.meshtastic.org` (Chrome/Edge required — no download needed)
2. Connect Heltec to your laptop via USB-C
3. Select **Heltec WiFi LoRa 32 V3** as target device
4. Enable **Full Erase** before flashing — clears residual config from previous firmware
5. Click Flash
6. Configure via Meshtastic app (Bluetooth) or web client at `client.meshtastic.org` (USB Serial):
   - **Region:** US (915 MHz)
   - **Role:** `REPEATER` — ⚠️ do NOT use `Router` or `Router_Client`
     - `Router` mode hardcodes power saving ON (by design, cannot be disabled) — causes boot loop on USB-only Heltec V3
     - `Router_Client` is deprecated and removed in firmware 2.3.15+
     - `REPEATER` is the correct role for a fixed USB-powered infrastructure node — no forced sleep
   - **Rebroadcast Mode:** `ALL_SKIP_DECODING`
   - **Power → ADC Multiplier Override:** `4.0` (max allowed; default 4.9 causes brownout on USB-only power)
   - **Power → Power Saving:** OFF
   - **Display → Screen Timeout:** `60` seconds — ⚠️ do NOT set to 0 (triggers separate freeze bug)
   - Set node name and short name (4 chars max)

> **OLED screen:** Goes dark after 60 seconds — normal burn-in protection. Device is running.
> Confirm via Meshtastic app (**Connected** status) not by OLED state.

> **Config via web client:** If Bluetooth pairing fails, connect via USB Serial at `client.meshtastic.org`
> in Chrome/Edge. Both Serial and Bluetooth work interchangeably.

> **Reference bugs (all fixed in 2.7.x but avoid triggering):**
> - GitHub #3391 — Router mode boot loop (RTC GPIO, ESP32-S3)
> - GitHub #8017 — OLED timeout=0 + Router mode freeze
> - GitHub #5053 — USB-only brownout on wake (ADC multiplier fix above)

---

### 6.3 Antenna Panel and Radio Connections

#### Custom 1U LoRa Panel with OLED Windows (U8 Front) + 120mm Fan (U8 Rear)

Both LoRa boards mount directly to a custom 3D-printed 1U panel at U8 (front rails) — antennas at the top of the rack for best RF propagation, maximum distance from power cables at U1-U2. The 120mm exhaust fan shares U8 on the rear rails. The panel integrates:
- **2× rectangular OLED cutout windows** — one per board, exposing each 0.96" OLED screen through the panel face for status visibility without opening the rack
- **2× SMA female bulkhead feedthroughs** — antennas mount cleanly on the outside of the rack
- **2× M2 standoff mounting positions** — boards mount on M2 × 8mm nylon standoffs on the panel's interior face

**Signal chain (per radio):**
```
Radio board (U.FL / IPEX connector on PCB)
    → U.FL-to-SMA-male pigtail cable (6", low loss)
    → SMA female bulkhead (interior side of U8 panel)
    → SMA female bulkhead (exterior side of U8 panel)
    → 915 MHz antenna (SMA male, screws on outside of rack)
```

> **Antenna connector note:** Both Heltec V3 boards have **IPEX (U.FL) ONLY** — no SMA connector on the board. Both use U.FL-to-SMA pigtails (BOM item 28) for panel connection. This eliminates the need for SMA male-to-male jumper cables.

**Parts for custom LoRa panel (all in BOM):**
| Part | Qty | BOM Item | Notes |
|------|-----|----------|-------|
| Custom 1U LoRa Panel (3D print) | 1 | #26 | Black PETG; ~1h print |
| SMA female panel-mount bulkhead connector | 2 | #27 | Standard SMA female-female feedthrough with nut |
| U.FL-to-SMA-male pigtail cable, 6" | 2 | #28 | IPEX MHF4 to SMA male; connects board → bulkhead directly |
| M2 × 8mm nylon standoffs + M2 screws | 8+8 | #28a | 4 standoffs per board; nylon prevents shorts |
| 915 MHz antenna, SMA male, 2–5 dBi | 2 | #19 | Screws onto panel bulkhead exterior |

#### Panel Assembly (do on a workbench before rack installation)

1. Install 2× SMA female bulkhead connectors into the panel's SMA cutout holes, secure with nuts from the interior side
2. Mount Heltec V3 (RNode) on the **LEFT** M2 standoff positions — align OLED behind the left window cutout; secure with 4× M2 nylon standoffs + screws
3. Mount Heltec V3 (Meshtastic) on the **RIGHT** M2 standoff positions — align OLED behind the right window cutout; secure with 4× M2 nylon standoffs + screws
4. Connect U.FL pigtail from LEFT Heltec V3 U.FL connector → left SMA bulkhead interior (ANT 1 — Reticulum)
5. Connect U.FL pigtail from RIGHT Heltec V3 U.FL connector → right SMA bulkhead interior (ANT 2 — Meshtastic)
6. Screw 915 MHz antennas onto the external SMA bulkheads — **verify SMA male (center pin), not RP-SMA**
7. Label each antenna position ("RNode / Reticulum" and "Meshtastic") with a label maker or tape
8. Install completed panel assembly into U8 front rails (top of rack)
9. Connect LEFT Heltec V3 (RNode) → Pi #2 USB 2.0 port 1 via 3ft USB-C cable (U8→U4, route along right side of rack)
10. Connect RIGHT Heltec V3 (Meshtastic) → Pi #2 USB 2.0 port 2 via 3ft USB-C cable (U8→U4, route along right side of rack)

#### RF Coexistence and Channel Separation

**GL.iNet WiFi antennas — internal, no modification needed:** The Slate AX uses internal PCB antennas for both its 2.4 GHz and 5 GHz WiFi radios. The open-frame RackMate T1 rack has no shielding, so the internal antennas radiate freely through the rack openings. Do not attempt to add external SMA connections to the router — it voids the warranty, risks PCB damage, and provides no meaningful benefit in a rack with open sides.

**WiFi vs. LoRa — no RF conflict:** The 2.4 GHz and 5 GHz WiFi bands have zero frequency overlap with the 902–928 MHz LoRa band. The external LoRa antennas on the custom LoRa panel and the router's internal WiFi antennas can be inches apart with no interference in either direction. LoRa's chirp spread-spectrum modulation adds ~19 dB of noise immunity on top of the band separation.

**RNode vs. Meshtastic — same band, manage with channel separation:** Both LoRa radios operate in the **902–928 MHz US915 band**. The stock firmware defaults are already on different frequencies — no configuration change needed if you use default channel settings on both:

| Radio | Protocol | Default Operating Frequency |
|---|---|---|
| Heltec V3 LEFT (RNode) | Reticulum | ~915.0 MHz (configure explicitly in Reticulum config) |
| Heltec V3 RIGHT (Meshtastic) | Meshtastic | ~906.875 MHz (LongFast default, US region) |

The ~8 MHz separation between these defaults is sufficient to prevent receiver desensitization during simultaneous transmissions. LoRa's inherently low duty cycle (<1% TX time) makes simultaneous TX events rare regardless. If you change either radio's channel or frequency from defaults, maintain at least 5 MHz separation between the two.

**Identify serial ports on Pi #2:**
```bash
ls /dev/ttyUSB*
# LEFT Heltec (RNode): /dev/ttyUSB0
# RIGHT Heltec (Meshtastic): /dev/ttyUSB1
# (order may vary — check with: udevadm info /dev/ttyUSBx)
```

**Enable RNode interface in Reticulum config:**
```bash
nano /opt/tactical-node/data/reticulum/config
```

Uncomment the `[[RNode LoRa]]` section and change `enabled = no` to `enabled = yes`.

**Restart Reticulum:**
```bash
cd /opt/tactical-node
docker compose up -d reticulum
```

Wait ~60 seconds for pip install to complete, then verify:

```bash
# Live interface status — confirms RNode is up, noise floor, airtime, temp
docker exec tactical-node-reticulum-1 rnstatus

# Expected output includes:
#   RNodeInterface[RNode LoRa]
#     Status    : Up
#     Rate      : 3.12 kbps
#     Noise Fl. : -90 dBm, no interference

# Docker logs (verbose output from rnsd -v)
docker compose logs --tail=50 reticulum
```

> **Note:** `rnsd` buffers verbose output — Docker logs may show pip output only for the first minute.
> Use `rnstatus` as the definitive check. If RNode shows `Status: Up` you're good.

---

### 4.6 Conduit Admin Room Reference

The admin room is your primary server management interface. It is created automatically when the first admin user registers. The `@conduit` bot must be a member of the room for commands to work.

**Command syntax:**
```
@conduit:yourdomain.com: <command>
```

**Most commonly used commands:**

| Command | Usage |
|---|---|
| `help` | List all available commands |
| `create-user <username> <password>` | Create a new user account |
| `reset-password <@user:domain> <newpassword>` | Reset a user's password |
| `deactivate-user <@user:domain>` | Permanently deactivate a user |
| `list-local-users` | Show all registered users on this server |
| `list-rooms` | Show all rooms the server knows about |
| `allow-registration true\|false` | Temporarily open/close registration (**does NOT persist across restarts** — see note below) |
| `show-config` | Print current Conduit configuration values |
| `memory-usage` | Print database memory usage statistics |

> **Registration persistence:** Enabling registration via the admin room command (`allow-registration true`) does NOT persist across Conduit restarts — it resets to the value in `conduit.toml`. To permanently enable open registration, edit `/opt/community-node/config/conduit/conduit.toml` directly: set `allow_registration = true`, then restart Conduit: `docker compose restart conduit`.

> **Admin room encryption:** Keep the admin room **unencrypted**. The Conduit bot cannot participate in E2EE rooms. Encrypting the admin room will prevent it from receiving or responding to commands, locking you out of server management.
>
> **Room structure recommendation:**
> - Encrypted: `#general`, `#ops`, and any member chat rooms — private, no bots
> - Unencrypted: `#node-status` (health bot output), `#announcements`, admin room — bot-accessible, read-only for members

---

## 9. Phase 7: Integration Testing

### 7.1 Service Health Checklist

Run from a laptop connected to the `CommunityNode` WiFi.

```bash
# Node #1 — Communications
curl -s http://192.168.8.10/_matrix/client/versions && echo "✓ Matrix (Conduit)"
curl -s http://192.168.8.10:8080/ | grep -q "Element" && echo "✓ Element Web"
curl -s http://192.168.8.10:7070/ && echo "✓ I2P console"

# Node #2 — Tactical
curl -s http://192.168.8.20:8080/ | grep -q "OpenTAK" && echo "✓ OpenTAK Server Web UI"
```

Monero RPC is bound to `127.0.0.1` on Pi #2 — it is not reachable from a LAN laptop. Verify from Pi #2 directly:

**[SSH — Pi #2 tactical-lan]**

```bash
# Monero RPC is accessible from Pi #2 only (bound to 127.0.0.1)
curl -s http://127.0.0.1:18089/get_info | python3 -m json.tool | grep status && echo "✓ Monero node"
```

---

### 7.2 Matrix Federation Test

> **"Failed to load service worker" warning:** This appears when accessing Element Web over plain HTTP (`http://192.168.8.10:8080`). Service workers require HTTPS and will not load on the local LAN address. **This is non-critical — dismiss it.** Text messaging works fully. Authenticated media (images, file attachments in encrypted rooms) may fail to display over the LAN address. For full functionality including media, use the Cloudflare Tunnel URL (`https://communitynode.yourdomain.com`) or the Tor hidden service, both of which satisfy the HTTPS requirement.
>
> **First login — "Reset Identity" prompt:** On a fresh Conduit server, Element Web has no existing cross-signing keys to verify against. It will show a "Can't confirm" button and then a "Reset Identity" pop-up. This is normal and expected — there is no prior identity to lose. Proceed through the reset, and when prompted save the **Security Key or Recovery Phrase** somewhere secure (password manager or printed copy stored with the rack). You will need it to verify future logins from new devices.
>
> **Browser compatibility:** Element Web requires a modern Chromium-based or Firefox browser.
> - ✓ Chrome, Edge, Brave — fully supported
> - ✓ Firefox — fully supported
> - ⚠️ Safari — partial support; some encryption and file-sharing features may not work
> - ✗ Internet Explorer — not supported
>
> **Run this test on CommunityNode WiFi** — do not disconnect to clearnet for this step. Local WiFi tests the full local stack (Conduit → Nginx → Element Web) without Cloudflare as a variable. Clearnet access via `m2-matrix.yourdomain.com` is verified separately in Phase 7.6.

```
# Stay on CommunityNode WiFi — open in browser:
http://192.168.8.10:8080

# Log in with the admin account created in Phase 4
# Create a test room
# Send a message — verify it persists after refreshing

# Also verify the community info page loads:
http://192.168.8.10:8081
```

---

### 7.3 ATAK Client Connection Test

1. Install ATAK on an Android device
2. Connect device to `CommunityNode` WiFi
3. In ATAK: Settings → Network → Connect to server
   - Server: `192.168.8.20`
   - Port: `8088`
   - Protocol: TCP
4. Verify connection via OTS web UI: open `http://192.168.8.20:8080` in a browser
   - The live Leaflet map should show your device's position marker
   - OTS web UI provides real-time map, MIL-STD-2525C symbology, and certificate management
5. **Expected result:** Your device appears on both the ATAK map and the OTS web UI map. For SSL connections, use port 8089 and enroll certificates via port 8446.

---

### 7.4 Monero Sync Verification

**[SSH — Pi #2 tactical-lan]**

```bash
# Monero RPC is accessible from Pi #2 only (bound to 127.0.0.1 — not LAN-accessible)
curl -s http://127.0.0.1:18089/get_info | python3 -m json.tool
# Key fields:
# "status": "OK"
# "synchronized": true
# "height": should match current Monero blockchain height
#   (check current height at: xmrchain.net)
```

---

### 7.5 LoRa Range Test

Test both radio paths independently. You need two people or a second phone left at the rack.

#### Meshtastic (RIGHT radio)

**At the rack — confirm the Meshtastic node is visible:**

1. Open the Meshtastic app on your phone (Bluetooth paired to a separate handheld Meshtastic device, OR connected to the rack's RIGHT Heltec V3 via USB serial)
2. Verify the rack node appears in the node list with a recent "last heard" timestamp

**Walk-away test:**

1. Take a handheld Meshtastic device (or phone with Meshtastic app + paired radio) and walk away from the rack
2. At each distance checkpoint, send a text message via Meshtastic and confirm receipt on the rack node
3. Checkpoints: 100m, 250m, 500m, 1km

| Environment | Expected Range | Notes |
|---|---|---|
| Open terrain (field, parking lot) | 1–5 km | Line-of-sight dependent |
| Suburban (houses, light trees) | 500m–2 km | Signal degrades with obstructions |
| Urban / indoor | 200–500m | Worst case; walls and metal attenuate 915 MHz |

**Verify on OTS web map (if Meshtastic gateway is configured):**

```
http://192.168.8.20:8080
```

The walking device should appear as a position marker on the OTS Leaflet map if the OTS Meshtastic gateway bridge is active. If it does not appear, the gateway serial connection may need restarting:

```bash
# SSH into Pi #2
systemctl restart opentakserver
```

#### Reticulum (LEFT radio — RNode)

Reticulum range testing requires a second RNode device or a device running `rnsd` with an RNode interface.

**From Pi #2, verify the local RNode interface is up:**

```bash
rnstatus
```

Expected: the RNode interface shows `UP` with a valid hardware address. If it shows `DOWN`, check the USB connection to the LEFT Heltec V3 and verify firmware was flashed correctly in Phase 6.1.

**Remote node test (if a second RNode is available):**

1. Configure a laptop with `rnsd` + RNode interface (separate Heltec V3 flashed with RNode firmware)
2. Walk to a distance checkpoint
3. Run `rnpath <destination_hash>` to verify path discovery to the rack node
4. Send a message via NomadNet or `rncp` and confirm delivery

> **If you only have one RNode:** Skip the walk-away test for Reticulum. The RNode firmware flash and `rnstatus` interface check are sufficient for integration testing. Full range testing can be done at the first field deployment.

---

### 7.6 UPS Power Budget and Runtime

**Tripp Lite BC600R specs:** 600VA / 300W rated · 7.2Ah @ 12V SLA battery · ~86Wh capacity · ~73Wh usable (85% inverter efficiency)

**Component power draw estimates:**

| Component | Idle | Typical | Peak |
|---|---|---|---|
| Raspberry Pi 5 16GB × 2 | ~16W | ~26W | ~46W |
| GL.iNet router | ~5W | ~6W | ~8W |
| TL-SG108S switch | ~4W | ~4W | ~5W |
| USB fan hub + 3× 80mm fans | ~3W | ~3W | ~4W |
| Touchscreen display | ~3W | ~4W | ~5W |
| 2× Heltec V3 LoRa radios (USB) | ~1W | ~1W | ~2W |
| Anker 747 adapter overhead | ~5W | ~5W | ~7W |
| **Total system draw** | **~37W** | **~49W** | **~77W** |

**Estimated battery runtime:**

| Scenario | Draw | Runtime |
|---|---|---|
| Standby / quiet overnight | ~37W | ~115 min (~2 hrs) |
| Typical field deployment | ~49W | ~85 min (~1.5 hrs) |
| Heavy use (active ATAK, Meshtastic traffic, Matrix load) | ~65W | ~65 min (~1 hr) |
| Maximum load (all services, Monero syncing, peak radio traffic) | ~77W | ~55 min |

> **Field planning rule of thumb: budget 60-90 minutes of runtime at a typical community deployment.** The node will sustain all services comfortably through a 1-hour power outage under normal field conditions. Monero and Headscale are the highest-draw services — stopping them (`docker compose stop monerod headscale`) during outages extends runtime by 10-15 minutes.

**UPS Failover Test:**

1. With all services running, pull the wall power plug
2. Verify: all services stay up, UPS beeps once
3. Monitor with: `docker compose ps` on both nodes — should show all running
4. Check Tripp Lite BC600R runtime indicator light
5. Restore power — verify UPS recharges and services continue without restart

---

## 10. Phase 8: Field Hardening

### 8.1 Full Backup Procedure

Run this before any major change, before an event, and after any credential rotation. Produces three files: a comms tarball, a tactical tarball, and an OTS database dump. All three are required to fully restore either Pi.

**What is backed up:**

| Pi | What | Why |
|---|---|---|
| comms | `config/` + `docker-compose.yml` | Container config, nginx, TLS certs, conduit.toml |
| comms | `data/conduit/` | Matrix RocksDB — all chat history and room state |
| comms | `data/tor/` | Tor hidden service private keys — lose this = .onion addresses change permanently |
| comms | `data/i2pd/` | I2P router keys and peer database |
| comms | `data/community-web/` | Community info page content |
| tactical | `config/` + `docker-compose.yml` | Headscale config, Mosquitto config |
| tactical | `data/headscale/` | Headscale SQLite DB + VPN private keys — lose this = all VPN nodes must re-register |
| tactical | `data/reticulum/` | Reticulum identity keys — lose this = new mesh identity |
| tactical | `data/nomadnet/` | NomadNet pages and node identity |
| tactical | `~/ots/` | OTS config.yml (RabbitMQ password, port config) |
| tactical | OTS PostgreSQL dump | All EUDs, issued certs, data packages, markers, tracks |

**Step 1 — Pi #1 (comms): stop, archive, restart**

```bash
# [SSH — comms-lan]
cd /opt/community-node && docker compose down
tar czf ~/comms-full-backup-$(date +%Y%m%d).tar.gz config/ docker-compose.yml data/
docker compose up -d
```

**Step 2 — Pi #2 (tactical): dump OTS database, stop, archive, restart**

```bash
# [SSH — tactical-lan]
sudo -u postgres pg_dump opentakserver > ~/ots-db-$(date +%Y%m%d).sql
cd /opt/tactical-node && sudo systemctl stop opentakserver cot_parser eud_handler eud_handler_ssl && docker compose down
tar czf ~/tactical-full-backup-$(date +%Y%m%d).tar.gz config/ docker-compose.yml data/ -C /home/pi ots/
docker compose up -d && sudo systemctl start opentakserver cot_parser eud_handler eud_handler_ssl
```

**Step 3 — Copy everything to your laptop**

```bash
# [Local — laptop]
scp pi@192.168.8.10:~/comms-full-backup-*.tar.gz .
scp pi@192.168.8.20:~/tactical-full-backup-*.tar.gz .
scp pi@192.168.8.20:~/ots-db-*.sql .
```

> Store copies in two separate locations (laptop + Obsidian vault `z_Backups/`). All three files together are your complete rebuild kit. Without the OTS SQL dump and Tor private keys, a Pi replacement means losing chat history, issued certs, and .onion addresses.

**What is NOT backed up here:**

- **Monero LMDB** (`/mnt/nvme/monero/data/`) — 100GB+, impractical to archive. The NVMe is physically separate from the Pi board. If the Pi fails but the NVMe survives, remount it on the replacement Pi. If both fail, rsync from your x86 node or resync from the network (takes days).
- **OTS issued data packages** stored under `/opt/opentakserver/` — regenerate via OTS Web UI → Data Packages after restore. Client devices will prompt to re-download on next connection.

---

### 8.2 Tor .onion Addresses

The Tor hidden service private keys are included in the `comms-full-backup` tarball (`data/tor/`). As long as that backup is intact, your .onion addresses survive Pi replacement.

Record your addresses here for reference (retrieve with the commands in §4.6):

| Service | .onion Address |
|---|---|
| Matrix API (homeserver) | *(fill in after deploy)* |
| Element Web (chat client) | *(fill in after deploy)* |
| Community Page (info/connect) | *(fill in after deploy)* |

To verify addresses are still valid after a restore:

```bash
# [SSH — comms-lan]
docker exec tor cat /var/lib/tor/matrix_hidden_service/hostname
docker exec tor cat /var/lib/tor/element_hidden_service/hostname
docker exec tor cat /var/lib/tor/community_hidden_service/hostname
```

All three should match the table above. If they differ, the restore used the wrong backup or `data/tor/` was missing from the tarball.

---

### 8.3 Air-Gap Procedure (Emergency Isolation)

When the node needs to go fully offline from the internet while maintaining local mesh services:

**Step 1 — Stop internet-facing services:**
```bash
# Pi #1
cd /opt/community-node
docker compose stop cloudflared

# Pi #2
cd /opt/tactical-node
docker compose stop monerod    # stops broadcasting to p2p network
```

**Step 2 — Cut WAN on GL.iNet:**
```bash
# Via web UI: http://192.168.8.1 → Internet → Disconnect
# OR physically unplug the WAN Ethernet cable
```

**Step 3 — Verify isolation:**
```bash
ip route     # no default gateway should remain
ping 8.8.8.8 # should time out
```

**What stays up after air-gap:**
- ✓ Matrix homeserver (local users only)
- ✓ Element Web (browser access on local WiFi)
- ✓ OpenTAK Server (ATAK on local WiFi)
- ✓ Reticulum mesh (TCP over local WiFi)
- ✓ LoRa radio mesh (fully off-grid, no WiFi needed)
- ✓ NomadNet pages (local + LoRa)
- ✓ Mosquitto MQTT (Meshtastic/OTS internal broker)
- ✗ Monero p2p sync (paused — resumes on reconnect)
- ✗ Cloudflare Tunnel (offline — expected)

---

### 8.4 Restore Procedure (Pi Replacement)

Use this when a Pi fails and you are rebuilding on a new board. You need the backup files from §8.1 on your laptop before starting.

**Prerequisites:**
- New Raspberry Pi 5 flashed with Raspberry Pi OS Lite (64-bit)
- SSH access confirmed, hostname set (`comms` or `tactical`), static IP assigned via router DHCP lease
- Backup files from §8.1 on your laptop: `comms-full-backup-YYYYMMDD.tar.gz`, `tactical-full-backup-YYYYMMDD.tar.gz`, `ots-db-YYYYMMDD.sql`

---

#### Restore Pi #1 (comms — 192.168.8.10)

**Step 1 — Install Docker:**
```bash
# [SSH — comms-lan]
curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER && newgrp docker
```

**Step 2 — Create directory and push backup from laptop:**
```bash
# [Local — laptop]
ssh pi@192.168.8.10 "sudo mkdir -p /opt/community-node && sudo chown ps:ps /opt/community-node"
scp comms-full-backup-YYYYMMDD.tar.gz pi@192.168.8.10:~
```

**Step 3 — Extract backup:**
```bash
# [SSH — comms-lan]
tar xzf ~/comms-full-backup-YYYYMMDD.tar.gz -C /opt/community-node/
```

**Step 4 — Pull images and start:**
```bash
# [SSH — comms-lan]
cd /opt/community-node && docker compose pull && docker compose up -d
```

**Step 5 — Verify .onion addresses:**
```bash
# [SSH — comms-lan]
docker exec tor cat /var/lib/tor/matrix_hidden_service/hostname
docker exec tor cat /var/lib/tor/element_hidden_service/hostname
docker exec tor cat /var/lib/tor/community_hidden_service/hostname
```

All three must match the addresses in §8.2. If they match, Tor identity is intact.

**Step 6 — Reinstall systemd auto-start (§8.5) and AP isolation fix (§3.2).**

---

#### Restore Pi #2 (tactical — 192.168.8.20)

**Step 1 — Install Docker and OTS:**
```bash
# [SSH — tactical-lan]
curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER && newgrp docker
curl -fsSL https://opentakserver.io/install.sh | sudo bash
```

> The OTS installer creates the PostgreSQL instance and systemd units. Stop OTS before restoring the database.

**Step 2 — Stop OTS, create directory, push backups from laptop:**
```bash
# [SSH — tactical-lan]
sudo systemctl stop opentakserver cot_parser eud_handler eud_handler_ssl
sudo mkdir -p /opt/tactical-node && sudo chown ps:ps /opt/tactical-node
```

```bash
# [Local — laptop]
scp tactical-full-backup-YYYYMMDD.tar.gz pi@192.168.8.20:~
scp ots-db-YYYYMMDD.sql pi@192.168.8.20:~
```

**Step 3 — Extract Docker/Headscale/Reticulum backup:**
```bash
# [SSH — tactical-lan]
tar xzf ~/tactical-full-backup-YYYYMMDD.tar.gz -C /opt/tactical-node/ --exclude='./ots'
# Restore OTS config to home directory
tar xzf ~/tactical-full-backup-YYYYMMDD.tar.gz -C /home/pi/ './ots'
```

**Step 4 — Restore OTS PostgreSQL database:**
```bash
# [SSH — tactical-lan]
sudo -u postgres psql -c "DROP DATABASE IF EXISTS opentakserver;"
sudo -u postgres psql -c "CREATE DATABASE opentakserver;"
sudo -u postgres psql opentakserver < ~/ots-db-YYYYMMDD.sql
```

**Step 5 — Mount NVMe and restore Monero:**

If the NVMe drive survived the Pi failure, remount it:
```bash
# [SSH — tactical-lan]
sudo mkdir -p /mnt/nvme && sudo mount /dev/nvme0n1p1 /mnt/nvme
```

Verify the blockchain data is present: `ls /mnt/nvme/monero/data/lmdb/` — should show `data.mdb` and `lock.mdb`.

If the NVMe is gone or corrupted, rsync from your x86 Monero node (takes minutes over LAN vs. days to resync from the network):
```bash
# [Local — laptop, via WSL or Git Bash]
rsync -avP /c/MoneroNode/data/lmdb/ pi@192.168.8.20:/mnt/nvme/monero/data/lmdb/
```

**Step 6 — Start everything:**
```bash
# [SSH — tactical-lan]
sudo systemctl start opentakserver cot_parser eud_handler eud_handler_ssl
cd /opt/tactical-node && docker compose up -d
```

**Step 7 — Verify OTS:**
```bash
# [SSH — tactical-lan]
systemctl is-active opentakserver
curl -s http://127.0.0.1:8080/api/me | python3 -m json.tool
```

OTS should return a JSON response. Open `http://192.168.8.20:8080` in a browser and confirm the map loads with the Community Node marker visible.

**Step 8 — Headscale reconnection:**

Existing VPN nodes (your phone, field devices) will reconnect automatically — their keys are in the restored `data/headscale/db.sqlite`. Verify with:
```bash
# [SSH — tactical-lan]
docker exec headscale headscale nodes list
```

All previously registered devices should appear. If a device shows `expired`, re-run key expiry extension (see §6.3).

**Step 9 — Reinstall systemd auto-start (§8.5) and udev rules (§5B Step 4).**

> **Rebuild time estimate:** Pi #1 ~20 minutes. Pi #2 ~45 minutes (plus Monero rsync time if NVMe failed). Both Pis simultaneously from separate laptops is viable if you have the hardware.

---

### 8.5 Create Systemd Auto-Start (so services survive power cycles)

```bash
# Pi #1
sudo nano /etc/systemd/system/community-node.service
```

```ini
# /etc/systemd/system/community-node.service
# Community Node — Pi #1 (comms, 192.168.8.10)
# Starts the full communications stack on boot via Docker Compose.
#
# --profile clearnet includes Cloudflare Tunnel (cloudflared).
# Omit --profile clearnet to run air-gapped (local/Tor/I2P only).
#
# To manage manually:
#   sudo systemctl start community-node
#   sudo systemctl stop community-node
#   sudo systemctl status community-node

[Unit]
Description=Community Node Docker Stack — Pi #1 Communications
# Wait for Docker daemon to be fully ready before starting
After=docker.service
Requires=docker.service

[Service]
# oneshot = run the command once; RemainAfterExit keeps unit "active" after it finishes
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/community-node
# Start all services including Cloudflare Tunnel (clearnet profile)
ExecStart=/usr/bin/docker compose --profile clearnet up -d
# On stop/reboot, bring all containers down cleanly
ExecStop=/usr/bin/docker compose --profile clearnet down
# Allow up to 5 minutes for all containers to pull/start on first boot
TimeoutStartSec=300

[Install]
# Start at normal multi-user boot (after network is up)
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable community-node && sudo systemctl start community-node
```

**Pi #2 — `/etc/systemd/system/tactical-node.service`:**

```ini
# /etc/systemd/system/tactical-node.service
# Community Node — Pi #2 (tactical, 192.168.8.20)
# Starts the full tactical/crypto stack on boot via Docker Compose.
#
# --profile vpn includes Headscale VPN coordination server.
# Omit --profile vpn to run without Headscale (e.g. fully air-gapped).
#
# To manage manually:
#   sudo systemctl start tactical-node
#   sudo systemctl stop tactical-node
#   sudo systemctl status tactical-node

[Unit]
Description=Community Node Docker Stack — Pi #2 Tactical
# Wait for Docker daemon to be fully ready before starting
After=docker.service
Requires=docker.service

[Service]
# oneshot = run the command once; RemainAfterExit keeps unit "active" after it finishes
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/tactical-node
# Start all tactical services including Headscale VPN (vpn profile)
ExecStart=/usr/bin/docker compose --profile vpn up -d
# On stop/reboot, bring all containers down cleanly
ExecStop=/usr/bin/docker compose --profile vpn down
# Allow up to 10 minutes — first-boot Docker image pulls can be slow; -d exits immediately on subsequent boots
TimeoutStartSec=600

[Install]
# Start at normal multi-user boot (after network is up)
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable tactical-node && sudo systemctl start tactical-node
```

> **✅ Systemd services finalized.** Both service files use `up -d` (detached mode) so systemd does not wait for containers to stream logs — the unit exits cleanly after containers start. Pi #2 `TimeoutStartSec=600` accommodates first-boot Docker image pulls; subsequent boots are fast. OpenTAK Server runs under its own systemd unit (`opentakserver.service`), separate from the Docker compose stack. Both services are enabled and confirmed working.

---

### 8.5 Field Deployment Checklist (Every Deployment)

Before transporting:
- [ ] All services confirmed running (`docker compose ps`)
- [ ] Monero sync status checked (write down current height)
- [ ] Config backup is current and stored offsite
- [ ] UPS at 100% charge
- [ ] All cables velcro-tied, nothing loose
- [ ] Unscrew both 915 MHz antennas from LoRa panel SMA bulkheads — store in case foam pocket or cable bag (antennas are the only external protrusions; everything else is within the rack envelope)
- [ ] If using Pelican 1610: lay rack flat in case on kaizen foam insert; BC600R remains inside rack at U1

On arrival:
- [ ] UPS → PDU → wait 5 sec → Pi's power on
- [ ] Wait 90 sec for Docker stacks to start
- [ ] Test Matrix, ATAK, LoRa connectivity before declaring operational
- [ ] Announce .onion addresses on LoRa/Meshtastic if internet-available

---

### 8.6 Matrix Status Bot (Node Health Reports)

A lightweight Python bot that posts health and sync status for both nodes into a Matrix room. Runs on Pi #1 as a Docker container alongside the comms stack.

**What it reports (every hour + on `!status` command):**
- Conduit, Element, I2P, Tor, Cloudflared — up/down
- OpenTAK Server, Mosquitto, Reticulum — up/down
- Monero sync status (height + synchronized flag)

#### 8.6.1 Create a bot Matrix account

On Pi #1, temporarily re-enable registration in `/opt/community-node/config/conduit/conduit.toml`:
```toml
allow_registration = true
```
Restart Conduit: `docker compose restart conduit`

Register the bot user:
```bash
curl -X POST "http://localhost:6167/_matrix/client/v3/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "statusbot",
    "password": "STRONG_BOT_PASSWORD_HERE",
    "auth": {
      "type": "m.login.registration_token",
      "token": "YOUR_REGISTRATION_TOKEN"
    }
  }'
```

Set `allow_registration = false` again and restart Conduit.

Log into Element as admin, create a private room called **#node-status**, and invite `@statusbot:yourdomain.com`.

#### 8.6.2 Create the bot script

On Pi #1:
```bash
mkdir -p /opt/community-node/statusbot
nano /opt/community-node/statusbot/bot.py
```

```python
#!/usr/bin/env python3
"""
M2 Community Node — Matrix Status Bot
Posts health checks for both nodes to a Matrix room.
Responds to !status command and posts automatically every hour.
"""

import asyncio
import aiohttp
import time
from nio import AsyncClient, MatrixRoom, RoomMessageText

HOMESERVER    = "http://conduit:6167"
BOT_USER      = "@statusbot:yourdomain.com"
BOT_PASSWORD  = "STRONG_BOT_PASSWORD_HERE"
STATUS_ROOM   = "#node-status:yourdomain.com"
REPORT_INTERVAL = 3600  # seconds

CHECKS = [
    # (label, url, node)
    ("Conduit (Matrix)",   "http://conduit:6167/_matrix/client/versions",  "comms"),
    ("Element Web",        "http://nginx:8080/",                            "comms"),
    ("I2P console",        "http://i2pd:7070/",                             "comms"),
    ("OpenTAK Web UI",     "http://192.168.8.20:8080/",                     "tactical"),
    ("Mosquitto",          "http://192.168.8.20:1883/",                     "tactical"),  # TCP; 200=up
    ("Reticulum",          "http://192.168.8.20:4242/",                     "tactical"),
    # Monero RPC is bound to 127.0.0.1 on Pi #2 — not reachable from Pi #1 via LAN.
    # Health check uses docker exec to curl from inside the monerod container instead.
    # ("Monero RPC", "http://192.168.8.20:18089/get_info", "tactical"),  # broken — localhost-only
]

async def run_checks():
    results = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for label, url, node in CHECKS:
            try:
                async with session.get(url) as r:
                    ok = r.status < 500
            except Exception:
                ok = False
            icon = "OK" if ok else "DOWN"
            results.append(f"[{node}] {label}: {icon}")

        # Monero sync detail — RPC is localhost-only on Pi #2, so we poll a
        # lightweight health endpoint served by a cron job on Pi #2.
        # The cron job (see §8.6.5) writes JSON to nginx on Pi #2 port 8081.
        try:
            r = requests.get("http://192.168.8.20:8081/monero-health.json", timeout=5)
            mdata = r.json()
            height = mdata.get("height", "?")
            target = mdata.get("target_height", "?")
            pct = mdata.get("sync_pct", "?")
            peers = mdata.get("outgoing_connections_count", "?")
            results.append(f"[tactical] Monero: height {height}/{target} ({pct}%) peers={peers}")
        except Exception:
            results.append("[tactical] Monero: health endpoint unreachable")

    ts = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    return f"**Node Status — {ts}**\n" + "\n".join(results)

async def main():
    client = AsyncClient(HOMESERVER, BOT_USER)
    await client.login(BOT_PASSWORD)

    # Resolve room alias to room ID
    resp = await client.room_resolve_alias(STATUS_ROOM)
    room_id = resp.room_id
    await client.join(room_id)

    last_report = 0

    async def cb(room: MatrixRoom, event: RoomMessageText):
        if hasattr(event, "body") and event.body.strip() == "!status":
            report = await run_checks()
            await client.room_send(room.room_id, "m.room.message",
                                   {"msgtype": "m.text", "body": report,
                                    "format": "org.matrix.custom.html",
                                    "formatted_body": report.replace("\n", "<br>")})

    client.add_event_callback(cb, RoomMessageText)

    async def scheduler():
        nonlocal last_report
        while True:
            now = time.time()
            if now - last_report >= REPORT_INTERVAL:
                report = await run_checks()
                await client.room_send(room_id, "m.room.message",
                                       {"msgtype": "m.text", "body": report})
                last_report = now
            await asyncio.sleep(60)

    await asyncio.gather(client.sync_forever(timeout=30000), scheduler())

asyncio.run(main())
```

#### 8.6.3 Add to comms docker-compose.yml

Append to the `services:` section of `/opt/community-node/docker-compose.yml`:

```yaml
  # ── Matrix Status Bot ──────────────────────────────────────
  statusbot:
    image: python:3.12.12-slim-bookworm
    restart: unless-stopped
    networks:
      - community-net
    volumes:
      - ./statusbot:/app
    command: >
      bash -c "pip install --quiet matrix-nio aiohttp &&
               python /app/bot.py"
    depends_on:
      - conduit
      - nginx
```

#### 8.6.4 Start the bot

```bash
cd /opt/community-node
docker compose up -d statusbot
docker compose logs -f statusbot
# Should show: logged in, joined room, waiting
```

Send `!status` in the **#node-status** room from your Element client to trigger an immediate report. Automatic reports post every hour.

#### 8.6.5 Monero Health Endpoint on Pi #2

The status bot runs on Pi #1, but Monero RPC binds to `127.0.0.1` on Pi #2. A cron job on Pi #2 polls the local RPC and writes a JSON file served by a minimal nginx instance on port 8081.

**[SSH — Pi #2 tactical-lan]**

Create the health check script:

```bash
mkdir -p /opt/tactical-node/monero-health
cat > /opt/tactical-node/monero-health/check.sh << 'SCRIPT'
#!/bin/bash
# Poll monerod RPC (localhost only) and write health JSON for remote status bot
OUT="/opt/tactical-node/monero-health/monero-health.json"
DATA=$(curl -s --max-time 5 http://127.0.0.1:18089/get_info 2>/dev/null)
if [ $? -eq 0 ] && echo "$DATA" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "$DATA" | python3 -c "
import sys, json
d = json.load(sys.stdin)
out = {
    'height': d.get('height', 0),
    'target_height': d.get('target_height', 0),
    'sync_pct': round(d.get('height',0) / max(d.get('target_height',1), d.get('height',1)) * 100, 1),
    'outgoing_connections_count': d.get('outgoing_connections_count', 0),
    'status': d.get('status', 'UNKNOWN'),
    'updated': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime())
}
json.dump(out, open('$OUT', 'w'))
"
else
    echo '{"status":"UNREACHABLE","updated":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$OUT"
fi
SCRIPT
chmod +x /opt/tactical-node/monero-health/check.sh
```

Add the cron job (runs every 5 minutes):

```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/tactical-node/monero-health/check.sh") | crontab -
```

Serve the JSON file via a one-line Python HTTP server in a systemd unit:

```bash
cat > /etc/systemd/system/monero-health-http.service << 'EOF'
[Unit]
Description=Monero health JSON endpoint
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/tactical-node/monero-health
ExecStart=/usr/bin/python3 -m http.server 8081 --bind 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now monero-health-http
```

**Verify from Pi #1:**

```bash
curl -s http://192.168.8.20:8081/monero-health.json | python3 -m json.tool
```

Expected output:
```json
{
    "height": 3456789,
    "target_height": 3456790,
    "sync_pct": 100.0,
    "outgoing_connections_count": 12,
    "status": "OK",
    "updated": "YYYY-MM-DDTHH:MM:SSZ"
}
```

---

### 8.7 Annotate Comms Node Configuration Files

> **When to do this:** After both stacks are running and passing Phase 7 integration tests. Not before — you need working configs to annotate, and changes during annotation could break a working system.

All comms node config files were created during Phase 4 as minimal working configs without inline comments. This pass adds explanatory comments so any operator can understand intent without digging through the build guide.

**Annotation style** (match Phase 5 tactical configs):
- Comment above each block explaining *why*, not *what*
- For TOML/YAML: use `#` comments on the line above the setting
- For JSON (Element config): JSON does not support comments — add a `_comment_<key>` field or document in a companion `.md` file alongside the config
- For nginx: use `# ──` section dividers between server blocks

**[SSH — Pi #1 comms-lan]**

**Files to annotate:**

| File | Path | Key items to explain |
|---|---|---|
| Docker Compose | `/opt/community-node/docker-compose.yml` | Each service purpose, network topology, volume mounts, profile groups (`comms`, `tor`, `vpn`) |
| Conduit config | `/opt/community-node/config/conduit/conduit.toml` | `server_name` vs `address`, registration token purpose, `database_backend` choice, `max_request_size` |
| Element config | `/opt/community-node/config/element/element-config.json` | `base_url` pointing to nginx (not Conduit directly), `server_name` matching Conduit, custom theme for kiosk |
| Nginx config | `/opt/community-node/config/nginx/nginx.conf` | Each server block: port 80 (Matrix well-known), 443 (HTTPS if certs present), 8448 (federation), 8080 (Element Web), 8081 (community page). Rate limiting rationale. `client_max_body_size` for DTED packages. |
| Tor config | `/opt/community-node/config/tor/torrc` | Each `HiddenServiceDir` and `HiddenServicePort` mapping. Why services are proxied over HTTP behind Tor (Tor provides transport encryption — TLS on top is redundant and breaks .onion cert validation). |
| i2pd config | `/opt/community-node/config/i2pd/i2pd.conf` | Bandwidth class selection, SAM bridge port, HTTP proxy port |
| i2pd tunnels | `/opt/community-node/config/i2pd/tunnels.conf` | Each tunnel: name, type (server/client), destination service and port |
| Systemd service | `/etc/systemd/system/community-node.service` | `Type=oneshot` + `RemainAfterExit=yes` pattern, `--profile` flags, `TimeoutStartSec` for slow image pulls |

**Procedure:**

1. SSH into Pi #1
2. Back up the config directory first: `sudo tar czf /opt/community-node/config-pre-annotation.tar.gz /opt/community-node/config/`
3. Edit each file, adding comments per the table above
4. After annotating, restart the stack and verify all services still pass the Phase 7.1 health checks:
   ```bash
   cd /opt/community-node && docker compose down && docker compose up -d
   ```
5. If any service fails to start, restore from the backup tarball and diff to find the annotation that broke the config (most likely a stray character in TOML or YAML indentation)

---

---

## 11. Phase 9: Post-Launch Improvements

### 9.1 ATAK Remote Access via Headscale (Clearnet Users)

> **Goal:** Allow ATAK users outside the local WiFi to connect to OpenTAK Server over the internet.

Cloudflare Tunnel cannot proxy raw TCP (ATAK CoT protocol) — only HTTP/HTTPS. The correct solution is **Headscale**, which is already in the compose file under the `vpn` profile.

> **⚠️ Cloudflare Tunnel is incompatible with Headscale.** Headscale's TS2021 control protocol uses a custom `Upgrade: ts2021` HTTP header. Cloudflare's HTTP proxy only passes `Upgrade: websocket` — all other custom upgrade headers are stripped at the CDN layer regardless of nginx proxy configuration, WebSocket zone settings, or `http2Origin` flags. This is a confirmed, documented limitation ([Headscale issue #2379](https://github.com/juanfont/headscale/issues/2379)). **Headscale requires one direct TCP port on the router.**

**Step 1 — Remove the headscale route from Cloudflare Tunnel (if previously added)**

Cloudflare → Zero Trust → Networks → Connectors → `m2-community-node` → Configure → Published application routes → delete the `m2vpn.yourdomain.com` route.

**Step 2 — Add a DNS A record (DNS-only)**

Cloudflare dashboard → `yourdomain.com` → DNS → Records → Add record:
- Type: `A`
- Name: `headscale`
- IPv4: your public IP (check at `https://whatismyip.com` from the node's network)
- Proxy status: **DNS only (gray cloud)** — do NOT enable orange cloud proxy

**Step 3 — Eliminate double NAT (if GL.iNet is behind another router)**

If the GL.iNet WAN IP is a private address (e.g. `192.168.1.x`), it is behind another router and port forwards on the GL.iNet will not be reachable from the internet. Fix this with IP Passthrough on the upstream router.

**AT&T BGW320-505 (Nokia):** Log into the upstream gateway → **Firewall → IP Passthrough**:
- **Allocation Mode:** `Passthrough`
- **Passthrough Mode:** `DHCPS-fixed`
- **Device List:** Choose from list → select the GL.iNet (identified by its WAN MAC address)
- Save — then disconnect/reconnect the GL.iNet WAN (repeater) to force a DHCP renewal

> GL.iNet WAN connection type is **Repeater** (found under Internet → Repeater in GL.iNet admin v4.x), not "WiFi WAN".
> After IP Passthrough activates, the GL.iNet WAN IP will change to the public IP (e.g. `104.183.119.70`). Verify in GL.iNet admin before continuing.

**Step 4 — Add a port forward on the GL.iNet router**

GL.iNet admin (`http://192.168.8.1`) → **Network → Port Forwarding** → Add:
- **Description:** `Headscale VPN`
- **Protocol:** TCP
- **External zone:** `wan`
- **External port:** `443`
- **Internal zone:** `lan`
- **Internal IP:** `192.168.8.20`
- **Internal port:** `443`

**Step 5 — Verify Headscale is running**

```bash
# SSH → Pi #2
sudo docker compose --profile vpn up -d
curl https://m2vpn.yourdomain.com/health
# Expected: {"status":"pass"}
```

**Step 6 — Create users and auth key**

```bash
# SSH → Pi #2
sudo docker exec tactical-node-headscale-1 headscale users create admin
sudo docker exec tactical-node-headscale-1 headscale users create community
sudo docker exec tactical-node-headscale-1 headscale preauthkeys create --user 1 --expiration 90d --reusable
```

**Step 7 — Connect client devices**

**Windows (PowerShell, Administrator):**
```powershell
tailscale up --login-server https://m2vpn.yourdomain.com --authkey <key> --reset
```

**Android (Tailscale Play Store app, v1.80+):**

> The custom coordination server field is NOT in the main app Settings. It is behind a three-dot menu on the Accounts screen. The deep link `tailscale://login?server=...` does not work on Android. Use the interactive login method below — it bypasses the pre-auth key flow entirely.

1. Open Tailscale → tap the **profile icon** (top-right) → tap **Accounts**
2. Tap the **three-dot menu** (top-right of the Accounts screen)
3. Select **"Use an alternate server"**
4. Enter: `https://m2vpn.yourdomain.com` → tap **Add account**
5. A screen appears with a `headscale nodes register` command — leave it open
6. Run the command on Pi #2 immediately (key expires in ~60 seconds):

```bash
# SSH — Pi #2 (tactical)
sudo docker exec tactical-node-headscale-1 headscale nodes register --key <key-from-screen> --user admin
```

7. Phone connects automatically — force-close and reopen the app if it shows "Not Connected"

Once connected, every device gets a `100.64.x.x` VPN IP and can reach both Pis and all LAN services remotely.

**Step 8 — Verify registration and rename nodes**

```bash
# SSH — Pi #2 (tactical)
sudo docker exec tactical-node-headscale-1 headscale nodes list
```

Rename any node with an auto-generated or unclear hostname:
```bash
# SSH — Pi #2 (tactical)
sudo docker exec tactical-node-headscale-1 headscale nodes rename --identifier <id> <name>
```

**Confirmed registered nodes ():**

| ID | Name | IP | Role |
|---|---|---|---|
| 1 | mike-pc | 100.64.1.3 | Operator laptop |
| 4 | tactical | 100.64.1.1 | Pi #2 — subnet router, **primary** for 192.168.8.0/24 |
| 5 | comms | 100.64.1.2 | Pi #1 — subnet router, **standby** for 192.168.8.0/24 |
| 6 | s25 | 100.64.1.4 | Operator phone |

> Headscale automatically elects one subnet router as primary. Both tactical and comms advertise `192.168.8.0/24` — if tactical goes offline, comms takes over. Approve routes on both with `headscale nodes approve-routes --identifier <id> --routes 192.168.8.0/24`.


> **One open port:** Only TCP 443 is exposed publicly — the Headscale control plane (HTTPS). Actual VPN data traffic uses Tailscale's DERP relay infrastructure (outbound-only). ATAK remote users connect to `192.168.8.20:8088` (TCP) or `192.168.8.20:8089` (SSL) after connecting to VPN.
>
> **Dynamic IP:** When deploying in the field on a new network (cellular, Starlink, etc.), the public IP will change. Update the Cloudflare DNS A record for `m2vpn.yourdomain.com` to the new IP before connecting clients. The DDNS script (§5.3.4) automates this — runs every 5 minutes via systemd timer.

---

### 9.1.1 Remote Operator Onboarding — Handoff Procedure

Use this when an incoming support team is en route from a non-impacted area and needs to join the M2 common operating picture before arriving on-site. Two tiers of access:

**Tier 1 — Web Map (view-only, no install)**

Send the operator this URL: `https://tak.yourdomain.com`

If Cloudflare Access is enabled (§4.5.4), also send them the email address you whitelisted. They enter it, receive a one-time PIN, and see the live OTS map in their browser. No app install, no VPN, works from any device.

This is the fastest path to situational awareness — incoming support can see team positions, markers, and data packages within 60 seconds.

**Tier 2 — Full ATAK over VPN (complete CoT)**

For operators who need position sharing, GeoChat, ExCheck, and full ATAK capabilities from outside the local WiFi.

**What the operator needs:**
- Android phone with ATAK-CIV installed (Play Store, free)
- Tailscale app installed (Play Store, free)

**What you (the node operator) do:**

1. Generate a pre-auth key:

```bash
# SSH — Pi #2 (tactical)
sudo docker exec tactical-node-headscale-1 headscale preauthkeys create --user community --expiration 24h
```

2. Send the operator (via Signal, Matrix, or voice) these three items:
   - Headscale server URL: `https://m2vpn.yourdomain.com`
   - The pre-auth key from step 1
   - ATAK connection info: `192.168.8.20` TCP port `8088`

**What the operator does:**

1. Open Tailscale → profile icon → Accounts → three-dot menu → **Use an alternate server**
2. Enter: `https://m2vpn.yourdomain.com`
3. Paste the pre-auth key when prompted
4. Wait for "Connected" status — their phone now has a `100.64.x.x` VPN IP
5. Open ATAK → Settings → Network Preferences → Network Connection Preferences → Manage Server Connections
6. Add server: address `192.168.8.20`, port `8088`, protocol **TCP**
7. **Uncheck** "Use default SSL/TLS certificates" (critical — see §14.2 troubleshooting)
8. Tap OK — their position appears on the map within seconds

**After the event:**

Revoke the pre-auth key or let it expire (24h default). List and delete nodes:

```bash
# SSH — Pi #2 (tactical)
sudo docker exec tactical-node-headscale-1 headscale nodes list
sudo docker exec tactical-node-headscale-1 headscale nodes delete --identifier <id>
```

> **Key expiry strategy:** Use `--expiration 24h` for incident response (auto-expires). Use `--expiration 90d --reusable` for permanent team members. Never create non-expiring keys.

> **Bandwidth note:** ATAK CoT is lightweight (~1-2 KB per position update). A remote operator on cellular data uses roughly 50-100 KB/hour of CoT traffic. VPN overhead adds ~20%.

---

### 9.2 ATAK SSL Certificate Setup

OpenTAK Server auto-generates certificates on first startup. Clients can enroll certificates via the built-in certificate enrollment endpoint at port 8446.

**Steps:**
1. Open the OTS web UI: `http://192.168.8.20:8080`
2. Navigate to the certificate management page
3. Generate a client certificate data package (.zip)
4. Transfer the data package to your Android device
5. In ATAK: import the data package — it auto-configures the server connection with SSL
6. Alternative: point ATAK to `192.168.8.20:8446` for automatic certificate enrollment
4. In ATAK: Server connection → SSL → port `8089`

> Until SSL is set up, TCP on port 8088 is fine for trusted LAN use.
> SSL becomes important once remote users connect via Headscale over the internet.

---

## 12. Quick Reference

### Access Cheat Sheet

Use the table below to find the right address for any service based on how you're connecting.

#### Matrix / Element (Chat)

| Method | How to Connect | Address |
|---|---|---|
| CommunityNode WiFi | Browser | `http://192.168.8.10:8080` |
| CommunityNode WiFi | Matrix client homeserver | `https://m2-matrix.yourdomain.com` |
| Clearnet (internet) | Browser | `https://communitynode.yourdomain.com` |
| Clearnet (internet) | Matrix client homeserver | `https://m2-matrix.yourdomain.com` |
| Tor | Tor Browser (Element Web) | `http://YOUR_ELEMENT_ONION.onion` |
| Tor | Matrix client homeserver | `http://YOUR_MATRIX_ONION.onion` |

> **LAN note:** `https://m2-matrix.yourdomain.com` works on CommunityNode WiFi only because the GL.iNet router has a hosts file entry pointing that domain to `192.168.8.10`. This does not work on other networks without that override.

#### Community Info Page

| Method | How to Connect | Address |
|---|---|---|
| CommunityNode WiFi | Browser | `http://192.168.8.10:8081` |
| Tor | Tor Browser | `http://YOUR_COMMUNITY_ONION.onion` |
| I2P | I2P-capable browser | *(see I2P tunnel address in i2pd console)* |

> This page is the recommended first link to hand to new members — it explains all connection methods.

#### ATAK / OpenTAK (Tactical)

| Method | How to Connect | Address |
|---|---|---|
| CommunityNode WiFi | ATAK → TAK Server → TCP CoT | `192.168.8.20` port `8088` |
| CommunityNode WiFi | ATAK → TAK Server → SSL CoT | `192.168.8.20` port `8089` |
| CommunityNode WiFi | Browser → OTS Web Map UI | `http://192.168.8.20:8080` |
| Clearnet (internet) | Browser → OTS Web Map | `https://tak.yourdomain.com` |
| Remote (VPN) | ATAK → TCP CoT over Headscale | `192.168.8.20` port `8088` (after VPN connect) |
| Remote (VPN) | ATAK → SSL CoT over Headscale | `192.168.8.20` port `8089` (after VPN connect) |

> **Local users:** Connect ATAK directly to `192.168.8.20` on CommunityNode WiFi.
> **Remote users (browser only):** Open `https://tak.yourdomain.com` for the live web map. Protected by Cloudflare Access (§4.5.4).
> **Remote users (full ATAK):** Install Tailscale, join Headscale VPN, then connect ATAK to `192.168.8.20:8088`. See remote onboarding procedure (§9.1.1).

#### ATAK Onboarding — Operator Script

Use this when a new user has just connected to CommunityNode WiFi and needs to get on the tactical map.

**Step 1 — Install the apps:**

Tell the user:
- **Android:** "Open the Play Store and search for **ATAK-CIV**. Install it — it's free."
- **iPhone:** "Open the App Store and search for **iTAK**. Install it — it's free."
- **If doing SAR:** "Also install **WASP** from the Play Store — it's the search marking tool."
- **For voice:** "Also install **Mumla** from the Play Store — it's push-to-talk."

Or have them scan the QR code on the community page (`http://192.168.8.10:8081`).

**Step 2 — Open the app and set a callsign:**

Tell the user:
- "Open the app. It will ask for a callsign — use your name or handle. This is what other people see on the map."
- "Tap through the initial setup. Accept the permissions it asks for (location is required)."
- "**Important:** Set location permission to **Allow all the time** — otherwise your position stops broadcasting when the screen turns off."

**Step 3 — Connect to the server (ATAK on Android):**

Tell the user:
1. "Tap the three-line menu at the top right."
2. "Tap **Settings**."
3. "Tap **Network Preferences** > **Network Connection Preferences** > **Manage Server Connections**."
4. "Tap the **+** button to add a server."
5. "Enter the address: **192.168.8.20**"
6. "Port: **8088**"
7. "Protocol: **TCP**"
8. "**Uncheck** 'Use default SSL/TLS certificates' — this is critical, it auto-enables and will break the connection."
9. "Tap **OK** or **Connect**."

> **SSL/TLS gotcha:** The "Use default SSL/TLS certificates" checkbox re-enables itself when you edit a server entry. If ATAK shows "No Data" or "Connection timed out," delete the server entry and re-add it with the checkbox unchecked. See §14.2 for details.

**Step 3 — Connect to the server (iTAK on iPhone):**

Tell the user:
1. "Tap the gear icon (Settings)."
2. "Tap **TAK Servers** > **Add Server**."
3. "Host: **192.168.8.20**, Port: **8088**, Protocol: **TCP**"
4. "Tap **Connect**."

**Step 4 — Connect Mumla (voice):**

Tell the user:
1. "Open Mumla."
2. "Add server: address **192.168.8.20**, port **64738**."
3. "Enter any username — it's your voice callsign."
4. "Tap Connect. You're now on push-to-talk voice."

**Step 5 — Verify:**

Tell the user:
- "You should see a map with your blue dot showing your location."
- "You should also see a **Community Node** marker — that's this node."
- "If you see other blue dots, those are other people on the network."
- "Pinch to zoom, long-press to drop a marker, use the chat icon for messaging."

> **Elevation data:** DTED terrain data is pre-loaded on the server. This gives you elevation readouts and line-of-sight analysis on the map.

> **Troubleshooting:** If the map is blank, zoom out — you may be viewing the wrong area. If you can't connect to the server, make sure you're on the CommunityNode WiFi (not cellular data). If ATAK shows "No Data," the SSL/TLS checkbox has re-enabled itself — delete the server entry and re-add it. If it still fails, ask the operator to verify OTS is running: `systemctl is-active opentakserver` on the tactical Pi.

> **Battery:** ATAK with GPS drains a phone in 2-4 hours. Bring a battery pack.

#### Meshtastic / LoRa Radio

| Method | How to Connect | Notes |
|---|---|---|
| Any location | Meshtastic app (Android/iOS) | No internet or WiFi required. 900 MHz LoRa, 1–5 km range. |
| CommunityNode WiFi | Meshtastic app → Bluetooth or WiFi | Connect to Heltec V3 RIGHT (ANT 2) |

#### Operator / Admin Services (LAN only)

| Service | Address | Notes |
|---|---|---|
| I2P web console | `http://192.168.8.10:7070` | View router stats, tunnel addresses |
| OpenTAK Web UI | `http://192.168.8.20:8080` | Live map, cert management, admin |
| Monero RPC | `http://127.0.0.1:18089` | Pi #2 localhost only (not LAN-accessible); use Tailscale VPN `100.64.1.1:18089` for remote access |
| Mosquitto MQTT | `192.168.8.20:1883` | Meshtastic/OTS internal broker |
| GL.iNet router admin | `http://192.168.8.1` | Network config, DHCP, hosts file |

### Headscale VPN — What It Gives You

Headscale creates an encrypted WireGuard mesh between all registered devices. Once connected, your device behaves as if it is physically on the `192.168.8.x` LAN — from anywhere in the world.

**Registered devices:**

| Device | VPN IP | What it can do |
|---|---|---|
| mike-pc | 100.64.1.3 | Full remote admin access to both Pis |
| tactical (Pi #2) | 100.64.1.1 | Subnet router — primary gateway to 192.168.8.0/24 |
| comms (Pi #1) | 100.64.1.2 | Subnet router — standby gateway to 192.168.8.0/24 |
| s25 (phone) | 100.64.1.4 | Field access to all node services |

**What you can do from your Android phone (S25) over VPN:**

| Task | How |
|---|---|
| **SSH into Pi #1 or Pi #2** | SSH client (Termux, ConnectBot) → `192.168.8.10` or `192.168.8.20` |
| **Open Element Web remotely** | Browser → `http://192.168.8.10:8080` |
| **Connect ATAK remotely** | ATAK → TAK Server → `192.168.8.20` port `8088` |
| **Check Monero node** | Browser or wallet → `http://100.64.1.1:18089` (Tailscale only — RPC is localhost on Pi #2, not LAN-accessible) |
| **Admin GL.iNet router** | Browser → `http://192.168.8.1` |
| **View I2P console** | Browser → `http://192.168.8.10:7070` |
| **Send MQTT messages** | Any MQTT client → `192.168.8.20:1883` |

**Key use cases:**

- **Field deployment, unattended node:** Node is left running at a location. You drive away. SSH in from your phone to check logs, restart a container, or update config — no physical access needed.
- **Remote ATAK:** Your team is dispersed. ATAK users outside the local WiFi connect their tablets to Headscale VPN and join the OpenTAK common operating picture from cellular.
- **Secure Monero wallet sync:** Point your Monero wallet to `100.64.1.1:18089` over Tailscale VPN — your transactions are verified by your own node, never a third party. (Monero RPC is localhost-only on Pi #2; use the Tailscale IP, not the LAN IP.)
- **Emergency admin:** A service goes down remotely. Pull up Termux on your phone, SSH in, and bring it back up without returning to the site.
- **No ports exposed:** Everything above happens through a single outbound WireGuard tunnel — no open attack surface beyond port 443 for the Headscale control plane.

**Connecting to VPN (phone):**

1. Open Tailscale app → tap **Connect**
2. All `192.168.8.x` addresses become reachable immediately
3. Disconnect when done — VPN does not need to run constantly

> **Field IP change:** If the node moves to a new network (cellular, Starlink), the public IP changes. Update the Cloudflare DNS A record for `m2vpn.yourdomain.com` manually until the dynamic DNS script (pending item 6) is in place.

---

### 9.2 Touchscreen Kiosk Dashboard (Pi #1)

**Hardware:** GeeekPi 2U 7.84" LCD touchscreen at U6 — HDMI-A-2 (port 0, nearest USB-C power) for display, USB-C "DC5V TOUCH" port for touch data.

> **HDMI port naming on Pi 5:** micro-HDMI port 0 (nearest USB-C power) = `HDMI-A-2` in Wayland. Port 1 = `HDMI-A-1`. Confirm with `swaymsg -t get_outputs` after compositor starts. This is counter-intuitive but consistent.

> **X11 does not work on Pi 5.** Attempts with `startx`, `xinit`, and `xorg.conf` modesetting driver all fail with "Cannot run in framebuffer mode" / "No devices detected". Pi 5 requires Wayland. Do not troubleshoot X11 — use Wayland only.

> **⚠️ CRITICAL: Line wrapping in PowerShell SSH sessions.** When you paste long config lines (especially the Chromium exec line in sway config) via a PowerShell SSH session, the terminal may visually wrap the line but nano interprets the wrap as a **real newline**, splitting the command in two. The second half becomes a separate (broken) line and the command silently loses its URL, flags, or other trailing content. **After pasting any long line into nano, press `End` key to jump to the end of the line and verify that the ENTIRE command is on ONE line.** If it's split, delete the newline to rejoin it. This applies to all long single-line commands in this guide — sway config, systemd ExecStart lines, and curl commands.

**Step 1 — Install packages**

```bash
# [SSH — Pi #1]
sudo apt install -y sway chromium xwayland foot
```

**Step 2 — Create kiosk user auto-login**

```bash
# [SSH — Pi #1]
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
```

```bash
# [SSH — Pi #1]
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ps --noclear %I $TERM
EOF
```

```bash
# [SSH — Pi #1]
sudo systemctl daemon-reload
```

**Step 3 — Create sway config**

```bash
# [SSH — Pi #1]
mkdir -p /home/pi/.config/sway
```

```bash
# [SSH — Pi #1]
tee /home/pi/.config/sway/config << 'EOF'
# ~/.config/sway/config — Community Node kiosk compositor
# Pi 5 HDMI port naming: port 0 (nearest USB-C power) = HDMI-A-2, port 1 = HDMI-A-1.
# Verify output names with: swaymsg -t get_outputs

# ── Visual chrome ─────────────────────────────────────────────────────────────
default_border none
hide_edge_borders both
bar { mode invisible }

# ── Output assignment ─────────────────────────────────────────────────────────
# HDMI-A-2 = touchscreen (Pi port 0, always present)
# HDMI-A-1 = pass-through external monitor (Pi port 1, connect on demand)
# Workspace 1 is pinned to the touchscreen. Chromium always opens here.
# Workspace 2 is pinned to HDMI-A-1. When a monitor is connected, sway
# automatically enables it and puts workspace 2 there — no restart needed.
output HDMI-A-2 enable resolution 1280x400
workspace 1 output HDMI-A-2
workspace 2 output HDMI-A-1

# ── Touch input ───────────────────────────────────────────────────────────────
# Map all touch events to the touchscreen output regardless of which output
# has focus. Without this, touch coordinates may map to the wrong display.
input type:touch map_to_output HDMI-A-2

# ── Idle / cursor ─────────────────────────────────────────────────────────────
# Hide cursor after 1 second of inactivity (kiosk — no mouse)
seat seat0 hide_cursor 1000
# Allow Ctrl+Alt+F2 to switch to tty2 for emergency text console access
seat * vt_switching enable

# ── Keybindings ───────────────────────────────────────────────────────────────
# Super+Enter = open foot terminal (appears on whichever workspace is focused)
set $mod Mod4
bindsym $mod+Return exec foot
# Super+1 / Super+2 = switch between kiosk (touchscreen) and console (external monitor)
bindsym $mod+1 workspace 1
bindsym $mod+2 workspace 2

# ── Kiosk application ────────────────────────────────────────────────────────
# Pin Chromium to workspace 1 (touchscreen) so it never migrates to HDMI-A-1
# when an external monitor is connected.
for_window [app_id="chromium"] move container to workspace 1

# --touch-events=enabled: required for tap-to-click on Wayland touchscreens.
# Sleep 45 gives Docker containers time to fully start after a cold boot before Chromium loads.
# 20s was not enough — Docker itself takes time to initialize after reboot, causing Chromium to hit
# an unresponsive nginx and fall back to the default browser page.
exec sleep 45 && swaymsg workspace 1 && chromium --kiosk --noerrdialogs --disable-infobars --no-first-run --no-sandbox --disable-dev-shm-usage --touch-events=enabled --check-for-update-interval=31536000 --ozone-platform=wayland http://localhost
EOF
```

**Step 4 — Create auto-start in `.bash_profile`**

```bash
# [SSH — Pi #1]
tee /home/pi/.bash_profile << 'EOF'
# ~/.bash_profile — Kiosk auto-start for Pi #1 (comms)
# Launches sway only on tty1 and only when not already in a Wayland session.
# SSH logins (which have no tty1) are unaffected.
if [ -z "$WAYLAND_DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    sleep 5
    exec sway
fi
EOF
```

**Step 5 — (Optional) Force HDMI hotplug detection**

If HDMI-A-2 goes blank after a power cycle, force detection:

```bash
# [SSH — Pi #1]
sudo nano /boot/firmware/config.txt
```

Add under `[all]`:
```ini
# Keep HDMI-A-2 (touchscreen, port 0) active even when no EDID is detected
hdmi_force_hotplug=1
```

Do **not** add `hdmi_force_hotplug:1=1` for HDMI-A-1 — that causes sway to span both outputs at boot even when the external monitor is unplugged.

**Step 6 — Reboot and verify**

```bash
# [SSH — Pi #1]
sudo reboot
```

After reboot, the touchscreen should show the community info page within ~25 seconds. If it shows "Site cannot be reached" briefly, wait — Docker containers may still be starting.

**To use the external monitor (on demand):**

Connect a monitor to HDMI-A-1 (Pi port 1, pass-through). Sway detects it automatically and enables workspace 2 there. Open a terminal: `Ctrl+Alt+F2` → login → `WAYLAND_DISPLAY=wayland-1 foot` (if foot is installed) or use VT switching for a text console.

**Step 7 — Set web content directory permissions**

By default, `/opt/community-node/data/community-web/` is owned by root. Set it to `ps` so the operator can deploy page updates directly via `scp` without needing sudo:

```bash
# [SSH — Pi #1]
sudo chown -R ps:ps /opt/community-node/data/community-web/
```

> Without this, `scp` to that path silently fails and the old page keeps serving. This must be run once after the directory structure is created.

---

**Kiosk troubleshooting:**

| Symptom | Cause | Fix |
|---|---|---|
| "Cannot connect to X server" | Tried X11 — won't work on Pi 5 | Use Wayland/Sway only |
| Page is stretched / distorted | Resolution set to 1920x1080 instead of native 1280x400 | Set `output HDMI-A-2 enable resolution 1280x400` in sway config |
| Touch taps don't register as clicks | Missing `--touch-events=enabled` Chromium flag | Add flag to Chromium exec line in sway config |
| Touch coordinates map to wrong location | Wrong resolution → misaligned touch grid | Fix resolution to native 1280x400 |
| Chromium appears on wrong display | Workspace not pinned | Verify `workspace 1 output HDMI-A-2` and `for_window` rule in sway config |
| SSH login launches nano/sway commands | Sway config accidentally pasted into `.bash_profile` | `ssh comms -t "bash --noprofile"` to bypass, then correct the file |
| No touch response | USB-C touch port not connected to Pi | Connect touchscreen USB-C "DC5V TOUCH" → Pi USB-A port |
| Touch on wrong screen | No `map_to_output` | Add `input type:touch map_to_output HDMI-A-2` to sway config |
| Chromium crash loop | First-run flags missing | Add `--no-first-run --disable-infobars` flags |
| Page update not showing in Chromium | Chromium has two separate cache locations | Clear BOTH: `rm -rf /home/pi/.config/chromium/Default/Cache /home/pi/.config/chromium/Default/"Code Cache" /home/pi/.cache/chromium/` |
| scp to community-web fails silently | Directory owned by root | Run `sudo chown -R ps:ps /opt/community-node/data/community-web/` once |
| Display shows "No Signal" blue screen on idle | DPMS cuts video signal — display OSD fires | Do not use DPMS/swayidle. Screen blanking is handled by JS in `index.html` navigating to `blank.html`. Signal stays live, display stays happy. |
| Blank screen doesn't return on touch | `blank.html` not deployed or wrong path | Verify `blank.html` is in `/opt/community-node/data/community-web/`. Touch listener navigates to `/` — confirm nginx serves index.html at root. |

---

### 9.4 Community Web Page — Updating Content

The community info page (`index.html`) is served by nginx at port 8081 from `/opt/community-node/data/community-web/`. The source file lives in the project repository on Windows.

> **Current version:** `community-web-index.html` v4.2 — dark theme, phone + kiosk dual mode (`?from=kiosk`), WiFi QR code, Element link, ATAK onboarding steps with app store QR codes, collapsible services section. The kiosk touchscreen dashboard is a separate file (`kiosk.html` v2.2) with tabs, live status polling, map integration, and screensaver. The requirements below capture future enhancements — the current pages are deployment-ready.

#### Redesign Requirements (capture before starting)

**Philosophy:** A user walks up with their phone. Within 10 seconds, they are connected. No typing. No confusion.

**QR Codes — one for every connection method:**
No user should ever have to type an `.onion` address or a clearnet URL. Use `qrcode.js` (client-side library, no server needed) to generate QR codes for:
- WiFi join: `WIFI:S:CommunityNode;T:WPA;P:<password>;;` — phone camera opens WiFi join dialog automatically
- Clearnet Element: `https://communitynode.yourdomain.com`
- Tor Element: `http://YOUR_ELEMENT_ONION.onion`
- Tor Matrix API: `http://YOUR_MATRIX_ONION.onion`
- Community Page (Tor): `http://YOUR_COMMUNITY_ONION.onion`
- Meshtastic channel URL (once configured)

**Tab structure:**
- **Tab 1 — Connect:** QR codes, connection steps, service list. Primary view.
- **Tab 2 — Status:** Live service health dashboard. Green/red indicators per container.

**Persistent navigation panel (both tabs):**
A fixed left or right sidebar (suits 1280x400 wide/short display) with controls visible on every tab:
- Tab 1 / Tab 2 toggle buttons
- Screensaver dismiss / wake button
- Possibly a brightness toggle or help button
- Panel should be narrow enough not to crowd content — 60–80px wide, icon-based

**JavaScript capabilities available (Chromium serves full V8 engine):**
- Full ES2023 JavaScript — no restrictions
- `fetch()` for polling local API endpoints
- WebSockets for real-time data
- CSS animations and Canvas/WebGL (GPU accelerated)
- Local Storage for persisting state

**Screensaver / idle behavior (JS-controlled — already implemented in current page):**
- Do NOT use swayidle or DPMS — cutting the video signal causes the display to show a "No Signal" blue OSD
- Current implementation: JS idle timer in `index.html` navigates to `blank.html` (pure black) after 10 minutes. Touch returns instantly. Signal stays live.
- Redesign upgrade: replace the hard navigate with a fade-to-black animation, then ambient screensaver (animated canvas, clock, node status summary) before going fully black
- Any touch at any point → instantly return to Tab 1 (connect page)

**Live status dashboard (Tab 2) — no extra containers needed:**
- Systemd timer on Pi #1 runs every 30 seconds: `docker compose ps --format json > /opt/community-node/data/community-web/status.json`
- JS fetches `http://192.168.8.10:8081/status.json` and renders live service indicators
- nginx already serves the `community-web` directory — no new ports or services required
- Show: container name, state (running/exited), uptime, last checked timestamp

**WiFi onboarding — QR code only, no WPS:**
WPS (Wi-Fi Protected Setup) has known security vulnerabilities (PIN brute-force via Reaver attack) and exposes a 2-minute open join window on Push-Button mode. Do not implement a WPS trigger button. The WiFi QR code is strictly better: same one-tap experience, no vulnerability, no timing window, works on every phone since 2018. GL.iNet has a JSON-RPC API that could trigger WPS programmatically, but this is not worth implementing.

> **NFC transmitter evaluated and cut.** A PN532 active NFC module was considered for tap-to-connect onboarding. Removed from scope — QR codes printed on the rack accomplish the same thing with zero hardware, zero software, and zero failure modes. See §2.4 for the QR code onboarding approach.

**Standard deployment workflow (Windows → Pi #1):**

**Step 1 — Edit the source file on Windows:**
```
C:\SOURCE CONTROL\M2-Community-Node\community-web-index.html
```

**Step 2 — Deploy to Pi #1:**

```powershell
# [Windows — local PowerShell]
scp "C:\SOURCE CONTROL\M2-Community-Node\community-web-index.html" comms:/opt/community-node/data/community-web/index.html
```

```powershell
# [Windows — local PowerShell]
scp "C:\SOURCE CONTROL\M2-Community-Node\blank.html" comms:/opt/community-node/data/community-web/blank.html
```

> `blank.html` must always be deployed alongside `index.html`. It is the screen blanker — a pure black page that the JS idle timer in `index.html` navigates to after 10 minutes of no touch. Touch anywhere on `blank.html` returns to the community page. The video signal stays live at all times — no DPMS, no "No Signal" OSD.

**Step 3 — Reload the kiosk on the touchscreen:**

> **Do NOT use `pkill chromium` by itself.** The sway `exec` line is a one-shot — it launches Chromium once at sway startup. Killing Chromium alone leaves sway running with no browser and no way to relaunch it. **Always kill sway instead**, which triggers the full auto-restart chain: `auto-login → .bash_profile → sway → exec chromium`.

```bash
# [SSH — Pi #1] — Clear Chromium cache first
rm -rf /home/pi/.config/chromium/Default/Cache /home/pi/.config/chromium/Default/"Code Cache" /home/pi/.cache/chromium/
```

```bash
# [SSH — Pi #1] — Restart the entire kiosk (sway + chromium)
pkill sway
```

Wait ~50 seconds for the full chain to restart (5s login delay + 45s Docker wait).

> Always clear both cache locations. Chromium stores cache in `/home/pi/.config/chromium/Default/Cache` AND `/home/pi/.cache/chromium/` — clearing only one leaves the old page visible.

**Verify nginx is serving the updated file (before blaming Chromium):**

```bash
# [SSH — Pi #1]
curl -s http://localhost:8081 | grep -i "your search term"
```

If curl returns the new content but Chromium still shows old content → clear both cache paths above.
If curl returns old content → the scp failed. Check permissions (`ls -la /opt/community-node/data/community-web/`).

---

### 9.3 SSH Configuration — Always Use Tailscale IPs

**Problem:** When Tailscale is running on Windows with subnet routes approved (`192.168.8.0/24`), Windows routes all `192.168.8.x` traffic through the VPN tunnel. If the tunnel is disrupted (power cycle, reconnect), SSH to the Pis via LAN IPs fails even when physically on the same WiFi.

**Root cause:** Tailscale takes ownership of the `192.168.8.0/24` route on the Windows routing table. Subnet routing is designed for *remote* access to LAN-bound services — not for device-to-device SSH.

**Correct solution:** Two parts working together:

1. Run Tailscale with `--accept-routes=false` on the operator Windows machine. This keeps Tailscale running (so 100.64.x.x device IPs work) but prevents Windows from taking over the `192.168.8.0/24` route. Direct WiFi access to LAN services is never disrupted.
2. SSH always via Tailscale device IPs (`100.64.x.x`) using the SSH config below.

> **[Windows — local PowerShell] — Run once, and after every Windows reboot:**
> ```powershell
> tailscale up --login-server https://m2vpn.yourdomain.com --accept-routes=false
> ```
> The message `Some peers are advertising routes but --accept-routes is false` is expected — not an error.

> **Tailscale must be running** for `ssh comms` / `ssh tactical` to work. If Tailscale is off, use the `-lan` fallback hosts (`ssh comms-lan`, `ssh tactical-lan`) which connect directly via LAN IP.
>
> **⚠️ Commercial VPN (Proton/Mullvad) + Tailscale conflict:** Proton VPN and Tailscale cannot run simultaneously on Windows — both use WireGuard TUN interfaces that conflict at the kernel routing table, DNS, and Windows Filtering Platform firewall level. Split tunneling does not fix this (confirmed). **When Proton VPN is active, run `tailscale down` and use `ssh comms-lan` / `ssh tactical-lan` for SSH.** When Proton is off, use `tailscale up` and `ssh comms` / `ssh tactical`. This is a temporary workflow until the M1 VPN Exit Node is built (see pending item 13), which eliminates the conflict permanently by running Mullvad on the TRIGKEY G5 as a Tailscale exit node.

**Remote access (when NOT on CommunityNode WiFi):** SSH still works identically via 100.64.x.x. If you also need browser access to LAN services (`192.168.8.10:8080`, etc.) from a remote network, temporarily enable routes:
```powershell
tailscale up --login-server https://m2vpn.yourdomain.com --accept-routes=true
```
Then revert to `--accept-routes=false` when back on the local network.

> 📋 **TROUBLESHOOTING CARD CANDIDATE** — Remote Access Scenario (plain language):
>
> **Situation:** You're away from the node (coffee shop, another site, cellular) and want to access community services in your browser — like the Matrix chat at `http://192.168.8.10:8080`.
>
> **Step 1 — Enable remote routing** `[Windows — local PowerShell]`:
> ```powershell
> tailscale up --login-server https://m2vpn.yourdomain.com --accept-routes=true
> ```
> Now your laptop can reach `192.168.8.x` addresses as if you were sitting next to the rack. SSH (`ssh comms`, `ssh tactical`) continues to work unchanged.
>
> **Step 2 — When you return to CommunityNode WiFi, switch back** `[Windows — local PowerShell]`:
> ```powershell
> tailscale up --login-server https://m2vpn.yourdomain.com --accept-routes=false
> ```
> This prevents a routing conflict where Tailscale and your local WiFi fight over the same addresses.
>
> **Rule of thumb:** `--accept-routes=false` at home. `--accept-routes=true` when remote and needing LAN services.

Create or update your SSH config (`C:\Users\YOUR_USERNAME\.ssh\config` on Windows, `~/.ssh/config` on Linux/macOS):

```
# Always connect to the Pis via Tailscale device IPs (100.64.x.x).
# Works identically whether physically on CommunityNode WiFi or remote.
# Tailscale device IPs bypass subnet routing entirely — they are never affected
# by tunnel disruption because they use direct peer-to-peer WireGuard paths.

Host comms
    HostName 100.64.1.2
    User ps

Host tactical
    HostName 100.64.1.1
    User ps

# Fallback: direct LAN (use only when Tailscale is fully stopped)
Host comms-lan
    HostName 192.168.8.10
    User ps

Host tactical-lan
    HostName 192.168.8.20
    User ps
```

Usage: `ssh comms` and `ssh tactical` — works from anywhere.

> **Subnet routing stays enabled.** This is still needed so devices connected to Headscale VPN can reach LAN-bound services (Matrix at 192.168.8.10:8080, ATAK at 192.168.8.20:8088, etc.). The SSH config change only affects how your Windows machine initiates SSH sessions.

---

### Service URLs (on local WiFi)

| Service | URL | Notes |
|---|---|---|
| Element Web (Matrix client) | `http://192.168.8.10:8080` | LAN/WiFi access |
| Community Info Page | `http://192.168.8.10:8081` | LAN/WiFi access |
| Matrix server (API via Nginx) | `http://192.168.8.10` | LAN clients use this as homeserver |
| Matrix server (direct, Pi only) | `http://127.0.0.1:6167` | Admin use from Pi #1 only |
| I2P web console | `http://192.168.8.10:7070` | |
| OpenTAK Web UI | `http://192.168.8.20:8080` | Live map, cert management |
| ATAK CoT endpoint | `192.168.8.20:8088` (TCP) | Configure in ATAK app |
| Monero RPC (restricted) | `http://127.0.0.1:18089` | Localhost/Tailscale only — not LAN-accessible |
| Monero Wallet RPC | `http://127.0.0.1:18083` | SSH tunnel only — operator use |
| Mosquitto MQTT | `192.168.8.20:1883` | |
| GL.iNet admin | `http://192.168.8.1` | |
| **Tor — Community Page** | `YOUR_COMMUNITY_ONION.onion` | Tor Browser required |
| **Tor — Element Web** | `YOUR_ELEMENT_ONION.onion` | Tor Browser required |
| **Tor — Matrix API** | `YOUR_MATRIX_ONION.onion` | Homeserver for Tor clients |
| **Clearnet — Element Web** | `https://communitynode.yourdomain.com` | Via Cloudflare Tunnel |
| **Clearnet — Matrix API** | `https://m2-matrix.yourdomain.com` | Via Cloudflare Tunnel |

### Key File Locations

| File | Path |
|---|---|
| Node #1 compose | `/opt/community-node/docker-compose.yml` |
| Node #2 compose | `/opt/tactical-node/docker-compose.yml` |
| Conduit config | `/opt/community-node/config/conduit/conduit.toml` |
| Reticulum config | `/opt/tactical-node/data/reticulum/config` |
| Tor onion keys | `/opt/community-node/data/tor/` |
| Monero blockchain | `/mnt/nvme/monero/data/` |

### Port Reference

| Port | Service | Node |
|---|---|---|
| 80, 443, 8448 | Nginx (Matrix federation) | #1 |
| 6167 | Conduit (internal) | #1 |
| 8080 | Nginx (Element Web client) | #1 |
| 8081 | Nginx (Community info page) | #1 |
| 4444, 4447 | I2P proxies | #1 |
| 7070 | I2P web console | #1 |
| 9050 | Tor SOCKS | #1 |
| 18080, 18089 | Monero p2p / RPC | #2 |
| 18083 | Monero Wallet RPC (loopback only) | #2 |
| 8080 | OpenTAK Server Web UI (HTTP) | #2 |
| 8088 | OpenTAK Server CoT (TCP) | #2 |
| 8089 | OpenTAK Server CoT (SSL) | #2 |
| 8443 | OpenTAK Server Web UI (HTTPS) | #2 |
| 8446 | OpenTAK Certificate Enrollment | #2 |
| 64738 | Mumble voice server | #2 |
| 4242, 37428 | Reticulum TCP / shared | #2 |
| 1883, 9001 | Mosquitto MQTT | #2 |
| 443, 50443 | Headscale VPN | #2 |

### Emergency Contacts (fill in before deployment)

| Role | Contact Method |
|---|---|
| M1 home base WireGuard | `10.0.0.x` (fill in after M1 build) |
| Matrix admin account | `@admin:m2.yourdomain.com` |
| Monero wallet RPC | `http://127.0.0.1:18083` via SSH tunnel — `ssh -L 18083:localhost:18083 tactical` |

### Hardware Summary (Recommended Build)

| Component | Item | Price | Notes |
|---|---|---|---|
| Compute × 2 | Raspberry Pi 5 16GB | $205 ea | Both nodes; PiShop.us confirmed Feb 2026 |
| Cooler × 2 | Pi 5 Active Cooler | $10.95 ea | PiShop.us confirmed |
| Pi mount + NVMe | GeeekPi 1U Dual Pi 5 Mount (B0F7XBVV4D) | ~$60 | Both Pi 5s in 1U; built-in PCIe NVMe adapters |
| Storage Pi #1 | WD SN740 256GB M.2 2230 OEM (B0C6MVP42M) | ~$40 | Official Pi SSD 256GB OUT OF STOCK Feb 2026 |
| Storage Pi #2 | Crucial P310 1TB M.2 2230 (CT1000P310SSD2) | ~$115–150 | Official Pi SSD 1TB OUT OF STOCK Feb 2026 |
| Chassis | GeeekPi RackMate T1 8U (B0CPLRD29P) | $119.99 | SOLD OUT DeskPi; check Amazon |
| Switch | TP-Link TL-SG108S (unmanaged) | ~$27 | |
| Router | GL.iNet Slate AX (AXT1800) | $119.99 | GL.iNet store confirmed |
| PDU | Tupavco TP1713 1U Rack PDU | ~$35 | 4-outlet, surge |
| UPS | Tripp Lite BC600R (600VA/300W) | ~$70 | U1 inside rack; PDU on rear rails at U2 |
| Touchscreen | GeeekPi 2U 7.84" LCD (B0F3C5R2BZ) | $79.99 | SOLD OUT DeskPi; check Amazon |
| Fan | 120mm USB exhaust fan × 2 | ~$26 | U8 top + push-pull |
| LoRa radio 1 (LEFT) | Heltec WiFi LoRa 32 V3 915MHz | $19.90 | RNode/Reticulum — LEFT panel position, ANT 1 |
| LoRa radio 2 (RIGHT) | Heltec WiFi LoRa 32 V3 915MHz | $19.90 | Meshtastic — RIGHT panel position, ANT 2 |
| Antennas | 915 MHz SMA × 2 | ~$12 | ⚠️ Must be SMA male (NOT RP-SMA) |
| GaN Charger | Anker 747 GaNPrime 150W (B09W2PNLX7) | ~$65 | C1→Pi#1, C2→Pi#2, C3→GL.iNet, USB-A→display; 1 PDU outlet |
| Cables + media | microSD × 2, patch cables, USB-C × 3, USB-A × 2 | ~$45 | See BOM items 20–23a |
| LoRa panel | Custom 1U LoRa Panel with OLED windows (3D print) | ~$2 | Black PETG; boards mount on panel with M2 standoffs |
| SMA bulkheads | SMA female panel-mount connectors × 2 | ~$8 | |
| U.FL pigtails | U.FL-to-SMA-male, 6" × 2 | ~$8 | Board U.FL → panel bulkhead (direct, no jumper) |
| M2 standoffs | M2 × 8mm nylon standoffs + screws, 20-pack | ~$3 | 4 per board = 8 used |
| Fan panel | LabStack 2U Mini 2x 80mm Fan Panel (3D print) | ~$2 | github.com/JaredC01/LabStack; U4-U3 rear |
| Rear fans | 80mm USB 5V fans × 2 (GDSTIME / ELUTENG) | ~$15 | |
| **Total** | | **~$1,385–$1,425** | ⚠️ Verify SSD prices before ordering — 2230 NVMe market volatile |

**Removed from earlier BOM revisions:**
- ~~M.2 HAT+ ($12)~~ — replaced by GeeekPi dual mount's built-in NVMe adapter
- ~~Crucial BX500 1TB USB SATA ($123.99) + SABRENT adapter ($10)~~ — replaced by Crucial P310 1TB NVMe via dual mount
- ~~2× GeeekPi 1U SBC shelves ($34)~~ — replaced by 1U dual mount
- ~~CyberPower CP685AVRG ($108.95)~~ — replaced by Tripp Lite BC600R
- ~~Powered USB hub ($15)~~ — Pi #2's 2× USB 3.0 ports connect radios directly

---

*Cross-reference: MASTER_PLAN.md · HARDWARE_BOM.md · M2_SecureComms_Matrix_I2P_Tor.md · MONERO_NODE.md · ATAK_RETICULUM_MESH.md*

---

## 13. Field Operations: Power Cycle Procedure

Full shutdown and startup procedure for the Community Node. Use this checklist after any power loss, planned maintenance, or field relocation.

### 13.1 Pre-Shutdown Verification

Before powering down, confirm current state so you know what "healthy" looks like:

```
# [SSH — Pi #1 comms-lan]
docker ps --format "table {{.Names}}\t{{.Status}}"
```

```
# [SSH — Pi #2 tactical-lan]
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Record which containers show `(healthy)` and how many are running. Pi #1 should have 6 containers (nginx, element-web, cloudflared, i2pd, tor, conduit). Pi #2 should have 5 Docker containers (monerod, nomadnet, reticulum, mosquitto, headscale) plus OpenTAK Server running under systemd (`systemctl is-active opentakserver`).

### 13.2 Shutdown Order

Power down in this sequence to avoid filesystem corruption on NVMe:

1. **Pi #1 (comms):** `sudo shutdown -h now`
2. **Pi #2 (tactical):** `sudo shutdown -h now`
3. **Wait 15 seconds** for both Pis to fully halt (green LED off, no disk activity)
4. **GL.iNet router:** Power off (unplug USB-C from Anker 747)
5. **Anker 747 charger:** Unplug from PDU or wall
6. **UPS (Tripp Lite BC600R):** Press power button to disable battery output (if relocating)

> Do NOT yank power from the Pis while they are running. NVMe corruption risk is real.

### 13.3 Startup Order

Power up in this sequence. The router must be fully online before the Pis boot — Docker services need network connectivity during initialization.

1. **UPS:** Press power button to enable battery output (if it was disabled)
2. **Anker 747 charger:** Plug into PDU / wall outlet
3. **GL.iNet router:** Plug USB-C into Anker 747 port C3
4. **Wait 60 seconds** — router needs time to initialize WiFi, DHCP, DNS, and guest network. The AP isolation fix scripts run at 15s and 30s post-boot.
5. **Pi #1 (comms):** Power will flow automatically from Anker 747 port C1. If using a physical switch on the Pi, toggle it now.
6. **Pi #2 (tactical):** Power flows from Anker 747 port C2. Same as above.
7. **Wait 90 seconds** — both Pis need time to boot, mount NVMe, start Docker, and bring all containers to healthy state.

### 13.4 Post-Boot Verification Checklist

Run these checks in order. Each must pass before moving to the next.

#### Step 1: Network Connectivity

```
# [SSH — Pi #1 comms-lan]
ping -c 2 192.168.8.1
```

```
# [SSH — Pi #2 tactical-lan]
ping -c 2 192.168.8.1
```

If either Pi cannot reach the router, wait another 30 seconds and retry. If still failing, check Ethernet cables and router DHCP leases.

#### Step 2: Docker Containers — Pi #1

```
# [SSH — Pi #1 comms-lan]
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected: 6 containers, all `Up`. `element-web` and `tor` should show `(healthy)` within 2 minutes.

If any container is missing or restarting:

```
# [SSH — Pi #1 comms-lan]
docker compose -f /opt/community-node/docker-compose.yml up -d
```

#### Step 3: Docker Containers — Pi #2

```
# [SSH — Pi #2 tactical-lan]
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected: 6 containers, all `Up`. `monerod` should show `(healthy)` within 5 minutes (it runs a sync check).

If any container is missing or restarting:

```
# [SSH — Pi #2 tactical-lan]
docker compose -f /opt/community-node/docker-compose.yml up -d
```

#### Step 4: NVMe Health

```
# [SSH — Pi #1 comms-lan]
df -h /opt/community-node
```

```
# [SSH — Pi #2 tactical-lan]
df -h /opt/community-node
```

Confirm both NVMe drives are mounted and not at 100% usage.

#### Step 5: Clearnet Connectivity

```
# [SSH — Pi #1 comms-lan]
curl -s -o /dev/null -w "%{http_code}" https://communitynode.yourdomain.com
```

Expected: `200`. If not, check cloudflared container logs:

```
# [SSH — Pi #1 comms-lan]
docker logs --tail 20 comms-node-cloudflared-1
```

#### Step 6: DDNS Record

```
# [SSH — Pi #2 tactical-lan]
sudo /usr/local/bin/ddns-update.sh
```

Check output confirms IP matches or was updated successfully.

#### Step 7: Headscale VPN

```
# [SSH — Pi #2 tactical-lan]
sudo docker exec tactical-node-headscale-1 headscale nodes list
```

Confirm your devices appear. If the node itself shows `offline`, check the Headscale container logs.

#### Step 8: Monero Sync Status

```
# [SSH — Pi #2 tactical-lan]
sudo docker exec tactical-node-monerod-1 monerod status
```

Check sync height matches network height. After a power cycle, the daemon may need several minutes to catch up.

#### Step 9: Kiosk Touchscreen

The kiosk (Pi #1) auto-launches Chromium in sway after a 45-second delay on boot. Verify:
- Touchscreen displays the kiosk dashboard
- Status tab shows green dots for all services
- Touch interaction works (tap an action card)

**If the kiosk screen is blank or shows the sway bar only:** Wait the full 45 seconds. If still not showing, reboot Pi #1 — Chromium cannot be relaunched from SSH on sway/Wayland (segfaults without GPU context).

```
# [SSH — Pi #1 comms-lan]
sudo reboot
```

#### Step 10: Guest WiFi Verification

Connect a phone to `CommunityNode` WiFi. Confirm:
- Phone receives a `192.168.9.x` IP address (guest subnet — this is correct)
- `http://192.168.8.10:8080` loads Element Web (guest→LAN firewall rule)
- `http://192.168.8.10:8081` loads the community info page

If guest cannot reach LAN services, verify UCI firewall rules survived the reboot:

```
# [SSH — root@192.168.8.1 (GL.iNet router)]
uci show firewall | grep guest_element
```

If no output, the rules were lost. Re-apply from `guest-firewall-rules.sh` in this repo.

---

### 13.4.1 Guest Firewall Rules — Initial Setup

This must be run once after the GL.iNet guest network is first configured. The `guest-firewall-rules.sh` script referenced in recovery (§13.4) implements the following policy:

- **AP isolation:** Guest WiFi clients cannot communicate with each other (prevents lateral movement between visitor devices)
- **Block guest → LAN:** Guests cannot reach internal services except the explicit allowlist below
- **Allow guest → Pi #1 ports 8080 and 8081:** Element Web and community info page are intentionally reachable from guest WiFi — this is the primary use case
- **Allow guest → WAN:** Guests have normal internet access

**[SSH — root@GL.iNet router (192.168.8.1)]**

Apply the rules via UCI (persists across reboots):

```
uci set firewall.guest_element=rule
```

```
uci set firewall.guest_element.name="Allow Guest to Element Web"
```

```
uci set firewall.guest_element.src="guest"
```

```
uci set firewall.guest_element.dest="lan"
```

```
uci set firewall.guest_element.dest_ip="192.168.8.10"
```

```
uci set firewall.guest_element.dest_port="8080 8081"
```

```
uci set firewall.guest_element.proto="tcp"
```

```
uci set firewall.guest_element.target="ACCEPT"
```

```
uci commit firewall && /etc/init.d/firewall restart
```

Verify the rule is present:

```
uci show firewall | grep guest_element
```

Expected: several lines showing the rule entries above.

Verify guest can reach Element Web: connect a phone to `CommunityNode` WiFi, browse to `http://192.168.8.10:8080` — Element Web should load. Then confirm the phone cannot reach `http://192.168.8.20:8080` (OTS) or `http://192.168.8.1` (router admin) — those requests should time out.

> If the GL.iNet guest network is on a different subnet (e.g. `192.168.9.x` rather than `192.168.8.x`), the `src="guest"` zone name must match what the GL.iNet firmware assigned. Check with `uci show firewall | grep zone` to confirm zone names.

### 13.5 Known Boot Timing Issues

| Issue | Cause | Resolution |
|---|---|---|
| Chromium not launching after boot | sway config has 45s delay before launching Chromium | Wait 45+ seconds; if still blank, reboot Pi #1 |
| Chromium cannot be relaunched from SSH | Wayland/sway GPU context not available to SSH sessions | Reboot Pi #1 — there is no SSH workaround |
| Guest WiFi not reaching LAN services | Router not fully initialized; AP isolation scripts run at 15s and 30s | Wait 60 seconds after router power-on before testing |
| Docker containers not healthy immediately | Health checks have intervals (30s–120s depending on service) | Wait 2–5 minutes; check with `docker ps` |
| Monero daemon shows low sync % | Daemon catches up from last saved block after restart | Normal — wait for sync to reach 100% (minutes to hours depending on downtime) |
| Cloudflared tunnel not connecting | Router DNS not ready when container started | Restart: `docker restart comms-node-cloudflared-1` |

### 13.6 Quick Power Cycle (No Relocation)

For a simple rack reboot without disconnecting anything:

1. SSH to both Pis: `sudo shutdown -h now`
2. Wait 15 seconds
3. Unplug Anker 747 from wall for 5 seconds, plug back in
4. Wait 60 seconds (router boot)
5. Wait 90 more seconds (Pi boot + Docker)
6. Run Steps 1–10 from §13.4

---

## PENDING: Post-Deployment Configuration Sessions

The following items are deferred until after integration testing and documentation are complete. Address these in order during the next configuration session.

| # | Topic | Notes |
|---|---|---|
| 1 | ~~**Monero Wallet RPC**~~ ✅ | Documented in §5.3.3. Wallet file created, systemd service configured, SSH tunnel access documented. Community member Option A (node as daemon) also documented. |
| 2 | ~~**Headscale Dynamic DNS**~~ ✅ | Documented in §5.3.4. Script at `/usr/local/bin/ddns-update.sh`, systemd timer fires every 5 minutes, Cloudflare API auto-updates A record on IP change. |
| 3 | ~~**Headscale auth key rotation**~~ ✅ | Admin auth key expires 2026-06-04 (90 days from issue). Generate a new key with `headscale preauthkeys create --user 1 --expiration 90d --reusable` and re-login on any devices that need re-registration. Already-connected devices are unaffected. **Set a calendar reminder.** To create a recurring .ics reminder: open Notepad, paste the ICS block below, save as `headscale-key-rotation.ics` (File → Save As → All Files), then import into your calendar app (Proton Calendar: Settings → Import). Replace `YOUR-EXPIRY-DATE` with your actual date in `YYYYMMDD` format. Do not use PowerShell here-strings for this — paste into Notepad directly to avoid formatting issues.<br><br>ICS template (no auth keys — fill in date only):<br>`BEGIN:VCALENDAR`<br>`VERSION:2.0`<br>`BEGIN:VEVENT`<br>`DTSTART;TZID=America/New_York:YOUR-EXPIRY-DATET090000`<br>`SUMMARY:Headscale Auth Key Rotation - Community Node`<br>`DESCRIPTION:SSH Pi 2 and run: sudo docker exec tactical-node-headscale-1 headscale preauthkeys create --user 1 --expiration 90d --reusable`<br>`RRULE:FREQ=DAILY;INTERVAL=90;COUNT=10`<br>`BEGIN:VALARM`<br>`TRIGGER:-P7D`<br>`ACTION:DISPLAY`<br>`DESCRIPTION:Headscale key rotation in 7 days`<br>`END:VALARM`<br>`END:VEVENT`<br>`END:VCALENDAR` |
| 4 | **Element Administration** | Room structure, bot integration, member onboarding flow, encrypted vs. unencrypted room policy, registration token workflow, moderation tools. Operator has specific ideas — start fresh session to work through all of them. |
| 5 | ~~**Headscale — Register Home Assistant**~~ → M1 | Moved to M1 project — not required for M2 community node operation. |
| 6a | ~~**Kiosk Dashboard (touchscreen)**~~ ✅ | 4-tab dashboard (Status, Actions, Network, Settings) deployed on 7.84" touchscreen. Live status polling via `generate-status.py` cron job → `status.json`. All 14 services monitored (Docker + systemd across both Pis via SSH). Vitals: uptime, public IP, DDNS match, Headscale peers, Monero sync %, NVMe disk, CPU temp, RAM. Research-backed field/kiosk color palette. Settings persist via localStorage. Tested: all dots green/red transitions verified, Pi #2 unreachable degradation confirmed. |
| 6b | ~~**Community Web Page (public)**~~ ✅ | v5.0 deployed. Two tabs (Connect + Status). Live status polling via status.json. WiFi QR, Element link, ATAK onboarding, app QR codes, service grid. Visitor onboarding via QR codes on rack (WiFi QR + Community Page QR). Captive portal evaluated and removed — Android WebView auto-dismiss is unfixable by design. |
| 7 | **Email for yourdomain.com** | Set up email forwarding or a lightweight mail solution so that yourdomain.com can send and receive email. Needed for Let's Encrypt renewal notices, Matrix notifications, and general operator contact. Options to evaluate: Cloudflare Email Routing (free, forward to personal inbox), ImprovMX, or self-hosted (Maddy / Stalwart). Cloudflare Email Routing is the fastest path — zero infrastructure, just DNS records. |
| 8 | **Field Troubleshooting Cards** | Laminated quick-reference cards for field operators covering each service, common failure modes, and recovery steps. Access cheat sheet (WiFi / Clearnet / Tor) is documented in §12 Quick Reference. Ready to lay out and produce. Include: Headscale auth key rotation procedure + expiry date (first expiry: 2026-06-04). Include remote access scenario (--accept-routes toggle). **MUST include boot timing note: after any power cycle or router reboot, wait 60 seconds before testing connectivity — AP isolation fix scripts run at 15s and 30s post-boot.** All credentials referenced from `M2_SECRETS.md` (local only, gitignored). A blank template (`M2_SECRETS.template.md`) is tracked in the repo — copy to `M2_SECRETS.md`, fill in actual values, print and laminate for field use. **NEVER commit the filled secrets file.** |
| 9 | ~~**NFC Add-On (Phase 10)**~~ | Evaluated and cut. QR codes on the rack accomplish the same onboarding with zero hardware/software. See §2.4 and §9.4. |
| 10 | **Monero Mining Research** | Explore Monero (RandomX) mining on spare x86 hardware. RandomX is CPU-optimized and ASIC-resistant by design — spare desktop/laptop CPUs are viable. Research: XMRig setup, pool vs. solo mining, realistic yield estimates for available hardware, power cost vs. reward math, pointing mined rewards to community node wallet address. |
| 11 | **Power-On Self-Test (POST) Process** | Build a robust automated POST script that runs after every boot on both nodes. Should verify: all Docker containers running, all systemd services active, NVMe mounted, network connectivity (LAN + clearnet), DNS resolution, Headscale connectivity, DDNS record matches current IP, Monero daemon synced, wallet-rpc responsive, nginx serving community page. Log results to `/var/log/community-post.log`. Alert mechanism TBD (Matrix notification, LED, or touchscreen indicator). |
| 12 | **Field Laptop Testing (Linux)** | Set up a Linux laptop as the field operator workstation. Test full SSH connectivity to both nodes, Tailscale/Headscale enrollment, wallet-rpc tunnel access, scp deployment workflow, and all troubleshooting procedures from a Linux terminal. Document any command differences from the Windows/PowerShell workflow. Build a field-test checklist that validates every service end-to-end from the laptop. |
| 13 | **VPN Exit Node (M1 — Mullvad)** → M1 | Proton/Mullvad VPN cannot coexist with Tailscale on the same Windows machine — dual WireGuard TUN interfaces conflict at the kernel routing table, DNS, and firewall rule level. Split tunneling does not fix this. **Correct solution:** Run VPN client (Gluetun container + Mullvad) on the M1 TRIGKEY G5, advertise it as a Tailscale exit node. Windows runs only Tailscale — all internet traffic routes through the TRIGKEY exit node → Mullvad tunnel. Zero conflict, any Tailscale device can opt in. Implement during M1 Phase 5 (TRIGKEY Docker). |
| 16 | **Adversarial Security Audit (Red/Blue Team)** | Spin up two independent Claude agents completely divorced from this repo. **Red Team agent:** Given only the node's external attack surface (IP ranges, exposed ports, service versions, network topology from MASTER plan), attempt to identify every exploitable weakness — open ports, default credentials, unpatched CVEs, lateral movement paths, privilege escalation, Docker escapes, WiFi attacks, guest→LAN pivots, Tor/I2P deanonymization risks, Headscale trust boundaries, Monero RPC abuse, NFC relay attacks, physical access vectors. **Blue Team agent:** Given the full architecture docs, harden every finding — firewall rules, fail2ban, SSH hardening, container isolation (read-only rootfs, no-new-privileges, seccomp), network segmentation, log monitoring, intrusion detection, credential rotation policy, physical tamper detection. Agents should be adversarial — Red Team tries to break what Blue Team fixes. Output: consolidated security report with findings ranked by severity (Critical/High/Medium/Low), remediation steps, and a hardened configuration checklist. Run this BEFORE any public deployment. |

---

## 14. Tech Verification Checklist

Run this checklist before every event. It verifies the full comms and tactical data stack end-to-end from the perspective of a tech standing at the rack. Complete all steps in order — each step validates a dependency for the next.

**Equipment needed:** Android device with ATAK-CIV installed, connected to `CommunityNode` WiFi.

---

### 14.0 Pre-CCC26 Checklist (Hard Deadline: June 5, 2026)

The node must be fully tested, secured, and packed before **June 5** (departure day). The node will be offline and in transit June 5–13. CCC26 event is June 13–14 in Florence, SC.

Complete all items in this section before packing the rack.

- [ ] **Rotate Headscale auth key** — current key created ~March 7, 2026 with `--expiration 90d` expires June 4. Rotate by June 1 to avoid expiry while in transit. Run on Pi #2: `sudo docker exec tactical-node-headscale-1 headscale preauthkeys create --user 1 --expiration 90d --reusable`
- [ ] **Verify Let's Encrypt cert auto-renewal** — certs issued ~March 2026 expire ~June 2026 (90-day). Run `sudo certbot renew --dry-run` on both Pi #1 and Pi #2. If less than 30 days remain, force-renew: `sudo certbot renew --force-renewal`
- [ ] **Refresh FL PMTiles extract** — current extract may be months old by June. Re-run the extract command from §5B Step 7 to pull an updated Protomaps build before the event
- [x] **Design and deploy community web page content** — v5.0 deployed (Connect + Status tabs, live health dashboard). QR code stickers for rack sides generated.
- [ ] Run full Tech Verification Checklist (§14.1 through §14.5) with all results passing
- [ ] Config backup current and stored offsite (§8.1)
- [ ] UPS at 100% charge
- [ ] All cables velcro-tied, nothing loose
- [ ] Antennas unscrewed and stored in case foam

> **Transit note:** Node will be offline June 5–13. Any time-sensitive auth tokens or certs that expire during that window will need manual renewal on arrival before the node is operational.

---

---

### 14.1 Server Health

Confirm all four OTS services and supporting infrastructure are running before any EUD testing.

**Step 1 — OTS services:**

```
# [SSH — tactical-lan]
systemctl is-active opentakserver eud_handler eud_handler_ssl cot_parser
```

Expected: four lines, all `active`. If `cot_parser` shows `inactive` or `dead`, restart it:

```
# [SSH — tactical-lan]
sudo systemctl restart cot_parser && systemctl is-active cot_parser
```

> `cot_parser` is the process that stores EUD positions and relays CoT to the web map. Without it, EUDs can connect but positions are silently dropped. It exits cleanly on crash (code 0), so systemd's on-failure restart does not trigger — check it manually after any power cycle.

**Step 2 — RabbitMQ queue:**

```
# [SSH — tactical-lan]
sudo rabbitmqctl list_queues name consumers 2>/dev/null
```

Expected: a `cot_parser` queue with `1` consumer. If the queue is missing, `cot_parser` is not running even if systemd says active — restart it.

**Step 3 — Offline tile server:**

```
# [SSH — tactical-lan]
curl -s -o /dev/null -w "%{http_code}" -r 0-1023 http://127.0.0.1:8080/tiles/florida.pmtiles
```

Expected: `206` (partial content — byte-range request working). If `404`, nginx is not serving tiles. Check `/etc/nginx/sites-enabled/ots_http` and confirm `/mnt/nvme/tiles/florida.pmtiles` exists.

**Step 4 — Community Node marker cron:**

```
# [SSH — tactical-lan]
crontab -l | grep push_node_marker
```

Expected: two lines (every 4 hours + @reboot). If missing, re-add from §14.4.

---

### 14.2 EUD Connection and Position Sharing

Verify an ATAK device can connect, send position, and appear on the kiosk map.

**Step 1 — Push the Community Node marker:**

```
# [SSH — tactical-lan]
python3 /home/pi/ots/push_node_marker.py
```

Expected: `Marker pushed at <timestamp>`. This ensures any device that connects will see the node immediately.

**Step 2 — Connect ATAK to the server:**

On the Android device:
1. Open ATAK → Settings (gear icon) → Network Preferences → Network Connection Preferences → TAK Servers
2. Confirm server entry: `192.168.8.20`, port `8088`, protocol `TCP`
3. **"Use default SSL/TLS certificates" must be UNCHECKED** — this is a plaintext TCP connection. ATAK sometimes re-enables this checkbox automatically. If checked, ATAK sends a TLS handshake instead of CoT XML and OTS receives zero data (connection shows "No Data" after timeout). If the server shows connected but the device never appears on the map, this checkbox is the first thing to check.
4. Enabled checkbox must be checked. If it was previously connected, toggle it off then back on to force a fresh connection.

**Step 3 — Confirm server sees the connection:**

```
# [SSH — tactical-lan]
tail -5 /home/pi/ots/logs/opentakserver.log
```

Expected: `New TCP connection from 192.168.9.x` within 5 seconds of enabling in ATAK.

**Step 4 — Confirm position is stored:**

Wait 30–60 seconds for ATAK to send its first SA report, then:

```
# [SSH — tactical-lan]
sudo -u postgres psql -d ots -c "SELECT callsign, latitude, longitude, timestamp FROM euds JOIN points ON euds.uid = points.device_uid ORDER BY points.id DESC LIMIT 5;"
```

Expected: the ATAK device's callsign with a valid lat/lon and a recent timestamp. If the row is missing after 60 seconds, `cot_parser` is not consuming — repeat §14.1 Step 1.

**Step 5 — Confirm device appears on kiosk:**

On the kiosk touchscreen (or browse to `http://192.168.8.20:8080`):
- Open the OTS web map
- The EUD icon for the connected device should appear at its GPS location

**Step 6 — Confirm Community Node marker appears on ATAK:**

On the ATAK device, zoom to the node's location (lat 28.5565, lon -81.1551). You should see the green "Community Node" HQ marker. If not visible, re-run §14.2 Step 1 — the marker may have staled since the last cron run.

---

### 14.3 DTED2 Elevation Data

Verify the elevation data package delivers to a connected EUD automatically.

**Step 1 — Confirm the package is uploaded and flagged for auto-install:**

```
# [SSH — tactical-lan]
curl -s -b /tmp/ots_cookies -X POST "http://127.0.0.1:8080/api/login" -d "username=administrator&password=YOUR_OTS_ADMIN_PASSWORD" -o /dev/null 2>/dev/null && curl -s -b /tmp/ots_cookies "http://127.0.0.1:8080/api/data_packages" 2>/dev/null | python3 -c "import sys,json; [print(p['filename'], 'auto-install:', p.get('install_on_connection')) for p in json.load(sys.stdin).get('results',[])]"
```

Expected: `FL_DTED2.zip` listed with `auto-install: True`. If the package is missing, rebuild it from §7 (Copernicus DTED pipeline).

**Step 2 — Verify EUD receives the package:**

When an EUD connects (or reconnects) to OTS, it should receive a data package notification in ATAK within 30–60 seconds. The device will show a dialog: "Accept data package FL_DTED2.zip?" — tap Accept. ATAK auto-imports it to `/sdcard/atak/DTED/`.

**Step 3 — Verify elevation on the EUD:**

On ATAK with the package imported:
1. Long-press any point on the map → tap the coordinate display at top
2. Elevation shown should read a realistic value for the area (Florida: 0–100 ft MSL)
3. Alternatively: draw an elevation profile line across the map — it should render with terrain data rather than a flat line

> On flat terrain like Florida, use the "Red X" tool: tap the map at any point, select "Red X", the popup shows elevation in feet MSL with the source (`DTED2`). A value of 0 MSL at the coastline and 20–80 ft inland confirms DTED2 is active.

---

### 14.4 Offline Maps (Kiosk)

Verify the kiosk map loads from local tile storage, not the internet.

**Step 1 — Confirm tiles are served with byte-range support:**

```
# [SSH — tactical-lan]
curl -s -o /dev/null -w "Status: %{http_code}, Size: %{size_download} bytes\n" -r 0-4095 http://127.0.0.1:8080/tiles/florida.pmtiles
```

Expected: `Status: 206, Size: 4096 bytes`. Any other status means byte-range is broken — PMTiles will not render.

**Step 2 — Visual check on kiosk:**

Open the kiosk location picker (or browse to `http://192.168.8.20:8080/kiosk-map.html` from LAN):
- The map should render as a dark vector map (Protomaps dark theme)
- Zoom to Florida — roads, labels, and water features should be visible
- If the map shows a blank grey background with the OSM raster fallback, protomaps-leaflet failed to load — check `/var/www/html/opentakserver/kiosk-assets/protomaps-leaflet.js` exists on tactical Pi

**Step 3 — Confirm offline behavior:**

Disconnect the tactical Pi from the internet (unplug WAN cable or disable GL.iNet uplink) and reload the kiosk map. The map must still render fully — it is pulling from `/mnt/nvme/tiles/florida.pmtiles` on the local NVMe, not from any CDN.

---

### 14.5 Communications Stack

**Matrix/Element:**

1. From a device on `CommunityNode` WiFi, browse to `http://192.168.8.10:8080`
2. Log in or register a new account
3. Send a message in any room — confirm it delivers
4. From a second device (or incognito window), log in as a different user — confirm the message is visible

**Monero Node:**

```
# [SSH — tactical-lan]
sudo docker exec tactical-node-monerod-1 monerod status
```

Expected: sync percentage at or near 100%, block height matches network. The restricted RPC is bound to `127.0.0.1` on Pi #2 — accessible from Pi #2 only. Wallet connections require Tailscale VPN (use `100.64.1.1:18089`).

---

### 14.6 Recovery: cot_parser Died Silently

Symptom: EUDs connect and ATAK shows "Connected" in server settings, but the device does not appear on the OTS web map or kiosk, and `last_point` is null in the EUD list.

```
# [SSH — tactical-lan]
sudo systemctl restart cot_parser
```

Then have the EUD disconnect and reconnect the TAK server in ATAK (toggle the server Enabled checkbox off then on). Position should appear on the map within one SA reporting cycle (~30 seconds).

Root cause: `cot_parser` is a separate process from OTS that consumes CoT from RabbitMQ and writes positions to PostgreSQL. If it exits cleanly (code 0), systemd does not restart it automatically. This can happen during boot if RabbitMQ is slow to start. The `@reboot` cron entry on the `ps` user account re-runs the node marker script 30 seconds after boot, which provides a passive indicator — if the marker is missing from ATAK devices, `cot_parser` may be down.
