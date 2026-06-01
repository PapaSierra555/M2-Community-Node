## Meshtastic 8-Node Field Pack

M2 Community Node now ships with a complete Meshtastic field deployment kit: 8 × Heltec T114 field nodes in a Pelican case, pre-configured and ready to loan to event attendees. The two rack-mounted Heltec V3 ROUTER nodes bridge all traffic to the MQTT/Matrix stack as before — the T114 fleet extends that coverage to everyone at the event.

<img src="https://github.com/PapaSierra555/M2-Community-Node/releases/download/v1.1.0/Meshtastic_8Pack.jpg" width="480">

<img src="https://github.com/PapaSierra555/M2-Community-Node/releases/download/v1.1.0/Meshtastic_Charging.jpg" width="480">

---

### What's new

**Hardware — MF-1 through MF-8**
- 8 × Heltec T114 LoRa nodes — 915 MHz, built-in GPS, E-ink display, Li-Po battery
- Pelican case with foam cutouts — all 8 nodes, color-coded lanyards, USB-C data cables
- Dedicated USB charging hub for bulk pre-event prep

**Scripts** (`meshtastic/scripts/`)

| Script | Purpose |
|---|---|
| `config_heltec_v3.py` | Push PSK + config to the 2 rack ROUTER nodes |
| `gen_m2_channel_qr.py` | Generate day-of channel QR card (rotate PSK first) |
| `generate_m2_mesh_handoff.py` | Rebuild operator reference PDF |
| `generate_m2_mesh_runbook.py` | Rebuild non-technical operator runbook |
| `generate_m2_mesh_cheatsheet.py` | Rebuild 1-page pre/day-of/post cheatsheet |
| `generate_m2_mesh_connection_card.py` | Rebuild T114 device checkout cards (8 nodes, 4 pages) |

**Print-ready PDFs** (`meshtastic/pdf/`)

| File | Purpose |
|---|---|
| `M2_Mesh_Handoff.pdf` | Operator reference — hardware inventory, scripts, troubleshooting |
| `M2_Mesh_Runbook.pdf` | Non-technical guide — T114 UF2 flash, configure, replace |
| `M2_Mesh_Cheatsheet.pdf` | 1-page quick reference for event day |
| `M2_Mesh_DeviceCard_Front.pdf` | T114 checkout cards — front (8 nodes, 4 pages) |
| `M2_Mesh_DeviceCard_Back.pdf` | T114 checkout cards — back (8 nodes, 4 pages) |

> `M2_Mesh_ChannelQR_DayOf.pdf` is gitignored — it encodes the live PSK. Regenerate after each rotation with `gen_m2_channel_qr.py` and print fresh for every event.

---

### Architecture

Two node classes, one mesh:

- **ROUTER (rack):** 2 × Heltec V3 — rack-mounted in M2 8U, USB serial to Pi 2, MQTT bridge to Matrix and ATAK. Always on.
- **CLIENT (field):** 8 × Heltec T114 — loan devices in Pelican case. Attendees pair over Bluetooth, scan QR to join CommunityNode channel. No cell service or internet required.

---

### Pre-event workflow

```
1. Generate new PSK and save
2. Update CHANNEL_PSK_B64 in config_heltec_v3.py AND gen_m2_channel_qr.py
3. python meshtastic/scripts/config_heltec_v3.py    # rack nodes
4. python meshtastic/scripts/gen_m2_channel_qr.py   # print fresh QR card
5. Distribute T114 field nodes from Pelican case at check-in
```

---

### Notes

- `config_m2_t114.py` (T114 field node config script) is referenced in documentation but not yet committed — add before first event deployment
- All PDFs are font-embedded and print-ready (verified with PyMuPDF)
- PSK rotation is mandatory before every event — see `M2_Mesh_Handoff.pdf` Section 5
