# M2 Community Node — Documentation

This directory contains the complete build and operations documentation for the M2 Community Node.

---

## Reading Order (First-Time Build)

1. **[PREREQUISITES.md](PREREQUISITES.md)** — Hardware, skills, and tools required before you start
2. **[HARDWARE_BOM.md](HARDWARE_BOM.md)** — Full bill of materials with sourcing notes
3. **[BUILD_GUIDE.md](BUILD_GUIDE.md)** — The primary build reference: OS install, networking, services, configuration
4. **[SERVICE_MAP.md](SERVICE_MAP.md)** — Every service, its role, port, and which Pi it runs on
5. **[NETWORK_CUSTOMIZATION.md](NETWORK_CUSTOMIZATION.md)** — How to adapt the reference 192.168.8.x layout to your environment
6. **[CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md)** — Cloudflare tunnel configuration for remote access
7. **[MAINTENANCE.md](MAINTENANCE.md)** — Routine update procedures, credential rotation, cert renewal
8. **[DISASTER_RECOVERY.md](DISASTER_RECOVERY.md)** — Full restore procedures from backup

---

## Service-Specific Docs

| Document | Topic |
|---|---|
| [ELEMENT_PLAN.md](ELEMENT_PLAN.md) | Matrix/Element room structure, event deployment, OPSEC rules |
| [ATAK_CONNECTIVITY.md](ATAK_CONNECTIVITY.md) | OpenTAKServer setup, ATAK enrollment, data package generation |
| [ATAK_RETICULUM_MESH.md](ATAK_RETICULUM_MESH.md) | Reticulum mesh networking integration with ATAK |
| [ATAK_SAR_PLUGINS.md](ATAK_SAR_PLUGINS.md) | Search and rescue plugin configuration |
| [MONERO_NODE.md](MONERO_NODE.md) | Monero full node setup and RPC configuration |
| [QR_CODES.md](QR_CODES.md) | QR code generation workflow for signage and field cards |

---

## Event Operations

| Document | Topic |
|---|---|
| [EVENT_RUNBOOK.md](EVENT_RUNBOOK.md) | Pre-event checklist, day-of procedures, post-event teardown |
| [FIELD_LAPTOP_SETUP.md](FIELD_LAPTOP_SETUP.md) | Admin terminal (field laptop) configuration |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common failure modes and recovery procedures |

---

## Planning Docs

| Document | Topic |
|---|---|
| [MASTER_PLAN.md](MASTER_PLAN.md) | System architecture overview and design decisions |
| [M2_Network_Diagram.drawio](M2_Network_Diagram.drawio) | Full network diagram — renders natively on GitHub; open in [app.diagrams.net](https://app.diagrams.net) to edit or print |

---

## Conventions

- `CHANGE_ME` — placeholder you must replace with your actual value before deploying
- `yourdomain.com` — placeholder for your real domain (set in `instance.conf` at the repo root)
- `192.168.8.x` — reference IP layout; see [NETWORK_CUSTOMIZATION.md](NETWORK_CUSTOMIZATION.md) to adapt
- `pi` — example Linux username; substitute the username you created during Pi OS setup
- Values marked `[see M2_SECRETS.md]` live in your local secrets file (never committed to git)
