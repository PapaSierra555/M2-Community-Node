# M2 Community Node — Build Options & Hardware Alternatives

The reference build in this repository uses two Raspberry Pi 5 16GB boards. That configuration has been built, field-tested, and has a complete build guide behind it. This document covers every other viable hardware path — what works, what doesn't, what you have to change, and what you lose.

Read this before buying hardware.

---

## The Hard Constraints

These apply regardless of what hardware you choose. They are not optional.

### 1. NVMe storage is required for Pi #2 (Tactical)

Monero's LMDB database does constant random 4K I/O. USB SATA drives get ~1–3K IOPS. NVMe gets 50–100K IOPS. On USB SATA, the initial sync stalls, block verification lags seconds per block, and the node falls behind the chain. The BOM calls it out explicitly: **NVMe is required for Monero LMDB performance, not optional.**

Pi #1 (comms) benefits from NVMe too, but Conduit and the other comms services can function on USB SATA if needed. Pi #2 with Monero cannot.

### 2. 16GB RAM is required if you run Monero

Monero's Docker container is limited to 4GB. During initial blockchain sync it can spike to 4–5GB actual usage. The OS and Docker daemon consume ~1.2GB before any services start. The rest of the tactical stack (OTS, Headscale, Mumble, Reticulum, Mosquitto) uses another 0.8–1.2GB. On an 8GB board, initial sync will cause swap thrashing and likely system instability. 16GB gives you 10–11GB headroom during worst-case Monero load.

If you drop Monero, the RAM floor drops to ~4GB for either Pi.

### 3. Initial Monero sync takes weeks on ARM

On a Pi 5, initial sync takes 2–4 weeks running unattended. On Pi 4, expect 4–8 weeks. On x86_64 hardware, closer to 1 week.

**The practical solution:** Pre-sync on a faster machine (desktop, laptop, any x86), then rsync the LMDB database to the Pi over the network. Reduces field-deploy wait from weeks to a few hours. This is documented in `docs/MONERO_NODE.md`.

### 4. ARM64 or x86_64 — 32-bit is out

All Docker images used in this stack are 64-bit only. Pi 3B and Pi 2 are not viable.

---

## Build Tiers at a Glance

| Tier | Hardware | Full Stack | Monero | Est. Cost | Notes |
|------|----------|-----------|--------|-----------|-------|
| **Reference** | 2× Pi 5 16GB | ✓ | ✓ | ~$994 | Fully documented, field-tested |
| **1 — Tight** | 2× Pi 5 8GB | ✓ | Pre-sync required | ~$784 | Works; Monero sync is the risk |
| **2 — Budget Pi** | Pi 5 16GB + Pi 4 8GB | Comms on Pi 5; tactical without Monero | ✗ | ~$700 | Drop Monero or accept risk |
| **3 — Single Box** | x86_64 Mini PC 16GB | ✓ (all on one device) | ✓ | ~$180–250 | Faster Monero, simpler build, less portable |
| **4 — No Monero** | 2× Pi 5 8GB | ✓ minus Monero | ✗ | ~$784 | Clean, simple, fully supported |
| **5 — Comms Only** | 1× Pi 5 (any RAM) | Comms stack only | ✗ | ~$350–420 | Matrix, Element, Tor, I2P, AdGuard |
| **Not viable** | Pi 4 4GB | ✗ | ✗ | — | OS + Docker alone = 1.2GB |
| **Not viable** | Pi 3B | ✗ | ✗ | — | 1GB RAM, Cortex-A53 too slow |

---

## Tier Reference: 2× Raspberry Pi 5 16GB (~$994)

This is what the build guide is written for. Every command, config, and troubleshooting step assumes this hardware. If you deviate, you are adapting.

**Why Pi 5 over Pi 4:**
- Cortex-A76 cores (Pi 5) are ~2× faster per-core than Cortex-A72 (Pi 4) for Monero cryptographic operations
- Pi 5 runs at 2.4GHz with a proper active cooler; Pi 4 throttles under sustained load
- Pi 5's PCIe connector gives you a native M.2 HAT — the NVMe requirement is met cleanly
- 16GB LPDDR4X is available on Pi 5; Pi 4 tops out at 8GB

**Changes from the build guide:** None. This is the build guide.

---

