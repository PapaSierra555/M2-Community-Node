# Maintenance Guide

Routine maintenance, service updates, and version management for the M2 Community Node.

---

## Version Philosophy

All Docker image versions are pinned in the `.env` files on each Pi. **Do not use `:latest`.** Uncontrolled updates have broken working configurations in the past — especially Conduit (Matrix homeserver) and OpenTAKServer, both of which have had breaking schema migrations between minor versions.

Update deliberately: read the upstream changelog, test in isolation if possible, update one service at a time.

---

## How to Update a Docker Service

The general pattern for any Docker service update:

```bash
# 1. Take a backup first (always)
cd /opt/community-node
tar czf ~/pre-update-backup-$(date +%Y%m%d).tar.gz config/ docker-compose.yml data/

# 2. Edit the version pin in .env
nano /opt/community-node/.env
# Change e.g. CONDUIT_VERSION=v0.10.12 to the new version

# 3. Pull the new image
docker compose pull <service-name>

# 4. Recreate the container
docker compose up -d <service-name>

# 5. Verify
docker compose ps
docker compose logs <service-name> --tail=50
```

If something breaks, roll back by reverting the `.env` version and re-running `docker compose up -d`.

---

## Service-Specific Notes

### Conduit (Matrix Homeserver)

Conduit stores its database in `/opt/community-node/data/conduit/`. Migrations run automatically on startup.

**Before updating:**
- Read the Conduit changelog at `https://conduit.rs/changelog`
- Check for any breaking changes to `conduit.toml` configuration keys
- Back up `data/conduit/` specifically — it contains the full Matrix database

**After updating:**
```bash
docker compose logs conduit --tail=100
```

Look for `Migration complete` or any `ERROR` lines. If Conduit exits immediately after an update, the logs will tell you whether it's a config key mismatch or a failed migration.

**Rollback:** Conduit does not support downgrade migrations. If a migration partially completes and fails, restore from the pre-update backup of `data/conduit/` before downgrading the image version.

---

### OpenTAKServer (OTS)

OTS runs as a native systemd service, not Docker. Updates use the OTS installer script.

**Before updating:**
```bash
# Dump the database
sudo -u postgres pg_dump opentakserver > ~/ots-db-backup-$(date +%Y%m%d).sql
```

**Update:**
```bash
# Download and run the OTS installer for the new version
# Check https://github.com/brian7704/OpenTAKServer for release instructions
# The installer handles service restarts and migrations
```

**After updating:**
```bash
sudo systemctl status opentakserver
sudo journalctl -u opentakserver -n 50
```

**Known issue:** After an OTS update, any client data packages (enrollment ZIPs) may need to be regenerated if the cert format or server metadata changed. Check the OTS web UI at `http://192.168.8.20:8080` and reissue enrollment packages if needed.

---

### Headscale

Headscale stores state in `/opt/tactical-node/data/headscale/`. Database migrations run automatically.

**Before updating:**
```bash
# Back up headscale state
cp -r /opt/tactical-node/data/headscale/ ~/headscale-backup-$(date +%Y%m%d)/
```

**After updating**, verify all nodes are still registered:
```bash
docker exec tactical-node-headscale-1 headscale nodes list
```

**Config file changes:** Headscale occasionally deprecates config keys between versions. If Headscale fails to start after an update, check `docker compose logs headscale` for `unknown field` or `deprecated key` errors and update `config/headscale/config.yaml` accordingly.

---

### Monero (monerod)

Monero requires periodic updates to stay on the correct hard fork version. Failure to update before a hard fork will cause the daemon to stop syncing.

**Check for upcoming hard forks:** Monitor `https://www.getmonero.org/resources/roadmap.html` and the Monero community channels.

**Update:**
```bash
# Edit the version pin in .env on Pi #2
nano /opt/tactical-node/.env
# Change MONEROD_VERSION to the new tag

docker compose pull monerod
docker compose up -d monerod
docker compose logs monerod --tail=50
```

Monero does not need a database migration — the blockchain data is forward-compatible. Downgrade is also safe as long as no hard fork boundary was crossed.

---

### Nginx

Nginx updates are low-risk. The config is fully templated and version changes rarely affect behavior.

```bash
# Update version in .env, pull, recreate
docker compose pull nginx
docker compose up -d nginx
```

Verify with `curl -I http://192.168.8.10:8080` — should return a 200 from Element.

---

### Cloudflared

Cloudflare updates the tunnel client frequently. The tunnel token is version-independent — updating only the binary.

```bash
docker compose pull cloudflared
docker compose up -d cloudflared
```

Verify the tunnel is active in the Cloudflare Zero Trust dashboard under **Networks → Tunnels**.

---

### AdGuard Home

AdGuard stores its config in `/opt/community-node/data/adguard/`. Config format is stable across versions.

```bash
docker compose pull adguard
docker compose up -d adguard
```

After updating, verify the DNS rewrites are still present: **AdGuard dashboard → Filters → DNS rewrites**. Rewrites are stored in `AdGuardHome.yaml` inside the data volume and survive updates, but verify before declaring success.

---

## OS and Security Updates

Both Pis run `unattended-upgrades` for security patches only (configured in Phase 3). This does NOT update Docker images or application software — only OS-level security fixes.

Manually check for and apply OS updates quarterly:

```bash
sudo apt update && sudo apt upgrade -y
```

Reboot after kernel updates:
```bash
sudo reboot
```

Allow ~3 minutes for full startup before checking services.

---

## Checking What's Outdated

To see if a pinned Docker image has a newer version available:

```bash
# Pull the latest for a given image tag to compare digests
docker pull matrixconduit/matrix-conduit:v0.10.12
# If "Image is up to date" — you have the latest of that pin
# Check upstream release page for newer version tags
```

For a full inventory of what's running:

```bash
# On Pi #1
docker compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}"

# On Pi #2
docker compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}"
```

---

## Log Rotation

Docker logs are managed by the default JSON log driver. On a long-running node, logs can accumulate. Add log limits to `docker-compose.yml` services if disk becomes a concern:

```yaml
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
```

Check current log sizes:

```bash
du -sh /var/lib/docker/containers/*/
```

---

## Credential Rotation

| Credential | Rotation approach |
|---|---|
| Headscale auth keys | Expire automatically — generate new keys in Headscale dashboard before old ones expire |
| Cloudflare API tokens | Rotate in Cloudflare dashboard; update `M2_SECRETS.md` and re-export to `.env` |
| Matrix bot token | Regenerate via Element (log out/in the bot account); update `M2_SECRETS.md` |
| OTS admin password | Admin > Users > administrator > change password (not via Profile) |
| Monero wallet RPC password | Update in systemd unit file, restart `monero-wallet-rpc` |

After rotating any credential: update `M2_SECRETS.md` locally and your encrypted backup copy.
