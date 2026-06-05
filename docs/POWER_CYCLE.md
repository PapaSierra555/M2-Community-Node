# M2 Community Node — Power Cycle & Field Startup

Quick reference for field ops. Pull repo, plug in, follow this doc.

---

## Physical Setup

1. Connect both Pis to the router (LAN ports)
2. Connect router WAN to internet uplink (hotspot, ethernet, etc.)
3. Connect monitor/keyboard to comms Pi (192.168.8.10) if using kiosk display
4. Apply power to router first — let it fully boot (~30s) before powering Pis
5. Apply power to both Pis

---

## Boot Wait

**Wait 90 seconds** after power-on before checking services.

Both Pis are configured with `After=network-online.target` — services wait
for full internet connectivity before starting. Give them the full 90s.

---

## Verify — Run From Field Laptop (or any machine on M2 WiFi)

**Comms Pi — all 7 containers should be Up:**
```
ssh ps@192.168.8.10 "sudo docker ps --format 'table {{.Names}}\t{{.Status}}'"
```
Expected: adguard, cloudflared, conduit, element-web, nginx, tor, i2pd — all `Up`

**Tactical Pi — systemd services + Docker containers:**
```
ssh ps@192.168.8.20 "sudo systemctl is-active headscale && sudo systemctl is-active opentakserver && sudo docker ps --format 'table {{.Names}}\t{{.Status}}'"
```
Expected: `active` / `active` / monerod, mosquitto, reticulum, nomadnet — all `Up`

**Smoke test — Matrix reachable:**
```
curl -sk https://m2-matrix.capableenough.org/_matrix/client/versions | head -c 60
```
Expected: JSON with `versions` array

---

## Status Dashboard

The kiosk display (comms Pi HDMI) shows live status. All indicators
should be green within ~2 minutes of boot:

| Indicator | What it checks |
|---|---|
| Monerod | Docker container up |
| OpenTAK | `systemctl is-active opentakserver` |
| Headscale | `systemctl is-active headscale` |
| Mosquitto | Docker container up |
| Reticulum | Docker container up |
| Tunnel (PUBLIC IP box) | `https://m2vpn.capableenough.org/health` returns 200 |

Dashboard refreshes every 60 seconds via cron. If something shows red
right after boot, wait one more minute before troubleshooting.

---

## Clean Shutdown

Always shut down cleanly — do not yank power.

```
ssh ps@192.168.8.10 "sudo docker compose -f /opt/community-node/docker-compose.yml --profile clearnet down && sudo shutdown -h now"
```
```
ssh ps@192.168.8.20 "sudo systemctl stop headscale && sudo shutdown -h now"
```

Wait ~30 seconds for both to halt, then cut power.

---

## Troubleshooting

**Mosquitto red / crash-looping:**
Check `/opt/tactical-node/config/mosquitto/mosquitto.conf` — must have
`allow_anonymous true` (no `password_file` line). Mosquitto 2.x will
crash on startup if `password_file` is set but the file doesn't exist.
```
ssh ps@192.168.8.20 "sudo docker restart tactical-node-mosquitto-1"
```

**Headscale red on dashboard:**
Dashboard checks `systemctl is-active headscale` on Pi #2. If red, check:
```
ssh ps@192.168.8.20 "sudo systemctl status headscale --no-pager -l | tail -10"
```
Most common cause: DERP map fetch failed at boot (network not ready).
Fix: `sudo systemctl restart headscale` — it will succeed once network is up.

**Headscale Docker container appearing in `docker ps`:**
Should never happen — headscale runs as systemd only. If it appears and
crash-loops, the `tactical-node.service` unit file has `--profile vpn`
in its ExecStart. Remove it:
```
ssh ps@192.168.8.20 "sudo sed -i 's/ --profile vpn//' /etc/systemd/system/tactical-node.service && sudo systemctl daemon-reload"
```
Then stop and remove the rogue container:
```
ssh ps@192.168.8.20 "sudo docker stop tactical-node-headscale-1 && sudo docker rm tactical-node-headscale-1"
```

**DDNS MISMATCH on dashboard (red box around public IP):**
M2 uses Cloudflare Tunnel — the Pi's public IP never matches DNS by
design. The dashboard checks tunnel reachability, not IP matching. If
this shows red, the Cloudflare tunnel is down. Check cloudflared:
```
ssh ps@192.168.8.10 "sudo docker logs community-node-cloudflared-1 --tail 20"
```

**OTS not responding:**
OTS depends on RabbitMQ. Check both:
```
ssh ps@192.168.8.20 "sudo systemctl is-active rabbitmq-server && sudo systemctl is-active opentakserver"
```

---

## Key IPs & Ports (LAN)

| Service | Address |
|---|---|
| Element Web | http://192.168.8.10:8080 |
| Matrix API | https://192.168.8.10 (via nginx) |
| OpenTAKServer | http://192.168.8.20:8080 |
| Monero RPC | http://192.168.8.20:18089 |
| AdGuard DNS | 192.168.8.10:3000 (admin) |

SSH: `ssh ps@192.168.8.10` (comms) / `ssh ps@192.168.8.20` (tactical)

---

## Clearnet Domains

| Domain | Service |
|---|---|
| communitynode.capableenough.org | Element Web |
| m2-matrix.capableenough.org | Matrix/Conduit API |
| tak.capableenough.org | OpenTAKServer |
| m2vpn.capableenough.org | Headscale VPN |

---

*See `docs/FIELD_LAPTOP_SETUP.md` for first-time field laptop config.*
