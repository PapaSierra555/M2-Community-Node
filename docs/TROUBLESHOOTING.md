# M2 Community Node — Troubleshooting

Organized by symptom. Every entry here was either experienced during the reference build or identified as a high-probability failure mode.

---

## WiFi / Network

### WiFi clients can't reach the Pis after changing router settings

**Symptom:** Phones connect to WiFi but can't load the community page or reach any Pi service. Wired devices work fine.

**Cause:** GL.iNet firmware silently sets `ap_isolate=1` after any WiFi configuration change. This blocks WiFi clients from reaching wired devices (the Pis) even on the same subnet.

**Fix:**
```bash
ssh root@192.168.8.1
hostapd_cli -i wlan0 set ap_isolate 0
hostapd_cli -i wlan1 set ap_isolate 0
```

If you have a boot script that applies this fix, verify it ran:
```bash
logread | grep ap_isolate
```

**Note:** This fix does not survive a router reboot unless applied via a scheduled script. The reference build runs this fix at 15s and 30s after boot via a cron job on the router.

---

### Devices won't connect after power cycle — wait 60 seconds

**Symptom:** Just power-cycled the rack. Nothing works. Phones can't connect.

**Cause:** The router takes 30-45 seconds to fully boot and apply all scripts. The AP isolation fix scripts run at 15s and 30s — if the router hasn't fully initialized, they fail silently.

**Fix:** Wait 60 seconds after power-on before testing. Then test from a wired device first, then WiFi.

---

### Can't get static DHCP leases before first boot

**Symptom:** Trying to assign fixed IPs (192.168.8.10 and 192.168.8.20) to the Pis before they've booted.

**Cause:** You need the Pi's MAC address to create a static lease, but the Pi hasn't booted yet to reveal its MAC.

**Fix:** Boot both Pis on DHCP first. Find their assigned IPs in the router's connected devices list. Note their MAC addresses. Then create static leases and reboot the Pis.

---

### DHCP range conflicts with static IPs

**Symptom:** Router assigns 192.168.8.10 or 192.168.8.20 to a random device.

**Fix:** Set the DHCP range to start above your static IPs. Example: static leases at .10 and .20, DHCP range starts at .100.

---

## Docker / Services (Pi #1)

### `docker compose up` fails with missing variable error

**Symptom:** Error like `variable CLOUDFLARE_TUNNEL_TOKEN is not set`

**Cause:** `.env` file missing or incomplete. Docker Compose requires all variables referenced in the compose file to be defined.

**Fix:**
```bash
cd /opt/community-node
ls -la .env    # verify it exists
cat .env       # verify all variables are populated
```

Create from the template if missing:
```bash
cp .env.template .env
nano .env      # fill in all values
```

---

### Conduit (Matrix) won't start — SSL certificate error

**Symptom:** `docker logs conduit` shows certificate errors. Matrix client can't connect.

**Cause:** SSL certificates either don't exist yet or are expired.

**Fix:**
```bash
certbot renew --dry-run    # test renewal
certbot renew              # renew if dry-run succeeds
docker compose restart nginx conduit
```

Verify cert is valid:
```bash
openssl s_client -connect matrix.yourdomain.com:443 </dev/null 2>&1 | grep "Verify return code"
```
Expected: `Verify return code: 0 (ok)`

---

### Conduit admin room commands don't work

**Symptom:** Commands sent to `@conduit:yourdomain.com` are ignored or return errors.

**Cause 1:** The admin room is encrypted. Conduit's admin bot cannot participate in E2EE rooms.

**Fix:** Create a new unencrypted room and invite `@conduit:yourdomain.com`. Use only that room for admin commands.

**Cause 2:** You're not using the admin account. Only the first registered user (admin) has control.

---

### Element Web loads but can't log in

**Symptom:** Element Web loads the login screen but authentication fails.

**Cause 1:** Homeserver URL is wrong. Element is configured to point to `matrix.yourdomain.com` but you're accessing it from a LAN IP.

**Fix:** Verify `element-config.json` has the correct homeserver URL for your deployment. On LAN, the homeserver is `http://192.168.8.10:6167` or the LAN-accessible Matrix URL.

**Cause 2:** Conduit is not running.
```bash
docker compose ps    # check conduit status
docker logs conduit  # check for errors
```

---

### Cloudflare tunnel is not routing traffic

**Symptom:** External domain (element.yourdomain.com) returns 502 or times out.

**Fix:**
```bash
docker logs cloudflared    # look for connection errors
```

If tunnel shows disconnected:
```bash
docker compose restart cloudflared
```

Verify the tunnel token in `.env` matches the token in Cloudflare Zero Trust > Networks > Tunnels.

---

### AdGuard Home blocks internal services

**Symptom:** After enabling AdGuard, node services stop resolving by hostname.

**Fix:** Add custom DNS rewrites in AdGuard Home (Settings > DNS Rewrites) for your local services:
```
matrix.yourdomain.com → 192.168.8.10
element.yourdomain.com → 192.168.8.10
```
This ensures local resolution goes to the Pi instead of the external IP.

---

## ATAK

### ATAK can't connect to OpenTAK Server — connection refused

**Symptom:** ATAK shows "Connection failed" or times out when trying to reach the server.

**Check 1:** Is OTS running?
```bash
ssh pi@192.168.8.20
sudo systemctl status opentakserver
```

**Check 2:** Is ATAK using the right IP and port?
- IP: `192.168.8.20`
- SSL port: `8089`
- TCP port (insecure): `8088`

**Check 3:** Is the device on the CommunityNode WiFi? ATAK over LAN only works when on the same network as the node.

**Check 4:** For remote access via VPN — is the device connected to Headscale? Check in Headscale admin or run `tailscale status` on the device.