## Tier 1: 2× Raspberry Pi 5 8GB (~$784, saves ~$210)

The Pi 5 is available in 8GB ($80) as well as 16GB ($80 vs $205). Two 8GB boards save ~$210 over the reference build.

**What works:** Everything on Pi #1 (comms) is fine. The comms stack at steady state uses ~1.2–1.8GB total, leaving 6GB+ headroom on an 8GB board.

**What's risky:** Monero on Pi #2 during initial sync. The 4GB Docker limit plus OS overhead pushes close to the 8GB ceiling. You will likely hit swap during the worst of the initial sync.

**How to make it work:**
1. Pre-sync Monero on a faster x86 machine before deploying to Pi #2. Copy the LMDB database over the network instead of syncing from scratch on the Pi. This eliminates the RAM spike during sync.
2. Once synced, Monero in steady state uses ~1–2GB, which is comfortable on 8GB.

**Changes from the build guide:** None to the build steps. You must pre-sync Monero before deploying — see `docs/MONERO_NODE.md`, "Pre-Sync on x86" section.

**Bottom line:** Works well if you do the pre-sync. Risky if you try to sync natively on the 8GB board.

---

## Tier 2: Mixed Pi 5 16GB + Pi 4 8GB

If you already own a Pi 4 8GB, you can use it for one of the two Pis. The question is which one.

**Use Pi 5 16GB as Pi #2 (tactical) and Pi 4 8GB as Pi #1 (comms).**

Pi #1 runs Docker services (Matrix, Element, Nginx, Tor, I2P, AdGuard). Total memory at steady state is ~1.2–1.8GB. A Pi 4 8GB handles this comfortably. Pi #2 gets the Pi 5 16GB where Monero needs it.

**Do not swap them.** Putting Pi 4 8GB on the tactical stack with Monero will fail.

**Known Pi 4 limitations for this stack:**
- No native M.2 PCIe — you need a USB 3.0 to NVMe adapter for Pi #1 storage. The comms stack can tolerate this (no Monero); USB SATA or NVMe-via-USB is acceptable for Pi #1.
- OpenTAK Server runs on Pi #2 (the Pi 5), so no OTS compatibility concern.
- Pi 4 does not have the same PCIe lane so NVMe requires a HAT that uses the USB 3.0 bus — ~29K IOPS vs NVMe's 100–197K. Adequate for Conduit and comms services.

**Changes from the build guide:**
- Pi #1 will not have a native NVMe HAT — use a USB 3.0 NVMe enclosure instead
- Pi 4 requires `arm_boost=1` in `/boot/firmware/config.txt` to run at full 1.8GHz
- Docker Compose images are all multi-arch (arm64/v8 and arm64/v7); no changes needed

---

## Tier 3: x86_64 Mini PC (Single Device, ~$180–250)

This is the biggest architectural departure — and arguably the best option for builders who prioritize simplicity and performance over portability.

**The idea:** Replace both Pis with a single x86_64 mini PC that runs both docker-compose stacks simultaneously. One device, one power cable, one NVMe, one set of network ports.

**Why x86_64 is better for Monero:**
- Intel N100 (Alder Lake-N, ~$160–180 mini PCs) benchmarks ~3× faster than Pi 5 per-core for Monero's cryptographic operations
- Initial sync time drops from 2–4 weeks to approximately 1 week
- Native PCIe NVMe, no HAT required
- More RAM options — 16GB or 32GB standard

**Recommended hardware:**

| Model | Cores | RAM | Storage | Idle Power | Price (approx.) |
|-------|-------|-----|---------|------------|----------------|
| Beelink EQ12 | Intel N100, 4c | 16GB | 500GB NVMe | ~6W | ~$160–180 |
| Beelink Mini S12 Pro | Intel N100, 4c | 16GB | 500GB NVMe | ~6W | ~$170–190 |
| Minisforum UM560 | AMD R5 5600H, 6c | 16GB | 512GB NVMe | ~8W | ~$200–250 |
| Trigkey G5 | Intel N100, 4c | 16GB | 500GB NVMe | ~5W | ~$150–170 |

Add a second 1TB NVMe or upgrade to 2TB to match the Pi #2 storage spec.

**Power consumption comparison:**

