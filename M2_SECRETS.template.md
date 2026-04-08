# M2 Community Node — Secrets Reference

**DO NOT COMMIT THE FILLED VERSION OF THIS FILE.**

Copy this template to `M2_SECRETS.md` and fill in your actual credentials.
`M2_SECRETS.md` is gitignored — it stays local only.

Keep a printed copy with the node for field deployment. Store securely.

---

## WiFi Networks

| SSID | Band | Password |
|---|---|---|
| `NodeAdmin` | 5GHz main | |
| `CommunityNode` | 5GHz guest | |

## Router Admin

| Item | Value |
|---|---|
| GL.iNet admin URL | `http://192.168.8.1` |
| Admin password | |

## Pi Access

| Host | IP | User | Auth |
|---|---|---|---|
| comms | 192.168.8.10 | ps | SSH key (no password) |
| tactical | 192.168.8.20 | ps | SSH key (no password) |

## Matrix / Conduit

| Item | Value |
|---|---|
| Homeserver domain | `yourdomain.com` |
| Registration token | |
| Admin user | |
| Admin password | |

## Monero

| Item | Value |
|---|---|
| Wallet name | community |
| Wallet encryption password | |
| RPC username | community |
| RPC password | |
| Daemon RPC address | `127.0.0.1:18081` |
| Wallet RPC address | `127.0.0.1:18083` |

## Headscale VPN

| Item | Value |
|---|---|
| Headscale URL | `https://m2vpn.yourdomain.com` |
| Admin API key | |
| Auth key (expires) | |
| Auth key expiry date | |

## Cloudflare

| Item | Value |
|---|---|
| Connector name | |
| Connector token | |
| DNS zone | `yourdomain.com` |
| DDNS API token | |
| Certbot DNS API token | |
| Tunnel routes | `matrix.yourdomain.com`, `element.yourdomain.com`, `tak.yourdomain.com`, `m2vpn.yourdomain.com` |
| Cloudflare Access | Email OTP enabled, approved operator emails listed in Zero Trust dashboard |

## Tor Hidden Services

| Service | .onion address |
|---|---|
| Element Web | |
| Matrix API | |
| Community Page | |

## Mosquitto MQTT

| Item | Value |
|---|---|
| Broker address | `192.168.8.20:1883` |
| Username | |
| Password | |

## OpenTAKServer

| Item | Value |
|---|---|
| Web UI (HTTP) | `http://192.168.8.20:8080` |
| Web UI (HTTPS) | `https://192.168.8.20:8443` |
| CoT TCP port | `192.168.8.20:8088` |
| SSL CoT port | `192.168.8.20:8089` |
| Certificate enrollment | `https://192.168.8.20:8446` |
| Static HTTPS (enrollment page) | `https://atakenroll.yourdomain.com:8447` |
| OTS admin username | `administrator` |
| OTS admin password | |
| OTS field username | `field` |
| OTS field password | |
| OTS viewer username | `viewer` |
| OTS viewer password | |
| PostgreSQL password | |
| RabbitMQ username | `guest` |
| RabbitMQ password | `guest` (must match default — OTS bug hardcodes default creds) |
| SECRET_KEY | |

> **Password change:** Admin > Users > click administrator > change password. NOT in Profile.

## Mumble Voice Server

| Item | Value |
|---|---|
| Server address | `192.168.8.20:64738` |
| Protocol | TCP + UDP |
| SuperUser username | `SuperUser` |
| SuperUser password | |

> ATAK users connect via Mumla app (Play Store). Server address: `192.168.8.20`, port: `64738`.

## Notes

- Print this document and laminate for field use
- Store digital copy in password manager only
- Rotate Headscale auth keys before expiry
- Update this document when any credential changes
- **NEVER commit M2_SECRETS.md to git**
