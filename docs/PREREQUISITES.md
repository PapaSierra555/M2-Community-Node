# M2 Community Node — Prerequisites

**Read this before starting the build.**

Everything in the main build guide assumes these are already in place. If any of these are missing, you will hit a wall partway through the build.

---

## Accounts You Must Have

### 1. Cloudflare Account (Required for clearnet access)

All clearnet services (Element, ATAK web map, Headscale, ATAK enrollment) route through Cloudflare Zero Trust. Without this, your node is LAN-only.

You need:
- A Cloudflare account (free tier works)
- A domain name you control, added to Cloudflare DNS
- Zero Trust enabled on your account (free for up to 50 users)
- An API token with **Zone:DNS:Edit** and **Zone:Zone:Read** permissions
- Ability to create tunnels in Zero Trust > Networks > Tunnels

See: `CLOUDFLARE_SETUP.md` for a full step-by-step walkthrough.

### 2. Domain Name (Required)

You need a domain you own and can manage DNS for. It does not need to be public-facing — Cloudflare handles the exposure.

Recommended subdomain structure:
```
matrix.yourdomain.com    → Conduit (Matrix server)
element.yourdomain.com   → Element Web
tak.yourdomain.com       → OTS web map (unauthenticated)
headscale.yourdomain.com → VPN access
atakenroll.yourdomain.com → ATAK enrollment page
```

**Important:** Do not apply Cloudflare Access protection to `matrix.` or your Matrix server ID subdomain. Matrix federation requires unauthenticated access to the well-known endpoint.

### 3. Email Address for SSL Certificates

Let's Encrypt requires a contact email for certificate issuance. This email receives expiry warnings. Use a real address you monitor.

---

## Hardware You Must Have Before Starting

> **Not using the reference hardware?** See [BUILD_OPTIONS.md](BUILD_OPTIONS.md) for Pi 4, mini PC, single-device, and no-Monero alternatives before purchasing.

| Item | Notes |
|------|-------|
| 2x Raspberry Pi 5 (8GB or 16GB) | 16GB strongly recommended for Monero |
| 2x NVMe SSD (1TB each) | Monero blockchain alone is ~100GB and growing |
| GL.iNet router (AXT1800 or similar) | Build guide assumes AXT1800 default subnet 192.168.8.x |
| Network switch | Unmanaged 8-port is fine |
| 2x Heltec V3 LoRa modules | One for Reticulum (RNode), one for Meshtastic |
| USB-C power supplies | One per Pi; 27W minimum each |
| MicroSD cards | 32GB minimum for each Pi's OS boot drive |

**If you substitute hardware:** The build guide is written for the specific models in the BOM. Different routers use different default subnets and admin interfaces. If your router uses a different subnet (e.g., 10.0.0.x), you must update all IP addresses throughout the documentation, scripts, and web pages before deploying.

---

## Software and Accounts on Your Build Machine

| Requirement | Notes |
|-------------|-------|
| SSH client | PuTTY (Windows) or built-in (macOS/Linux) |
| SSH key pair | You will use key-based auth to the Pis — no password auth |
| Git | For cloning this repo |
| Python 3.12+ | For running generation scripts |
| PowerShell (Windows) or Bash | Build guide commands are written for PowerShell/Windows |

**Linux/macOS builders:** The build guide explicitly notes commands are PowerShell-first. You will need to adapt quoting and variable syntax. Most commands are standard enough to port without difficulty.

---

## Knowledge Prerequisites

You need working knowledge of:

| Topic | Why It Matters |
|-------|---------------|
| **Linux command line** | All Pi configuration is done over SSH |
| **systemd** | OTS and Monero run as systemd services |
| **Docker and Docker Compose** | The entire comms stack on Pi #1 runs in Docker |
| **Basic networking** | DHCP, DNS, subnets, port forwarding |
| **SSH key management** | Key-based auth required; password auth is disabled |

You do NOT need to know:
- Matrix/Element internals (build guide covers setup)
- ATAK internals (build guide covers server setup; ATAK_Connectivity_Guide covers device setup)
- Monero internals (just need to run the node, not understand the protocol)

---

## Time Expectations

| Phase | Expected Time |
|-------|--------------|
| Hardware assembly | 2-4 hours |
| OS install and initial Pi config | 1-2 hours |
| Docker stack (Pi #1) | 2-3 hours |
| Cloudflare + SSL setup | 1-2 hours |
| OTS install and config (Pi #2) | 2-4 hours |
| Monero sync | **24-72 hours** (runs unattended; just wait) |
| Headscale VPN setup | 1-2 hours |
| Testing and ATAK enrollment | 1-2 hours |
| **Total active build time** | **~12-18 hours** |
| **Total calendar time** | **3-5 days** (dominated by Monero sync) |

**Do not plan to use the node the same day you start the build.** Monero sync is the long pole.

---

## Before You Start: Deployment Parameters Checklist

Fill this out before touching any hardware:

```
My domain:                ______________________
My Node 1 IP:             ______________________  (default: 192.168.8.10)
My Node 2 IP:             ______________________  (default: 192.168.8.20)
My router IP:             ______________________  (default: 192.168.8.1)
My WiFi SSID (guest):     ______________________
My WiFi SSID (admin):     ______________________
My email (SSL certs):     ______________________
My Cloudflare API token:  [in secrets manager]
My Cloudflare Zone ID:    [in secrets manager]
My Cloudflare Tunnel ID:  [will generate during build]
```

Copy `instance.conf.template` to `instance.conf` and fill it in. All generation scripts (QR codes, PDFs, status page) read from this file automatically.

---

## If You Are NOT Using Clearnet (Air-Gapped Mode)

If you are deploying without internet access or do not want clearnet exposure:

- Skip all Cloudflare setup steps
- Skip Let's Encrypt SSL (use self-signed certs or no TLS for LAN services)
- Skip Headscale (no remote VPN needed)
- All services are still fully functional on LAN
- Tor and I2P still work (they tunnel out through whatever internet is available)
- QR codes will point to LAN IPs only — adjust `instance.conf` accordingly

The node is fully functional as a LAN-only device. Clearnet access is optional.
