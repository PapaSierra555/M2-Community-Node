# M2 Community Node — Day-of-Event Runbook

**For the tech running the node at a SAR operation, community event, or training exercise.**

This document assumes the node has already been built and configured per `BUILD_GUIDE.md`. You do not need to read the build guide to use this runbook.

---

## Power-On Sequence

Order matters. Power on in this sequence:

1. **UPS** (BC600R) — press power button, confirm LED is green
2. **GL.iNet router** (AXT1800) — power on, wait **60 seconds** before touching anything
3. **TL-SG105 switches** — power on (no boot time)
4. **Pi #1 (comms, 192.168.8.10)** — power on
5. **Pi #2 (tactical, 192.168.8.20)** — power on
6. Wait **90 seconds** for both Pis to fully boot and services to start
7. **Kiosk touchscreen** — power on last

**Total boot time: ~3 minutes.** Do not test connectivity during this window.

---

## POST — Power-On Self-Test

After the 90-second boot window, run this check from any device on the `NodeAdmin` WiFi:

### Quick check (30 seconds)

Open a browser and hit these URLs. All should load:

| URL | Expected | Service |
|---|---|---|
| `http://192.168.8.1` | GL.iNet admin panel | Router |
| `http://192.168.8.10:8081` | Community info page | Kiosk web |
| `http://192.168.8.10:8080` | Element Web login | Matrix chat |
| `http://192.168.8.20:8080` | OTS web map | OpenTAK Server |

If all four load: **node is go.**

### Full POST (SSH, 2 minutes)

Run this on your laptop if the quick check fails or you want full confidence:

```
[SSH — comms-lan]
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output (all containers `Up`):
```
community-node-nginx-1         Up X hours
community-node-cloudflared-1   Up X hours
community-node-element-web-1   Up X hours (healthy)
community-node-tor-1           Up X hours (healthy)
community-node-i2pd-1          Up X hours
community-node-conduit-1       Up X hours
```

```
[SSH — tactical-lan]
systemctl is-active opentakserver cot_parser headscale && docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected: `active` (three times), then containers:
```
tactical-node-monerod-1     Up X hours (healthy)
tactical-node-nomadnet-1    Up X hours
tactical-node-reticulum-1   Up X hours
tactical-node-mosquitto-1   Up X hours
```

> Note: Headscale runs as a systemd service (`headscale.service`), not Docker. Verify with `systemctl is-active headscale`.

---

## Pre-Event Checklist (30 minutes before go-live)

- [ ] All POST checks pass
- [ ] Kiosk map is live and showing the Community Node marker at correct location
- [ ] Connect a test phone to `CommunityNode` WiFi, open ATAK, confirm it connects to `192.168.8.20:8089`
- [ ] Test phone icon appears on OTS web map at `http://192.168.8.20:8080`
- [ ] GeoChat test: send a message from the test phone, confirm it appears in OTS
- [ ] Mumla voice test: open Mumla → `192.168.8.20` port `64738` → confirm connection
- [ ] Field cards printed and on hand (or QR codes available on kiosk)
- [ ] If running structured SAR: pre-build an ExCheck checklist template in ATAK and distribute via OTS data package before go-live
- [ ] WiFi password posted/available for incoming team members

---

## Onboarding Arriving Team Members

**Path A — Local WiFi (everyone physically here):**

1. Connect phone to `CommunityNode` WiFi
2. Open ATAK → Menu → Import → QR Code
3. Scan the QR code from the kiosk or from OTS Web UI (Certificates → Generate Data Package → Show QR Code)
4. Set callsign: Settings → My Preferences → Callsign
5. Verify icon on map. Done. **~3 minutes.**

**Path B — Remote viewer (off-site, browser only):**

1. Add their email to Cloudflare Access: `dash.cloudflare.com` → Zero Trust → Access → Applications → OTS Web Map → Edit → add email → Save
2. Send them: `https://tak.yourdomain.com`
3. They enter email, get 6-digit OTP, see live map. **~60 seconds.**

**Path C — Remote ATAK (trusted operator, full participation):**

```
[SSH — tactical-lan]
sudo headscale preauthkeys create -c /opt/tactical-node/config/headscale/config.yaml --user 2 --expiration 24h
```

Send them the key + `https://m2vpn.capableenough.org` + ATAK server `192.168.8.20:8089`.

---

## Pre-Event: Matrix Event Space Setup (1 week before)

Run from the field laptop (m2-field) or any machine on NodeAdmin WiFi with the repo checked out.

**Requires:** m2bot access token from `M2_SECRETS.md` → Matrix section → Bot password. Get the token by logging in as m2bot via the Matrix API or Element.

**Step 1 — Create the space and rooms:**

```
[m2-field or Windows dev machine]
cd ~/SOURCE\ CONTROL/M2-Community-Node
python3 scripts/m2-event-space.py create --event "CCC26" \
  --bot-token <m2bot-token> \
  --invite @YOUR_ADMIN_ACCOUNT:matrix.org
```

Output lists 6 room aliases (1 space + 5 rooms). State saved to `/tmp/m2-event-space-state.json` — do not delete this file until after teardown.

**Step 2 — Accept invites:**

Open Element at `https://communitynode.yourdomain.com`, log in as `@YOUR_ADMIN_ACCOUNT:matrix.org`, accept all 6 invites.

**Step 3 — Promote admin:**

```
python3 scripts/m2-event-space.py promote \
  --bot-token <m2bot-token> \
  --invite @YOUR_ADMIN_ACCOUNT:matrix.org
```

