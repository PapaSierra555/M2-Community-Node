# Cloudflare Zero Trust Setup

This is a prerequisite for all clearnet access to your node. Without it, all services are LAN-only (which is fine for air-gapped deployments — skip this entire doc if that's your intent).

---

## What You're Building

```
Internet user
    ↓
Cloudflare Edge (your domain DNS)
    ↓ Zero Trust Tunnel
cloudflared (Docker container on Pi #1)
    ↓
Nginx reverse proxy (Pi #1)
    ↓
Individual services (Conduit, Element, OTS, Headscale)
```

The tunnel means your Pi never has to have a public IP or open firewall ports. All traffic flows outbound through the `cloudflared` container.

---

## Step 1 — Create Cloudflare Account and Add Domain

1. Go to cloudflare.com and create an account (free tier works)
2. Click **Add a Site**, enter your domain
3. Select the **Free** plan
4. Cloudflare will show you two nameservers (e.g., `ada.ns.cloudflare.com`)
5. Go to your domain registrar and update your nameservers to the two Cloudflare provides
6. Wait for DNS propagation (usually 5-30 minutes, up to 48 hours)
7. Cloudflare will email you when your domain is active

---

## Step 2 — Get Your Zone ID

1. In Cloudflare dashboard, click your domain
2. Scroll down on the right sidebar to **API** section
3. Copy **Zone ID** — save this to your secrets file

---

## Step 3 — Create an API Token

1. Cloudflare dashboard > top-right avatar > **My Profile** > **API Tokens**
2. Click **Create Token**
3. Use template: **Edit zone DNS**
4. Under **Zone Resources**: Select your specific domain
5. Click **Continue to summary** > **Create Token**
6. Copy the token — **you will only see it once**
7. Save it to your secrets file as `CLOUDFLARE_API_TOKEN`

---

## Step 4 — Enable Zero Trust

1. Cloudflare dashboard > left sidebar > **Zero Trust**
2. If prompted, choose a team name (e.g., `mynode`) — this becomes `mynode.cloudflareaccess.com`
3. Select **Free** plan (supports up to 50 users)
4. Zero Trust is now active on your account

---

## Step 5 — Create the Tunnel

1. Zero Trust dashboard > **Networks** > **Tunnels**
2. Click **Create a tunnel**
3. Select **Cloudflared** as the connector type
4. Name it (e.g., `community-node-pi1`)
5. Click **Save tunnel**
6. On the next screen, Cloudflare shows an install command. You only need the **token** from that command — it looks like:
   ```
   cloudflared tunnel run --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
7. Copy the full token string. Save it to your secrets file as `CLOUDFLARE_TUNNEL_TOKEN`
8. Add it to your Pi #1 `.env` file:
   ```
   CLOUDFLARE_TUNNEL_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

## Step 6 — Configure Tunnel Routes (Public Hostnames)

After creating the tunnel, click **Configure** on your tunnel, then go to **Public Hostnames**.

Add one hostname per service:

| Subdomain | Domain | Service | URL |
|-----------|--------|---------|-----|
| `matrix` | yourdomain.com | HTTP | `http://nginx:80` |
| `communitynode` | yourdomain.com | HTTP | `http://element:80` |
| `tak` | yourdomain.com | HTTP | `http://192.168.8.20:8080` |
| `headscale` | yourdomain.com | HTTP | `http://headscale:8080` |
| `atakenroll` | yourdomain.com | HTTP | `http://192.168.8.20:8447` |

> **Domain plan (pending):** M2's Element Web will be served at `communitynode.yourdomain.com`.
> `element.yourdomain.com` will be re-delegated to the M1 home Element server.
> Update nginx `element-config.json` base_url accordingly when this change is made.

**Important for Matrix:** Do NOT set "No TLS Verify" unless you are using self-signed certs internally. Cloudflare terminates TLS at the edge — internal traffic goes HTTP.

---

## Step 7 — Configure Access Policies (Optional but Recommended)

By default, all public hostnames are publicly accessible. For admin interfaces, add an Access policy:

1. Zero Trust > **Access** > **Applications**
2. Click **Add an application** > **Self-hosted**
3. Application name: `Headscale Admin` (or similar)
4. Application domain: `headscale.yourdomain.com`
5. Under **Policies**, add a policy requiring email OTP or your preferred auth method
6. Save

**Do NOT add Access policies to:**
- `matrix.yourdomain.com` — breaks Matrix federation
- `tak.yourdomain.com` — breaks public web map access

---

## Step 8 — DNS Records

Cloudflare automatically creates CNAME records pointing to your tunnel when you add public hostnames. Verify they exist:

1. Cloudflare dashboard > your domain > **DNS** > **Records**
2. You should see CNAMEs like:
   ```
   element    CNAME    <tunnel-id>.cfargotunnel.com
   matrix     CNAME    <tunnel-id>.cfargotunnel.com
   tak        CNAME    <tunnel-id>.cfargotunnel.com
   ```

If they're missing, add them manually pointing to `<your-tunnel-id>.cfargotunnel.com`.

---

## Step 9 — Verify Tunnel Is Running

After `docker compose up` on Pi #1:

```bash
docker logs cloudflared
```

Look for:
```
2026-01-01T00:00:00Z INF Connection established connIndex=0 ...
2026-01-01T00:00:00Z INF Connection established connIndex=1 ...
```

Four connections is normal and healthy. Zero connections means the token is wrong or the container can't reach Cloudflare.

---

## SSL Certificates (Let's Encrypt)

Cloudflare terminates TLS at the edge. Your Pis still need valid certs for services that clients connect to directly (not through Cloudflare) — specifically ATAK enrollment and the Matrix federation port.

```bash
# On Pi #1
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /etc/cloudflare/cloudflare.ini \
  -d matrix.yourdomain.com \
  -d element.yourdomain.com \
  -d headscale.yourdomain.com \
  --email your@email.com \
  --agree-tos --non-interactive
```

Create `/etc/cloudflare/cloudflare.ini`:
```ini
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
```

Set permissions:
```bash
chmod 600 /etc/cloudflare/cloudflare.ini
```

Auto-renewal is handled by certbot's systemd timer. Verify it's active:
```bash
systemctl status certbot.timer
```

---

## Troubleshooting Cloudflare

**Tunnel shows "Inactive" in dashboard:**
- Check `docker logs cloudflared` on Pi #1
- Verify `CLOUDFLARE_TUNNEL_TOKEN` in `.env` is correct and complete
- Restart: `docker compose restart cloudflared`

**504 Gateway Timeout through Cloudflare:**
- The backend service is not responding
- Check if the target service is running: `docker compose ps`
- Verify the hostname route URL is correct (right port, right container name)

**Matrix federation not working:**
- Confirm no Access policy is applied to `matrix.yourdomain.com`
- Test federation from an external server: https://federationtester.matrix.org
- Verify the `.well-known/matrix/server` endpoint returns your server address

**SSL cert renewal fails:**
- Verify Cloudflare API token still has DNS Edit permissions
- Check token hasn't expired in Cloudflare > My Profile > API Tokens
- Re-run certbot manually: `sudo certbot renew --force-renewal`
