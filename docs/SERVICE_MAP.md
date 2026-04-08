# M2 Community Node — Service Map & Admin Field Card

Quick reference for all hosted services, access paths, and admin scenarios.

---

## Network Access Contexts

| Context | Your IP | Can reach |
|---|---|---|
| **NodeAdmin WiFi** (admin SSID) | 192.168.8.x | Everything |
| **CommunityNode WiFi** (guest SSID) | 192.168.8.x | Element, OTS web map only |
| **Clearnet / off-site** | public IP | Cloudflare tunnel services only |
| **Tor** | — | .onion hidden services |

---

## Pi #1 — comms (192.168.8.10)

Hosts: Matrix/Conduit, Element Web, Nginx, Cloudflared tunnel, Tor, I2P, AdGuard Home

| Service | LAN URL | Clearnet URL | Notes |
|---|---|---|---|
| **Element Web** | `http://192.168.8.10:8080` | `https://communitynode.yourdomain.com` | Matrix chat client |
| **Matrix federation** | `http://192.168.8.10` | `https://matrix.yourdomain.com` | Conduit homeserver |
| **AdGuard Home** | `http://192.168.8.10:3000` | — | DNS filtering admin |
| **Element (Tor)** | `YOUR_ELEMENT_ONION_ADDRESS.onion` | — | Anonymous access |
| **Matrix API (Tor)** | `YOUR_MATRIX_ONION_ADDRESS.onion` | — | Anonymous federation |
| **Community page (Tor)** | `YOUR_COMMUNITY_ONION_ADDRESS.onion` | — | Public info page |
| **Matrix federation test** | — | `https://federationtester.matrix.org` | External health check |

---

## Pi #2 — tactical (192.168.8.20)

Hosts: OpenTAK Server, Headscale, Mumble, Mosquitto MQTT, Monerod, Reticulum/NomadNet

| Service | LAN URL | Clearnet URL | Notes |
|---|---|---|---|
| **OTS Web UI (HTTP)** | `http://192.168.8.20:8080` | `https://tak.yourdomain.com` | Admin + web map |
| **OTS Web UI (HTTPS)** | `https://192.168.8.20:8443` | — | Secure local access |
| **ATAK enrollment** | `https://192.168.8.20:8446` | `https://atakenroll.yourdomain.com:8447` | Device cert enrollment |
| **Headscale admin** | `https://m2vpn.yourdomain.com` | `https://m2vpn.yourdomain.com` | VPN management UI |
| **Mumble voice** | `192.168.8.20:64738` | — | TCP+UDP, use Mumla on Android |
| **MQTT broker** | `192.168.8.20:1883` | — | Auth required |
| **MQTT WebSocket** | `192.168.8.20:9001` | — | Browser clients |

---

## Network Infrastructure

| Device | LAN URL | Notes |
|---|---|---|
| **GL.iNet router** | `http://192.168.8.1` | Gateway, DHCP, AP isolation |
| **TP-Link switch** | — | Unmanaged, no web UI |

---

## Brave Bookmark Set — M2 Node Admin

Copy these into a bookmark folder called **M2 Node**.

### Always accessible (NodeAdmin WiFi)
```
GL.iNet Router          http://192.168.8.1
AdGuard Home            http://192.168.8.10:3000
Element (local)         http://192.168.8.10:8080
OTS Web UI              http://192.168.8.20:8080
OTS Web UI (HTTPS)      https://192.168.8.20:8443
ATAK Enrollment (LAN)   https://192.168.8.20:8446
Headscale Admin         https://m2vpn.yourdomain.com
```

### Clearnet (any internet connection)
```
Element                 https://communitynode.yourdomain.com
TAK Web Map             https://tak.yourdomain.com
ATAK Enrollment         https://atakenroll.yourdomain.com:8447
Headscale Admin         https://m2vpn.yourdomain.com
Matrix Fed Test         https://federationtester.matrix.org
```

### Tor (Tor Browser only)