| Build | Idle | Typical | Peak |
|-------|------|---------|------|
| 2× Pi 5 16GB | ~7W | ~14W | ~20W |
| Mini PC (N100) | ~6W | ~10W | ~15W |
| Mini PC (Ryzen 5) | ~8W | ~15W | ~25W |

The mini PC is actually more efficient than two Pis at typical load — and you eliminate one device, one power supply, and one set of network cables.

**What you lose:**
- The dual-Pi form factor. The reference build's two-Pi layout provides physical isolation between comms and tactical services — one Pi can reboot without taking down the other. On a single box, both stacks go down together.
- ARM experience. If your use case involves learning to maintain ARM SBCs, a mini PC doesn't teach you that.
- Portability. The reference build fits in an 8U 10" mini-rack weighing under 10 lbs. A mini PC in a rack adds bulk and needs a rack shelf.

**What changes in the build guide:**
- Phase 1 (OS install): Install Ubuntu 24.04 LTS x86_64 instead of Pi OS
- Phase 2 (storage): No NVMe HAT needed; NVMe installs directly to M.2 slot
- All docker-compose files run on one machine: run both `docker-compose.yml` and `docker-compose.tactical.yml` from the same host
- OpenTAK Server installs the same way (systemd binary) — use the x86_64 installer from the OTS releases page
- Remove all Pi-specific steps: no `raspi-config`, no `dtparam=pciex1_gen=3`, no active cooler setup
- Kiosk display: if you want the touchscreen kiosk, you will need a USB-connected monitor or repurpose a separate display

---

## Tier 4: No Monero (~$784, 2× Pi 5 8GB)

If you do not need a community Monero privacy node, the hardware requirements drop significantly.

**What you lose:** The Monero full node and restricted RPC endpoint. Everything else — ATAK, Matrix, Meshtastic, Reticulum, Headscale, Mumble, Tor, I2P, AdGuard — runs exactly the same.

**What you gain:**
- RAM floor drops from 16GB to 8GB per Pi
- Pi #2 storage drops from 1TB to 256GB
- No 2–4 week initial sync delay
- Simpler deployment

**How to remove Monero from the build:**
1. In `docker-compose.tactical.yml`, comment out or remove the `monerod` service block entirely
2. Skip `docs/MONERO_NODE.md` during the build
3. Use a 256GB NVMe for Pi #2 instead of 1TB

No other services depend on Monero. The rest of the tactical stack is unaffected.

**Cost impact:** Two Pi 5 8GB boards ($80 each) instead of two Pi 5 16GB ($205 each) saves ~$250. Pi #2 dropping from 1TB to 256GB NVMe saves another ~$80–100.

---

## Tier 5: Comms Stack Only (1× Pi 5, ~$350–420)

If you only need encrypted group chat, Tor/I2P access, and DNS filtering — and do not need ATAK, VPN, or mesh radio — the entire comms stack runs on a single Pi.

**What runs on Pi #1 alone:**
- Matrix / Conduit (encrypted group chat, federation)
- Element Web (browser client)
- Nginx reverse proxy
- Tor hidden services
- I2P
- AdGuard Home DNS
- Cloudflare tunnel for clearnet access

**What you lose:** All Pi #2 services — ATAK/OTS, Headscale, Mumble, Meshtastic, Reticulum, Monero.

**Hardware:** A single Pi 5 (8GB is sufficient, 16GB if you want headroom), 256GB NVMe, GL.iNet router. Around $350–420 depending on whether you include the router.

**Build guide:** Follow all phases except those that reference Pi #2. The comms stack has no dependencies on tactical services.

---

## Choosing a LoRa Radio

The reference build uses Heltec V3 USB LoRa modules — one for Meshtastic, one as an RNode for Reticulum. These are plug-and-play over USB and require no additional HATs.

**Alternatives:**
- **Waveshare SX1262 LoRa HAT** — attaches to Pi GPIO header. Works with both Meshtastic and Reticulum. Saves a USB port. Requires HAT installation step.
- **RAK WisHat RAK2287** — higher-end, used in serious infrastructure deployments. More expensive (~$60–100), but better sensitivity and range.
- **Any RNode-compatible hardware** — Reticulum supports a wide range of RNode-flashed hardware. See the Reticulum documentation for the current compatibility list.

If you drop Meshtastic and only need Reticulum, one LoRa radio is sufficient.

---

