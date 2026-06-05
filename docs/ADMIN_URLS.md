# Admin URL Reference — M2 Community Node + Homestead

Quick reference for all clearnet admin interfaces, tools, and services.
Pull `M2_SECRETS.md` from Obsidian for credentials.

---

## Cloudflare

| Resource | URL |
|---|---|
| Main dashboard | https://dash.cloudflare.com |
| DNS (capableenough.org) | https://dash.cloudflare.com/profile (select zone) |
| Zero Trust (tunnels, access) | https://one.dash.cloudflare.com |
| Tunnels (Connectors tab) | https://one.dash.cloudflare.com/networks/connectors |
| Workers (matrix-wellknown) | https://dash.cloudflare.com/workers |
| Redirect rules | https://dash.cloudflare.com (Rules > Redirect Rules) |

---

## M2 Community Node (Clearnet)

| Resource | URL |
|---|---|
| Element Web | https://communitynode.capableenough.org |
| Element Web (alt) | https://element.capableenough.org |
| Matrix API (homeserver) | https://m2-matrix.capableenough.org |
| Well-known discovery | https://m2.capableenough.org/.well-known/matrix/client |
| Community page | https://capableenough.org |
| OpenTAKServer | https://tak.capableenough.org |
| ATAK enrollment | https://atakenroll.capableenough.org |
| Headscale VPN | https://m2vpn.capableenough.org |

## M2 Community Node (LAN — 192.168.8.x)

| Resource | URL | Notes |
|---|---|---|
| GL.iNet router admin | http://192.168.8.1 | WiFi, DHCP, dnsmasq |
| Element Web (LAN) | http://192.168.8.10:8080 | No Cloudflare |
| OpenTAKServer (HTTP) | http://192.168.8.20:8080 | |
| OpenTAKServer (HTTPS) | https://192.168.8.20:8443 | |
| OTS cert enrollment | https://192.168.8.20:8446 | |
| Mosquitto MQTT | 192.168.8.20:1883 | TCP, no browser |
| Mumble voice | 192.168.8.20:64738 | TCP+UDP, use Mumla/Mumble app |

## M2 Tor Hidden Services

| Resource | .onion Address |
|---|---|
| Element Web | http://jnrdtdzc34sal2nyyzjh4maikxy7y67fkuu5zx2gntnp2osa5l5gzbad.onion |
| Matrix API | http://k2ewq24hwpslxojem3paguosn5d44hrk3prqnsjvwgmc7odj77ku24ad.onion |
| Community Page | http://wqbgfd7s4lxdli5766ny7hkkvy4sj7yiir2klzygpdyrlwtsfvdvycid.onion |

---

## M1 Homestead (Future — not live yet)

| Resource | Planned URL | Status |
|---|---|---|
| Element Web | https://element.capableenough.org | M2 must vacate first |
| Matrix API | https://matrix.capableenough.org | M2 must vacate first |
| Home Assistant | https://ha.capableenough.org | ce-homestead tunnel |
| M1 server name | capableenough.org | Permanent |

---

## GitHub

| Resource | URL |
|---|---|
| Profile | https://github.com/PapaSierra555 |
| M2-Community-Node repo | https://github.com/PapaSierra555/M2-Community-Node |
| ClaudeWorkflow repo | https://github.com/PapaSierra555/ClaudeWorkflow |
| SSH keys | https://github.com/settings/keys |
| Fine-grained PATs | https://github.com/settings/tokens?type=beta |
| Actions / CI | https://github.com/PapaSierra555/M2-Community-Node/actions |

---

## Claude / Anthropic

| Resource | URL |
|---|---|
| Claude web | https://claude.ai |
| Claude Code (web) | https://claude.ai/code |
| API console / usage | https://console.anthropic.com |
| API keys | https://console.anthropic.com/settings/keys |

---

## ProtonVPN / Proton

| Resource | URL |
|---|---|
| Proton account | https://account.proton.me |
| ProtonVPN dashboard | https://account.proton.me/vpn |
| Proton Drive (backups) | https://drive.proton.me |
| Proton Mail | https://mail.proton.me |

---

## Obsidian

| Resource | URL |
|---|---|
| Obsidian Sync dashboard | https://sync.obsidian.md |
| Account | https://obsidian.md/account |

---

## Matrix / Element Ecosystem

| Resource | URL |
|---|---|
| matrix.to (room deep-links) | https://matrix.to |
| Matrix spec | https://spec.matrix.org |
| Conduit docs | https://conduit.rs |
| Element Web releases | https://github.com/element-hq/element-web/releases |

---

## Meshtastic

| Resource | URL |
|---|---|
| Web flasher | https://flasher.meshtastic.org |
| Channel URL decoder | https://meshtastic.org/e/ |
| Docs | https://meshtastic.org/docs |
| Firmware releases | https://github.com/meshtastic/firmware/releases |

---

## OpenTAKServer / ATAK

| Resource | URL |
|---|---|
| OTS docs | https://opentak.org |
| ATAK CIV (Play Store) | https://play.google.com/store/apps/details?id=com.atakmap.app.civ |
| WinTAK | https://tak.gov (requires account) |
| iTAK (App Store) | https://apps.apple.com/us/app/itak |

---

## Headscale / Tailscale

| Resource | URL |
|---|---|
| Headscale docs | https://headscale.net |
| Headscale releases | https://github.com/juanfont/headscale/releases |
| Tailscale clients | https://tailscale.com/download |

---

## GoDaddy (Domain Registrar)

| Resource | URL |
|---|---|
| Domain management | https://dcc.godaddy.com/manage/capableenough.org/dns |
| Account | https://account.godaddy.com |

> Note: DNS is managed in Cloudflare, not GoDaddy. GoDaddy NS records point to Cloudflare.

---

*Pull credentials from Obsidian `z_Backups/M2_SECRETS.md` before any admin session.*
*Last updated: 2026-06-05*
