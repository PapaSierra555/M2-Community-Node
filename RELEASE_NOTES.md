# M2 Community Node — Release Notes

## v1.0.0

**First public release.**

![M2 Community Node](https://github.com/PapaSierra555/M2-Community-Node/releases/download/v1.0.0/node-photo.jpg)

This is a complete, field-tested build plan for a self-contained community communications node — dual Raspberry Pi 5 in an 8U 10" mini-rack. Everything required to replicate it from scratch is in this repository.

---

### Before You Start — Read This

**This is a build plan, not a plug-and-play installer.** It is a step-by-step blueprint for constructing and configuring a multi-service communications node from commodity hardware. Prior hardware or networking expertise is not a hard requirement — but only with realistic expectations and the right support.

**This node was built with the help of an AI companion assisting at every step** — walking through commands, catching config errors, explaining tradeoffs, and adapting to the specific hardware and environment as problems came up. That approach is strongly recommended for anyone attempting this build.

The build guide has every command and every config, but this is a complex, multi-service system. Standing it up involves:

- Configuration decisions that depend on your domain, hardware, and use case
- Gotchas in third-party software (OpenTAKServer, Conduit, Headscale) that are not documented upstream
- Network and firewall behaviors that vary by router model and ISP
- Security choices around access tiers, certificates, and credentials that require deliberate decisions
- Unexpected states during setup that require diagnosis, not just copy-paste

**The recommendation:** Work through the build guide with an AI assistant — Claude, ChatGPT, or similar — that can read the docs alongside you, adapt commands to your environment on the fly, and help you reason through the decisions. This is not a project where you follow a guide blindly. It is a project where you follow the guide with a knowledgeable collaborator and build something that actually fits your community.

---

### What's Included

**Services (Comms Pi — Pi #1)**
- Matrix / Conduit homeserver
- Element Web client
- Nginx reverse proxy with Cloudflare Tunnel for clearnet access
- Tor hidden services (Element, Matrix API, community page)
- I2P node
- AdGuard DNS with LAN split-DNS

**Services (Tactical Pi — Pi #2)**
- OpenTAKServer — ATAK/TAK shared situational awareness
- Headscale — self-hosted VPN (WireGuard)
- Mumble voice server
- Meshtastic LoRa mesh bridge (via Mosquitto MQTT)
- Reticulum / RNode encrypted mesh transport
- Monero full node (restricted RPC, community privacy node)

**Kiosk Display**
- Touch-screen status dashboard (service health, system vitals, QR codes)
- Offline map viewer (PMTiles street-level + DTED2 terrain)

**Documentation**
- 17 reference documents covering every phase of the build
- Full hardware BOM with part numbers and pricing
- Event operations runbook
- Troubleshooting guide (symptom-based, field-usable)
- ATAK connectivity guide (3 access tiers: LAN, clearnet, VPN)
- Disaster recovery procedures

**Print-ready PDFs**
- Build book, event runbook, wiring diagram, ATAK field card, troubleshooting reference
- Community outreach materials (booth handouts, recruiting cards)

**Tooling**
- ReportLab PDF generators (OFL fonts bundled — works on any machine)
- Status bot (Matrix posts every 12h)
- ATAK data package builder
- QR code generators for WiFi, app stores, onion services
- Vinyl label generators for rack panels
- instance.conf template — one file controls all instance-specific values

---

### Hardware

**Recommended build (~$994)**
- 2× Raspberry Pi 5 16GB
- 8U 10" mini-rack (wall-mount capable)
- 2× NVMe HAT + 1TB NVMe SSD each
- GL.iNet Beryl AX (Wi-Fi 6 router)
- 2× Heltec V3 LoRa radios
- 10" touch monitor
- UPS module + LiPo battery

**Budget build (~$889)** — single Pi variant covered in docs.

Full BOM with ASINs and current pricing: [docs/HARDWARE_BOM.md](docs/HARDWARE_BOM.md)

---

### Configuration

All instance-specific values (IP addresses, domain names, WiFi credentials, event details) live in `instance.conf` — gitignored, never committed. A fully commented template is provided at `instance.conf.template`.

Secrets (tokens, passwords, API keys) live in `M2_SECRETS.md` — also gitignored. Template at `M2_SECRETS.template.md`.

No credentials or personal data are present in this repository.

---

### Known Limitations / Gotchas

- **Tor .onion addresses** are generated on first startup and are unique to each node. The addresses in docs and templates are placeholders — yours will be different. Commands to retrieve them are in [docs/SERVICE_MAP.md](docs/SERVICE_MAP.md).
- **OpenTAKServer** password reset follows a non-standard procedure (HMAC+argon2). The correct steps are documented in [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
- **Conduit Matrix** works best on room version 10 — there is a known auth bug in v11/v12 for creator power levels. The event space script pins v10 for this reason.
- **AT&T Fiber** blocks Monero p2p — VPN required. Documented in [docs/MONERO_NODE.md](docs/MONERO_NODE.md).
- **Headscale on Tailscale clients** overrides `/etc/resolv.conf` on Pi #1 — local DNS entries require `/etc/hosts` overrides, not AdGuard. Documented in the status bot deploy note.
- **Reticulum config** must be validated against the installed version — the example configs in docs may require adjustment for your RNode firmware.

---

### Special Thanks

This project would not exist without the vision, community, and mission of three organizations that helped build the idea, necessity, and reasoning behind it:

- **[Carolina Capabilities Co-Op](https://www.carolinacapabilitiesco-op.com/)** — community resilience and preparedness, built from the ground up
- **[Light Fighter Manifesto](https://lightfightermanifesto.org/)** — the framework and philosophy driving the mission
- **[Light Fighter Homefront Initiative](https://lightfighterhomefront.org/)** — putting that mission into practice at the community level

The inspiration and architecture for this project couldn't have been done without the first iteration built by **Christopher M. Rance**. Go support the group or join a chapter — [instagram.com/christopher_m_rance](https://www.instagram.com/christopher_m_rance/)

---

### License

[CC BY-NC-SA 4.0](LICENSE) — build one for your community, adapt it, share it. You cannot sell it. Derivative works use the same license.
