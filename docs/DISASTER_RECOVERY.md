# Disaster Recovery

Procedures for recovering from hardware failure, data loss, or corrupted services. Written for the field — assumes you are working under pressure and need clear steps.

---

## What to Back Up (and Where)

Back these up before and after every major change. Store copies in at least two places (USB drive, cloud storage, printed).

| Item | Location on Pi | Why Critical |
|------|---------------|--------------|
| Tor private keys | `/opt/community-node/data/tor/*/private_key` | Losing this changes your .onion addresses permanently |
| Conduit signing key | `/opt/community-node/data/conduit/` | Losing this breaks Matrix room membership |
| SSL certificates | `/etc/letsencrypt/` | Losing this means service downtime until cert is reissued |
| Cloudflare tunnel token | `.env` file | Losing this means regenerating tunnel and updating config |
| OTS database | `/opt/opentakserver/data/` | Contains all enrolled clients, tracks, and history |
| Headscale database | `/opt/community-node/data/headscale/` | Contains all VPN clients and keys |
| `instance.conf` | Project root | Your entire deployment configuration |
| `M2_SECRETS.md` | Project root (gitignored) | All credentials |
| `.env` | `/opt/community-node/.env` | Docker service secrets |

### Backup Command (run on each Pi)

```bash
sudo tar -czf /tmp/m2-backup-$(date +%Y%m%d).tar.gz \
  /opt/community-node/data/tor \
  /opt/community-node/data/conduit \
  /etc/letsencrypt \
  /opt/community-node/.env \
  /opt/opentakserver/data
```

Copy the archive off the Pi:

```bash
scp pi@192.168.8.10:/tmp/m2-backup-*.tar.gz .
scp pi@192.168.8.20:/tmp/m2-backup-*.tar.gz .
```

---

## Scenario 1 — Pi Fails to Boot

**Symptoms:** Pi does not appear on network. No SSH. Power LED on but no activity.

**Steps:**

1. Connect a monitor and keyboard directly to the Pi. Note any error output.

2. If no video output at all — suspect power supply. Try a known-good 27W USB-C supply.

3. If boot error on screen — likely SD card or NVMe failure. Remove SD card, reseat NVMe.

4. Boot from SD card only (remove NVMe) to isolate the fault.

5. If SD card is corrupted, re-flash it:
   - Use Raspberry Pi Imager on your field laptop
   - Flash Raspberry Pi OS Lite (64-bit)
   - Enable SSH in advanced settings before flashing
   - Re-image the NVMe using the SD card as intermediary

6. Once Pi boots, restore data from backup (see Scenario 4).

---

## Scenario 2 — Pi #1 (Comms) Fails at an Event

Pi #1 hosts: Matrix/Conduit, Element Web, Nginx, Tor, I2P, Cloudflared, AdGuard.

**Immediate mitigation:**
- Element Web is gone until Pi #1 is restored.
- Matrix federation may be disrupted.
- Clearnet access is down (no cloudflared).
- Direct LAN access to Element is gone.