---

### ATAK manual enrollment fails — truststore password rejected

**Symptom:** ATAK asks for truststore password during manual setup and rejects the entered value.

**Default password:** `atakatak`

If you changed this during OTS installation, retrieve it from your secrets file. There is no way to recover the truststore password other than from your records — if lost, you must regenerate the truststore in OTS and re-enroll all clients.

**Where it's set:** OTS admin console > Certificate Enrollment > Truststore settings.

---

### ATAK positions stop updating / COT not flowing

**Symptom:** Team members are connected but positions don't update on the map.

**Diagnosis:**
```bash
ssh pi@192.168.8.20
sudo systemctl status opentakserver
sudo journalctl -u opentakserver -n 50
```

Look for: database connection errors, memory pressure, or COT parser failures.

**Common cause:** OTS PostgreSQL database ran out of space (Monero sync fills the NVMe, OTS shares it).

```bash
df -h    # check disk usage
```

If disk is full, the Monero node is the most likely culprit — prune the blockchain or add storage.

---

### Reporting strategy — positions update inconsistently

**Symptom:** Some team members show real-time positions, others are stale.

**Cause:** ATAK reporting mode defaults to "Dynamic" which only updates when the device moves. For event use, all EUDs should be set to "Consistent" (updates on a fixed interval regardless of movement).

**Fix (per device):** ATAK > Settings > Show All > Reporting Strategy > Consistent

This cannot be set server-side; each operator must change it on their device.

---

## Monero

### Monerod appears hung — no sync progress

**Symptom:** `monerod status` shows height that isn't increasing, or systemd says the service is running but blockchain is at 0%.

**Cause:** Monero blockchain sync takes 24-72 hours on a Pi. This is normal. Do not restart monerod during sync unless you have confirmed it is actually stuck (no disk activity for 30+ minutes).

**Check progress:**
```bash
ssh pi@192.168.8.20
sudo journalctl -u monerod -n 20
```

Look for lines like: `Synchronized 2500000/3264185, net hash 3.24 GH/s`

**If actually stuck:**
```bash
sudo systemctl stop monerod
rm /opt/monero/data/p2pstate.bin    # clears stale peer list
sudo systemctl start monerod
```

---

### Monero RPC returns authentication error

**Symptom:** Wallet software or status scripts get 401 from `192.168.8.20:18089`.

**Cause:** RPC digest credentials are wrong. The password is set in `monerod.conf` and must match what your wallet/script uses.

**Fix:** Check `monerod.conf` for `rpc-login=username:password`. Update your wallet config to match.

---

## Reticulum / Meshtastic

### RNode not initializing

**Symptom:** Reticulum shows no LoRa interface. `rnsd` logs show interface error.

**Check:** Is the LEFT Heltec V3 flashed with RNode firmware (not Meshtastic)?
```bash
rnodeconf /dev/ttyUSB0 --info
```

If it shows Meshtastic firmware, you have the devices swapped. LEFT = RNode, RIGHT = Meshtastic.

---

### Meshtastic not appearing in ATAK

**Symptom:** Meshtastic devices are visible in the Meshtastic app but don't show up in ATAK.

**Check:** Is the Meshtastic ATAK plugin installed and configured to point to the ATAK server at `192.168.8.20:8089`?

The plugin creates a local bridge between Meshtastic and ATAK. Without it, the two systems are independent.

---

## Tor / I2P

### .onion addresses not resolving

**Symptom:** Tor Browser can't reach `.onion` addresses for Element or Matrix.

**Check:** Is the Tor container running?
```bash
docker compose ps tor
docker logs tor
```

**Check:** Are the hidden service directories populated?
```bash
ls /opt/community-node/data/tor/
```
Each service should have a `hostname` file with the `.onion` address.

**Important:** If you delete the Tor data directory or lose `private_key` files, your `.onion` addresses change permanently. Back up the entire `data/tor/` directory.

---

## General Diagnostics

### Quick health check (run from field laptop or any SSH session)

```bash
# Pi #1 (comms)
ssh pi@192.168.8.10 'docker compose -f /opt/community-node/docker-compose.yml ps'

# Pi #2 (tactical)
ssh pi@192.168.8.20 'sudo systemctl status opentakserver monerod'

# Disk usage (both Pis)
ssh pi@192.168.8.10 'df -h /'
ssh pi@192.168.8.20 'df -h /'
```

### Service ports quick reference

| Service | Host | Port | Protocol |
|---------|------|------|----------|
| Element Web (LAN) | 192.168.8.10 | 8080 | HTTP |
| Community page | 192.168.8.10 | 8081 | HTTP |
| Matrix (Conduit) | 192.168.8.10 | 6167 | HTTP (internal) |
| Nginx / Matrix TLS | 192.168.8.10 | 443 | HTTPS |
| AdGuard Home | 192.168.8.10 | 3000 | HTTP |
| OTS web | 192.168.8.20 | 8080 | HTTP |
| OTS TCP (ATAK) | 192.168.8.20 | 8088 | TCP |
| OTS SSL (ATAK) | 192.168.8.20 | 8089 | TLS |
| OTS cert enroll | 192.168.8.20 | 8446 | HTTPS |
| ATAK enrollment page | 192.168.8.20 | 8447 | HTTPS |
| Mumble voice | 192.168.8.20 | 64738 | TCP/UDP |
| Monero RPC | 192.168.8.20 | 18089 | HTTP (localhost only — use Tailscale VPN) |
| Headscale | m2vpn.yourdomain.com | 443 | HTTPS (clearnet only) |
| GL.iNet admin | 192.168.8.1 | 80/443 | HTTP/HTTPS |
