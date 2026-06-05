# M2 Community Node — Project CLAUDE.md

## Project Overview

Offline-capable community communications node. Raspberry Pi stack running Matrix/Element, OpenTAKServer, Meshtastic integration, Headscale VPN, Monero node, Tor/I2P hidden services. Deployed at community events as a self-contained mesh comms platform.

**Repo:** `PapaSierra555/M2-Community-Node` (PUBLIC)
**Live node:** Florence SC — Pis at 192.168.8.10 (comms) and 192.168.8.20 (tactical)

---

## Key Architecture

| Service | Host | Access |
|---|---|---|
| Matrix/Conduit | comms Pi | `m2-matrix.capableenough.org` |
| Element Web | comms Pi | `communitynode.capableenough.org` |
| OpenTAKServer | tactical Pi | `tak.capableenough.org` |
| Headscale VPN | tactical Pi | `m2vpn.capableenough.org` |
| Meshtastic | USB serial | scripts/meshtastic/ |

Matrix server name: `m2.capableenough.org`
Homeserver API: `https://m2-matrix.capableenough.org` (NOT matrix.capableenough.org)

---

## Session Recovery

1. Read this file + `~/.claude/CLAUDE.md` + `~/.claude/projects/.../memory/`
2. `git log --oneline -10 && git status`
3. Check `memory/project_status.md` for live node state
4. Verify cert expiry dates and any pending post-event cleanup

---

## Repo Structure

```
M2-Community-Node/
├── scripts/              — PDF/QR generators + Matrix ops tools
│   └── fonts/            — TrueType fonts (BigShoulders, IBMPlexMono, InstrumentSans)
├── meshtastic/
│   ├── scripts/          — Device config + card generators
│   └── pdf/              — Generated QR/device card PDFs
├── community-outreach/
│   ├── scripts/          — Marketing PDF generators
│   └── assets/           — Logos, images (lfhi-logo.png)
├── operational-pdfs/     — Generated reference/event PDFs
├── config/               — Service config templates (conduit, nginx, element, etc.)
├── docs/                 — Build guides, field setup, architecture
├── docker-compose.yml    — Comms Pi services
├── docker-compose.tactical.yml — Tactical Pi services
├── instance.conf.template — Network/domain config (gitignored when filled)
└── M2_SECRETS.template.md — Credentials template (gitignored when filled)
```

---

## Python Scripts

Run all scripts from the **project root** — paths are relative to root:

```bash
python3 scripts/generate_qr.py
python3 meshtastic/scripts/gen_ccc_channel_qr.py
python3 meshtastic/scripts/build_ccc_device_cards.py
python3 meshtastic/scripts/generate_m2_ccc26_join_card.py
python3 meshtastic/scripts/config_ccc_t114.py   # USB serial — plug device first
python3 meshtastic/scripts/config_ccc_t3s3.py   # USB serial — plug device first
```

Dependencies: `pip3 install -r requirements.txt`

---

## Secrets

- `M2_SECRETS.md` — gitignored, pull from Obsidian `z_Backups/M2_SECRETS.md`
- `instance.conf` — gitignored, local network config
- NEVER commit either file

---

## Pi SSH Access

```bash
ssh ps@192.168.8.10   # comms Pi (Matrix, Element, Tor)
ssh ps@192.168.8.20   # tactical Pi (OTS, Headscale, Mosquitto, Monero)
```

Or via aliases if `~/.ssh/config` is set up (see `docs/FIELD_LAPTOP_SETUP.md`).

---

## Matrix Admin

```bash
# Get access token
curl -s -X POST "https://m2-matrix.capableenough.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  -d '{"type":"m.login.password","identifier":{"type":"m.id.user","user":"admin"},"password":"<from M2_SECRETS.md>"}'
```

---

## Meshtastic Fleet (CCC26)

T114 fleet: MESH 01–08 (physical labels: slot 01–08, permanent)
T3S3 personal: PS-01, PS-02, PS-03 (permanent, event-agnostic)
CCC26 channel: `CCC26` | PSK: in M2_SECRETS.md | Region: US | Preset: LONG_FAST

PSK rotation: generate → update all 3 scripts + M2_SECRETS.md → push to z_Backups/ → re-run gen_ccc_channel_qr.py → reprint cards

---

## Post-CCC26 Cleanup (June 15, 2026)

1. `python3 scripts/m2-event-space.py destroy` — tombstone CCC26 rooms
2. SSH comms Pi → edit `conduit.toml` → `allow_registration = false`, restore token → `docker restart conduit`
3. Delete Cloudflare redirect rule `element-to-m2-ccc26`
4. Rotate Meshtastic PSK for next event
