# Element Administration Plan — M2 Community Node

## Architecture

- **M2 (Conduit)** — Standalone field server, portable, local comms during deployment
- **M1 (Synapse, optional)** — If you run a separate always-on home server, it can serve as the primary identity and persistent room host. This is an optional addition; M2 runs fully standalone without it.
- **Federation between M2 and M1 is not recommended** — Conduit-to-Conduit federation is unreliable. Treat them as independent servers with overlapping users if both are deployed.
- **Reticulum/NomadNet** on M2 serves as disconnected-mode fallback when Matrix is unreachable

## Space & Room Structure

### Admin Space (Private, Invite-Only)
- `#general` — operator/admin chat
- `#server-status` — bot-posted health updates
- `#alerts` — critical notifications (disk full, service down, UPS on battery)
- `#media` — photo/file sharing

### Community Space (Invite-Only, Dynamic Rooms)

The Community Space is the operational backbone. Persistent rooms exist for standing capabilities, but **new rooms are spun up on demand** based on mission, emergency, or event needs. Rooms are created and archived as the situation requires — the space is alive, not static.  This Lives on the M2 Community Node.

**Standing rooms (always present):**
- `#comms` — radio, mesh, Reticulum, Meshtastic
- `#medical` — first aid, trauma, community health
- `#agriculture` — food production, permaculture
- `#security` — physical security, situational awareness
- `#logistics` — supply chain, transportation, events
- `#general` — social, announcements
- `#onboarding` — encryption setup help, welcome resources

**Dynamic rooms (spun up as needed):**
- Mission-specific: `#hurricane-prep-2026`, `#water-response-team`, `#grid-down-drill`
- Event coordination: `#ccc-june-planning`, `#field-day-logistics`
- Emergency: `#active-situation`, `#evacuation-coord`
- Created by admin/moderator, scoped to need, archived or deleted when complete

---

### Event Demo Space — Example (Adapt for Your Event)

> **This section is an example** of how to configure M2 for a temporary public event deployment. The specific event details below (CCC26) are illustrative — adapt the room names, registration settings, and cleanup procedures for your own event. The operational pattern (open registration + token, demo rooms, post-event wipe) applies to any public-facing deployment.

**Example Event:** Carolina Capabilities Initiative Weekend
**Example Dates:** June 13-14, 2026 (8 AM - 5 PM both days)
**Example Location:** Southeastern Institute of Manufacturing Technology (SiMT), Florence, SC

**Purpose:** Live demonstration of the M2 Community Node's Element server. Attendees experience encrypted group chat on fully self-hosted, air-gapped-capable infrastructure. Teams use it for real coordination during training exercises, proving the tactical value under field conditions.

**Access method:**
- NFC tap or QR code scan at the event → opens a custom registration/landing page
- **Auto-registration enabled** — open to all attendees, unlimited users
- **Relaxed restrictions** — no member caps per room, no bridger tracking; this is a demo, not an operational deployment
- QR/NFC link points to a custom landing page (not the default Element login)

**Landing page content:**
- What this is: self-hosted encrypted chat running on a portable Raspberry Pi node — no cloud, no data leaves the box
- Quick-start encryption setup (simplified 3-step guide)
- Demo rules: no PII, no illegal content, be respectful
- Time frame: **this space and all messages will be wiped after the event ends on June 14**
- Direct link to join the CCC26 Space after reading

**CCC26 rooms:**
- `#welcome` — read-only: event schedule, announcements, instructions
- `#general` — open chat for all attendees
- `#comms-demo` — live demo of radio/mesh integration (Meshtastic bridge, Reticulum, etc.)
- `#training-chat` — coordination channel for active training exercises
- `#feedback` — attendees leave thoughts on the platform and the node
- Additional rooms spun up as needed by event staff or training teams

**Post-event cleanup:**
- All CCC26 accounts deactivated
- All CCC26 rooms purged (messages + media)
- Auto-registration disabled
- CCC26 Space deleted from server
- Conduit reverts to invite-only mode

---

## OPSEC Rules (Community Space — NOT CCC26 Demo)

- No room exceeds ~10 members; split if community grows (`#comms-alpha`, `#comms-bravo`)
- Bridgers (people in 3+ rooms) tracked and flagged by admin
- Room history visibility: `joined` — no scrollback before join
- Plans scoped to single group; never shared between groups without consent
- Recruiting: only trust people YOU approached, not those who approached you

## Encryption Enforcement

- Element Web config: `"e2ee": { "default": true, "secure_backup_required": true }`, `"force_verification": true`
- Well-known file: `"io.element.e2ee": { "default": true, "force": true }`
- Only admins (PL 100) can disable encryption on a room
- Once encryption is enabled on a room, it cannot be disabled (Matrix protocol enforced)
- Custom welcome page with encryption setup instructions for new users

## Media Retention

- Conduit (M2): 20MB upload limit, cron job to purge old media from media directory
- Synapse (M1, future): `local_media_lifetime: 180d`, `remote_media_lifetime: 30d`, 50MB limit
- Monitor media store size, alert at 80% via status bot

## Status Bots (matrix-nio, Python)

- `@statusbot` — one per server, posts to `#server-status`
- System health: CPU, RAM, disk, temp, uptime
- Docker container status: running/stopped/restarting
- Service-specific: Monero sync height, Headscale nodes, Mosquitto clients
- Scheduled posts every 15 min; immediate alerts to `#alerts` on threshold breach
- Built with matrix-nio (pure Python, ARM64 compatible, E2EE support)

## User Onboarding Flow

### Standard (Community/Family)
1. Admin creates account via API (no open registration)
2. New user gets welcome DM from statusbot with setup instructions
3. User sets up key backup (Security & Privacy → Secure Backup)
4. User verifies session with admin in person (QR or emoji comparison)
5. Admin adds user to appropriate rooms (max 3-4 to start)
6. Custom Element welcome page reinforces encryption on first login

### CCC26 Demo (Event Only)
1. Attendee scans QR code or taps NFC at the event
2. Custom landing page: what it is, encryption quick-start, rules, time frame
3. Auto-registration creates account, user enters CCC26 Space
4. User lands in `#welcome` (read-only schedule/instructions) and `#general`
5. No in-person verification required — demo context, temporary accounts

## Roles

- **Admin** — Operator + trusted team members (1-2 people), PL 100
- **Moderator** — Promoted community members, PL 50
- **Member** — Standard users, limited per room, PL 0

## M1 Deployment (Future — After M1 Build)

**Purpose:** Always-on home server for persistent rooms and federation. M2 remains field-portable with no home dependency once M1 is live.

- Synapse on Docker host (`YOUR_M1_HOST_IP`) — N100/N150 mini PC or equiv.
- Element Web (same version as M2)
- PostgreSQL 16 for Synapse database
- matrix-nio status bot container
- Exposed via Caddy + Cloudflare Tunnel — no ports opened