Sets PL 100 in all rooms. Verify in Element: room Settings → Roles & Permissions → @YOUR_ADMIN_ACCOUNT should show Admin.

**Step 4 — Test:**

- Send a message in each room
- Confirm encryption lock icon is present
- Confirm status bot is posting to `#m2-ops` (fires every 12h — check if one is due or post manually via `sudo systemctl start m2-status-bot.service`)

**Rooms created:**

| Alias | Purpose |
|---|---|
| `#m2-ccc26:m2.yourdomain.com` | Space container |
| `#m2-ccc26-general:m2.yourdomain.com` | General coordination |
| `#m2-ccc26-ops:m2.yourdomain.com` | Ops / logistics |
| `#m2-ccc26-field:m2.yourdomain.com` | Field team comms |
| `#m2-ccc26-sar:m2.yourdomain.com` | SAR / emergency |
| `#m2-ccc26-atak:m2.yourdomain.com` | ATAK coordination |

All rooms: private, invite-only, E2E encrypted, room version 10.

---

## During the Event

### Kiosk status tab
The kiosk dashboard (touchscreen at rack U6) shows live service status. Green = healthy. If anything goes red, see troubleshooting below.

### If ATAK positions stop updating

```
[SSH — tactical-lan]
systemctl status cot_parser
sudo systemctl restart cot_parser
```

Wait 15 seconds, confirm positions resume on the map.

### If a user can't connect to ATAK

Common causes:
1. **SSL checkbox** — in ATAK server settings, "Use default SSL/TLS Certificates" must be **unchecked**. Delete the server entry and re-add with it unchecked.
2. **Wrong WiFi** — confirm they're on `CommunityNode`, not a personal hotspot
3. **Certificate enrollment** — if connecting manually (not QR), port 8446 must be reachable. Confirm OTS is running.

### If Element/Matrix is down

```
[SSH — comms-lan]
docker restart community-node-conduit-1
docker restart community-node-nginx-1
```

Wait 30 seconds, refresh Element Web.

### If the kiosk screen is blank

Touch the screen to wake. If still blank after 10 seconds, the screensaver is active — touch again. If Chromium has crashed, SSH in:

```
[SSH — comms-lan]
sudo reboot
```

Do NOT pkill Chromium from SSH — it won't relaunch automatically.

---

## Teardown / Pack-Up

**Shut down in reverse order: Pis first, then power.**

**Step 0: Tear down Matrix event space**

```
[m2-field or Windows dev machine]
python3 scripts/m2-event-space.py destroy --bot-token <m2bot-token>
```

Tombstones all 6 rooms and leaves. Room history persists in Conduit DB for the record — members can still read history but the rooms are archived. Kick remaining members if you want to fully vacate.

**Step 1: Graceful Pi shutdown**

```
[SSH — comms-lan]
sudo shutdown -h now
```

Wait 15 seconds, then:

```
[SSH — tactical-lan]
sudo shutdown -h now
```

Wait for SSH to disconnect (Pi has powered off). Do NOT pull power while SSH is still connected.

**Step 2: Power down**

1. Kiosk screen — power off
2. Switches — power off
3. GL.iNet router — power off
4. UPS — hold power button until LED goes out

**Step 3: Pack-up notes**
- LoRa antennas: coil gently, no tight bends
- USB cables: do not yank — grip the connector, not the cable
- Monero sync state is preserved on NVMe — no action needed
- Tor keys are preserved at `/opt/community-node/data/tor/` — no action needed
- Element config and message history persists on NVMe — no action needed

---

## Emergency: Internet Lost Mid-Event

Local WiFi ATAK, Matrix chat, and Meshtastic all continue working with no internet. Nothing to do.

Services that stop working: `tak.yourdomain.com` (remote viewers), `communitynode.yourdomain.com`, Headscale enrollment.

If you want to cut outbound traffic intentionally (air-gap):

```
[SSH — comms-lan]
docker stop community-node-cloudflared-1
```

```
[SSH — tactical-lan]
docker stop tactical-node-headscale-1
```

This isolates the node to LAN-only. Reverse with `docker start` when ready to reconnect.

---

## Emergency: A Pi Won't Boot

If a Pi is completely unresponsive after full boot window:

1. Check power LED on the Pi (solid red = power OK, green = activity)
2. Check ethernet LED on switch port (should blink)
3. If no lights: check USB-C cable and Anker power supply output
4. If lights OK but SSH unreachable: connect HDMI monitor to Pi, check boot messages
5. If SD card corruption suspected: re-flash SD from a backup image

**If Pi #1 (comms) is down:** ATAK and Monero still work. Matrix/Element is unavailable. Meshtastic still works.

**If Pi #2 (tactical) is down:** ATAK is unavailable. Matrix/Element still works for coordination.

---

## Quick Reference

| Service | URL / Address | Notes |
|---|---|---|
| Router admin | `http://192.168.8.1` | NodeAdmin WiFi only |
| Community page | `http://192.168.8.10:8081` | QR codes, app links |
| Element Web | `http://192.168.8.10:8080` | Matrix chat |
| OTS web map (LAN) | `http://192.168.8.20:8080` | Admin login |
| OTS web map (clearnet) | `https://tak.yourdomain.com` | Email OTP required |
| ATAK server | `192.168.8.20:8089` | SSL, uncheck default certs |
| Mumble voice | `192.168.8.20:64738` | Mumla app |

---

v1.0