**What still works:**
- ATAK (Pi #2)
- Mumble voice (Pi #2)
- Meshtastic (LoRa)
- Reticulum (LoRa)
- Monero node (Pi #2)

**Recovery steps:**

1. Confirm it's not just a Docker issue first:
   ```bash
   ssh pi@192.168.8.10
   docker compose ps
   docker compose up -d
   ```

2. If Pi is unreachable, attempt hard reboot: power cycle.

3. If still down, move to full hardware recovery (Scenario 1).

4. Estimated downtime: 30-60 min if spare SD card is pre-imaged. 2+ hours from scratch.

---

## Scenario 3 — Pi #2 (Tactical) Fails at an Event

Pi #2 hosts: OpenTAK Server, Reticulum, Monero, Headscale, Mosquitto, Mumble.

**Immediate mitigation:**
- ATAK server is gone. ATAK apps will lose server connection.
- Mumble voice is gone.
- Monero node is down (wallets can point to a public node temporarily).
- Meshtastic continues to work (it's standalone LoRa).
- Matrix/Element still work (Pi #1).

**Quick ATAK fallback:**
Direct team to use Meshtastic for position sharing. The Meshtastic ATAK plugin will still bridge to ATAK locally — positions will still show if devices are in LoRa range of each other.

**Recovery steps:** Same as Pi #1 above.

---

## Scenario 4 — Restore from Backup

**Prerequisites:** Backup archive from the failed Pi, and the Pi is now bootable.

1. Copy the backup archive to the Pi:
   ```bash
   scp m2-backup-YYYYMMDD.tar.gz pi@192.168.8.10:/tmp/
   ```

2. Extract to restore data:
   ```bash
   ssh pi@192.168.8.10
   sudo tar -xzf /tmp/m2-backup-YYYYMMDD.tar.gz -C /
   ```

3. Re-clone the repo and restore the compose file:
   ```bash
   cd /opt
   sudo git clone https://github.com/YOUR_GITHUB_USERNAME/M2-Community-Node.git community-node
   cd community-node
   # Restore .env from backup or re-create from M2_SECRETS.md
   ```

4. Start services:
   ```bash
   docker compose up -d
   ```

5. Verify Tor keys restored correctly — .onion addresses should match your records:
   ```bash
   cat /opt/community-node/data/tor/element/hostname
   cat /opt/community-node/data/tor/matrix/hostname
   ```

---

## Scenario 5 — Lost Tor .onion Addresses

**Cause:** Tor data directory was deleted or not backed up.

**Impact:** Your previous .onion addresses are gone permanently. New addresses will be generated on next Tor startup. Any QR codes or links pointing to the old addresses are broken.

**Recovery:**

1. Start the Tor container — it will generate new keys and addresses automatically:
   ```bash
   docker compose up -d tor
   docker exec tor cat /var/lib/tor/element/hostname
   docker exec tor cat /var/lib/tor/matrix/hostname
   docker exec tor cat /var/lib/tor/community/hostname
   ```

2. Update `instance.conf` with the new .onion addresses.

3. Regenerate QR codes for documents:
   ```bash
   python scripts/generate_qr.py
   ```

4. Regenerate vinyl-cut QR codes using [mini-qr](https://github.com/lyqht/mini-qr) — update the URLs in `svg/WebQrCodes/qr-url-list.csv` with the new .onion addresses, then paste each into mini-qr and export. See `docs/QR_CODES.md`.

5. Redeploy QR SVGs to Pi #1 and update any printed materials.

5. **Lesson learned:** Back up `/opt/community-node/data/tor/` after every restart that changes keys.

---

## Scenario 6 — SSL Certificates Expired

**Symptoms:** HTTPS services return certificate errors. ATAK can't connect. Element shows certificate warning.

**Check expiry:**
```bash
echo | openssl s_client -connect matrix.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

**Renew:**
```bash
sudo certbot renew
docker compose restart nginx
```

**If renewal fails (DNS challenge error):**
- Verify Cloudflare API token is still valid (they expire — check in Cloudflare > API Tokens)
- Verify the token has DNS:Edit permissions for your zone
- Re-run certbot with verbose output: `sudo certbot renew -v`

**Temporary workaround during outage:**
Configure ATAK to use TCP port 8088 (unencrypted) instead of SSL 8089. This is insecure but keeps ATAK functional until certs are renewed. Revert immediately after.

---

## Scenario 7 — Cloudflare Tunnel Down

**Symptoms:** Clearnet domains (element.yourdomain.com, tak.yourdomain.com) don't load. LAN services still work.

**Diagnose:**
```bash
docker logs cloudflared
```

**Common causes and fixes:**

| Error | Fix |
|-------|-----|
| `invalid token` | Regenerate tunnel token in Cloudflare, update `.env`, restart cloudflared |
| `connection refused` | Pi #1 internet access is down — check router WAN connection |
| `tunnel not found` | Tunnel was deleted in Cloudflare — recreate tunnel and update token |
| `no healthy upstream` | Target service is down — restart the affected container |

**Restart cloudflared:**
```bash
docker compose restart cloudflared
```

---

## Scenario 8 — OTS Database Corrupted

**Symptoms:** OTS starts but shows no clients or history. ATAK enrollment fails. OTS logs show PostgreSQL errors.

**Check OTS logs:**
```bash
sudo journalctl -u opentakserver -n 100
```

**If PostgreSQL is corrupted:**
```bash
# Stop OTS
sudo systemctl stop opentakserver

# Check PostgreSQL
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -c "\l"    # list databases
```

**Restore from backup:**
```bash
# Stop OTS and PostgreSQL
sudo systemctl stop opentakserver
sudo systemctl stop postgresql

# Restore from backup
sudo tar -xzf /tmp/m2-backup-latest.tar.gz -C /

# Restart
sudo systemctl start postgresql
sudo systemctl start opentakserver
```

**If no backup is available:**
- Re-run the OTS installer (this reinitializes the database with clean state)
- Re-enroll all ATAK clients from scratch
- Historical tracks and data packages will be lost

---

## Pre-Event Recovery Checklist

Run this 24 hours before any event:

```bash
# Verify both Pis are reachable
ping -c 3 192.168.8.10
ping -c 3 192.168.8.20

# Verify all Docker services on Pi #1
ssh pi@192.168.8.10 'docker compose -f /opt/community-node/docker-compose.yml ps'

# Verify OTS and Monero on Pi #2
ssh pi@192.168.8.20 'sudo systemctl status opentakserver monerod'

# Check SSL cert expiry
ssh pi@192.168.8.10 'sudo certbot certificates'

# Check disk space
ssh pi@192.168.8.10 'df -h /'
ssh pi@192.168.8.20 'df -h /'

# Test ATAK connection from a phone
# (manual step — enroll one device and verify position sharing)

# Take a fresh backup
ssh pi@192.168.8.10 'sudo tar -czf /tmp/pre-event-pi1.tar.gz /opt/community-node/data/tor /opt/community-node/data/conduit /etc/letsencrypt /opt/community-node/.env'
ssh pi@192.168.8.20 'sudo tar -czf /tmp/pre-event-pi2.tar.gz /opt/opentakserver/data'
scp pi@192.168.8.10:/tmp/pre-event-pi1.tar.gz .
scp pi@192.168.8.20:/tmp/pre-event-pi2.tar.gz .
```

---

## Spare Parts Recommendation

For a resilient event deployment:

| Item | Qty | Notes |
|------|-----|-------|
| Pre-imaged SD card (Pi #1) | 1 | Full OS, repos cloned, Docker installed |
| Pre-imaged SD card (Pi #2) | 1 | Full OS, OTS installed |
| USB drive with latest backup | 1 | Updated before every event |
| Spare USB-C power cable | 2 | Power cables are a common failure point |
| Spare Ethernet cable | 2 | Short patch cables |