## Choosing a Router

The build guide is written for the GL.iNet AXT1800 (Slate AX) with its default `192.168.8.x` subnet. Any OpenWrt router will work with adaptation.

**Drop-in compatible (same default subnet):**
- GL.iNet MT3000 (Beryl AX) — faster Wi-Fi 6, more compact, ~$99
- GL.iNet MT2500 (Brume 2) — no Wi-Fi, wired-only, good for rack builds with a separate AP

**Requires subnet adaptation:**
- Any non-GL.iNet OpenWrt router. The default subnet is likely `192.168.1.x`. Update all IP references in docs, scripts, and HTML files before deploying (see `docs/NETWORK_CUSTOMIZATION.md`).
- Consumer routers with OpenWrt support — works, but GL.iNet routers ship with a hardened OpenWrt build and native WireGuard/Headscale support.

**If you use a managed switch** (instead of the unmanaged TL-SG108S): VLANs give you physical network isolation between guest WiFi and the admin network. The build supports this — see `docs/NETWORK_CUSTOMIZATION.md`.

---

## Service Dependency Map

Before dropping or substituting any service, know what depends on what:

| Service | Depends on | Required by |
|---------|------------|-------------|
| Conduit (Matrix) | Nginx, Docker | Element Web |
| Element Web | Nginx | (none — client only) |
| Nginx | (none) | Conduit, Element Web, Cloudflare tunnel |
| Cloudflare tunnel | Nginx | Remote access to all clearnet services |
| AdGuard Home | (none) | Split-DNS for LAN clients (optional) |
| Tor | (none) | Tor hidden services |
| I2P | (none) | I2P routing |
| OpenTAK Server | RabbitMQ (bundled), systemd | ATAK clients, OTS web map |
| Headscale | (none) | Remote VPN access |
| Mumble | (none) | Voice comms |
| Meshtastic bridge | Mosquitto (MQTT), Heltec radio | LoRa mesh |
| Reticulum (RNS) | RNode-compatible radio | NomadNet, ATAK mesh layer |
| Monero | NVMe storage, 16GB RAM | (none — standalone service) |

Monero has no dependents. It can be dropped with no effect on any other service.

---

## Storage Quick Reference

| Service | Minimum | Recommended | Growth rate |
|---------|---------|-------------|-------------|
| Conduit (Matrix DB) | 1GB | 50GB | ~2GB/year (active node) |
| Monero (pruned) | 95GB | 200GB | ~8–10GB/year |
| OTS / ATAK data | 2GB | 20GB | ~500MB/month (active events) |
| OS + Docker | 20GB | 30GB | Minimal |
| **Pi #1 total** | 32GB | **256GB** | — |
| **Pi #2 total (with Monero)** | 120GB | **1TB** | — |
| **Pi #2 total (no Monero)** | 32GB | **256GB** | — |

---

## Frequently Asked Questions

**Can I run everything on a single Pi?**
Not reliably with Monero. The RAM ceiling is the hard stop. Without Monero, a single Pi 5 16GB can run both stacks — but you lose fault isolation (one crash takes everything down).

**Can I use a USB SSD instead of NVMe for Pi #2?**
Only if you drop Monero. USB SATA (~29K IOPS) is inadequate for Monero LMDB. For Pi #1 (comms only), USB SSD works but NVMe is faster and cleaner.

**Can I use a Pi 4 for anything in this build?**
Yes — Pi #1 (comms stack only, no Monero) on Pi 4 8GB works. Do not use Pi 4 for Pi #2 with Monero.

**What is the minimum viable build for a one-day event?**
Single Pi 5 8GB + 256GB NVMe + GL.iNet router. Run the comms stack (Matrix, Element, AdGuard, Tor). Add OTS if you need ATAK. Skip Monero entirely. ~$350–420 all in.

**Can I add more storage later?**
Yes. Swap the NVMe drive while the Pi is powered off. Copy data using `rsync -aHAX` before swapping. For Monero specifically, the LMDB database copies cleanly — just point the service at the new path.

**What if I want to add services not in this build?**
The Docker architecture is extensible. Add services to the appropriate `docker-compose.yml` or `docker-compose.tactical.yml`. Ensure any new services get entries in the Nginx reverse proxy config and Cloudflare tunnel routes if they need clearnet access.