> **Your .onion addresses are unique to your node.** They are generated automatically when Tor starts for the first time and will differ from any addresses shown in documentation or examples. To find yours after deployment:
> ```bash
> # On Pi #1
> sudo cat /opt/community-node/data/tor/hidden_service_element/hostname
> sudo cat /opt/community-node/data/tor/hidden_service_matrix/hostname
> sudo cat /opt/community-node/data/tor/hidden_service_community/hostname
> ```
> Record these in your `M2_SECRETS.md`. If you lose the Tor private keys (see DISASTER_RECOVERY.md), new .onion addresses are generated and all QR codes must be reprinted.

```
Element                 YOUR_ELEMENT_ONION_ADDRESS.onion
Matrix API              YOUR_MATRIX_ONION_ADDRESS.onion
Community Page          YOUR_COMMUNITY_ONION_ADDRESS.onion
```

---

## Admin Scenarios — Quick Reference

### "Node is up, I'm on NodeAdmin WiFi"
Full access. Use LAN URLs. SSH: `ssh comms` / `ssh tactical` (Tailscale) or `ssh pi1` / `ssh pi2` (LAN).

### "I need to check if services are healthy remotely"
- Matrix federation: `https://federationtester.matrix.org` → enter `yourdomain.com`
- OTS web map: `https://tak.yourdomain.com`
- Element: `https://communitynode.yourdomain.com`
- Headscale: `https://m2vpn.yourdomain.com/health` → should return `{"status":"pass"}`

### "An operator can't connect ATAK"
Three enrollment paths (see `ATAK_CONNECTIVITY.md`):
1. **LAN direct** — ATAK server: `192.168.8.20`, port `8088` (TCP) or `8089` (SSL)
2. **Cert enrollment** — browser to `https://192.168.8.20:8446`, download profile
3. **Clearnet** — enrollment page at `https://atakenroll.yourdomain.com:8447`

### "Matrix registration — onboarding a new user"
1. Log in to Element as `@admin:yourdomain.com`
2. Share registration token from `M2_SECRETS.md` — or generate a new one-time token in Element Admin

### "Router/network issue"
1. Browser → `http://192.168.8.1` (GL.iNet admin)
2. Check DHCP leases, WiFi clients, WAN status
3. AdGuard DNS: `http://192.168.8.10:3000`

### "SSH into nodes — off-site"
Requires M2 Headscale (m2-mode on field laptop or Windows connected to M2 Headscale):
```bash
ssh comms      # 100.64.1.2
ssh tactical   # 100.64.1.1
```

### "SSH into nodes — on NodeAdmin WiFi"
```bash
ssh pi1        # comms  → 192.168.8.10
ssh pi2        # tactical → 192.168.8.20
```

---

## Service Ports — Quick Reference

| Port | Protocol | Service | Host |
|---|---|---|---|
| 80 | TCP | Nginx HTTP | comms |
| 443 | TCP | Nginx HTTPS / Headscale | comms / tactical |
| 3000 | TCP | AdGuard Home | comms |
| 8080 | TCP | Element Web / OTS HTTP | comms / tactical |
| 8088 | TCP | ATAK CoT (plain) | tactical |
| 8089 | TCP | ATAK CoT (SSL) | tactical |
| 8443 | TCP | OTS HTTPS | tactical |
| 8446 | TCP | ATAK cert enrollment | tactical |
| 8447 | TCP | ATAK enrollment (clearnet) | tactical |
| 9001 | TCP | MQTT WebSocket | tactical |
| 1883 | TCP | MQTT broker | tactical |
| 18081 | TCP | Monerod RPC (local only) | tactical |
| 50443 | TCP | Headscale gRPC | tactical |
| 64738 | TCP/UDP | Mumble voice | tactical |

---

*Reference: `M2_SECRETS.md` for credentials | `ATAK_CONNECTIVITY.md` for enrollment detail | `EVENT_RUNBOOK.md` for day-of ops*
