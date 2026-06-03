# M2 Community Node — ATAK Connectivity Guide

**Operator reference for onboarding users at each access tier.**

Three paths into the network. Pick the one that fits the user.

---

```
                        +---------------------+
                        |   New team member    |
                        |   needs map access   |
                        +----------+----------+
                                   |
                     +-------------+-------------+
                     |  Are they physically here? |
                     +-------------+-------------+
                            +--yes-+--no--+
                            |             |
                     +------+------+ +----+--------------------+
                     |  PATH A     | |  Do they need full ATAK |
                     |  Local WiFi | |  (CoT, GeoChat, PLI,    |
                     |  Full ATAK  | |   markers, missions)?   |
                     +-------------+ +----+--------------------+
                                     +--no-+--yes--+
                                     |             |
                              +------+------+ +----+-------------+
                              |  PATH B     | |  PATH C          |
                              |  Clearnet   | |  VPN + ATAK      |
                              |  Browser    | |  Operator only   |
                              +-------------+ +-----------------+
```

---

## Path A -- Local WiFi (Primary)

**Who:** Anyone physically at the node -- SAR volunteers, community members, field teams.

**What they get:** Full ATAK -- live position sharing, GeoChat, markers, missions, voice (Mumble), mesh relay (Meshtastic).

**Use cases:**

- Search and rescue operation at a state park
- Community event with distributed teams
- Training exercise with local volunteers
- Disaster response -- everyone gets on the same map in minutes

### Operator walkthrough -- someone walks up and wants to join

**What you need:** Your phone or laptop on the node WiFi, logged into the OTS Web UI.

**Step 1: Get the user on the WiFi**

Tell them to connect to `CommunityNode` WiFi. Give them the password from the printed card or read it to them. They do NOT need the admin WiFi -- `CommunityNode` has full access to the server.

**Step 2: Make sure they have ATAK installed**

They need ATAK-CIV from the Play Store (Android) or iTAK from the App Store (iPhone). If they don't have it, point them at the community page QR codes (`http://192.168.8.10:8081`) or hand them the field card.

**Step 3: Generate their enrollment QR code**

On your device (phone or laptop), open the OTS Web UI:

```
http://192.168.8.20:8080
```

Log in with the admin credentials. Then:

1. Navigate to **Certificates** (left sidebar)
2. Click **Generate Data Package**
3. Enter a callsign for this user (e.g., their name or assigned callsign)
4. Click **Generate**
5. OTS creates a client certificate + server connection profile bundled into a data package
6. Click **Show QR Code** on the generated package

**Step 4: User scans the QR code**

The user opens ATAK on their phone:

1. ATAK > Menu (three lines) > **Import** > **QR Code**
2. They scan the QR code from your screen
3. ATAK auto-imports the data package -- server connection, certificate, and truststore are all configured automatically
4. ATAK connects to the server within seconds

That's it. No manual server entry, no port numbers, no truststore passwords. The QR code handles everything.

**Step 5: User sets their callsign**

Settings > My Preferences > Callsign. Use their name or an assigned tactical callsign.

**Step 6: Verify**

- Their icon appears on the shared map
- Test GeoChat: have them send a message in the default channel
- If using Mumble: open Mumla, server `192.168.8.20`, port `64738`

### Fallback -- manual setup (if QR doesn't work)

If the QR scan fails (old phone, camera issues), the user can manually add the server in ATAK:

1. ATAK > Settings > Network > TAK Servers > Add

| Setting | Value |
|---|---|
| Server | `192.168.8.20` |
| Port | `8089` |
| Protocol | SSL |
| Enable authentication | Yes |
| Enroll for client certificate | Yes |
| Use default SSL/TLS certs | **No** (uncheck this) |
| Truststore password | `atakatak` |

2. ATAK will contact the server on port 8446, download and install the certificate automatically
3. The server connection switches to SSL on port 8089

OTS handles all the PKI -- it auto-generates a unique client certificate for each device that enrolls. You don't create certificates manually. The server does it.

**Time to onboard:** 2-5 minutes with QR code. 5-10 minutes manual.

---

## Path B -- Clearnet Browser (Remote Viewers)

**Who:** Remote team members, partner agencies, anyone with internet who needs situational awareness but does NOT need to be a CoT participant on the map.

**What they get:** Full OTS web map in a browser -- all team positions, markers, missions, live updates. View and monitor. No app install required.

**Use cases:**

- Team lead at home monitoring a field operation
- Partner agency watching the shared picture from their office
- Family member checking in on a SAR deployment
- After-action review from anywhere
- Briefing a remote stakeholder who needs to see the map right now

### Operator walkthrough -- someone remote needs to see the map

**What you need:** Access to the Cloudflare Zero Trust dashboard.

**Step 1: Add their email to the approved list**

You must add their email BEFORE they can log in. The OTS web map is gated behind Cloudflare Access -- only pre-approved emails receive the OTP code.

1. Open `dash.cloudflare.com`
2. Go to **Zero Trust** > **Access** > **Applications**
3. Find the `OTS Web Map` application > click **Edit**
4. Under the policy, find the **Include** rule (type: Emails)
5. Add the user's email address
6. **Save**

**Step 2: Send them the link**

Text, email, or Element message -- whatever works:

```
Web map: https://tak.yourdomain.com

To log in:
1. Open the link in any browser
2. Enter your email address
3. Check your inbox for a 6-digit code
4. Enter the code -- you're in
```

That's it. No app, no VPN, no configuration. Works on any phone, tablet, or computer with a browser.

**Step 3: Revoke access (when needed)**

Same path: Zero Trust > Access > Applications > Edit > remove their email from the Include rule. Access is cut immediately -- their next page load will be blocked.

**Time to onboard:** Under 60 seconds (add email, send link).

**Limitations:**

- They can see the map but do NOT appear as a position on it
- No GeoChat, no marker creation, no mission participation from the browser
- Requires internet access (the tunnel routes through Cloudflare)
- If you don't add their email, they can't get past the login screen

---

## Path C -- VPN + Full ATAK (Controlled Remote Access)

**Who:** Specific, trusted operators who need full ATAK participation from outside the node WiFi. This is NOT for general users. The operator personally sets this up for each individual.

**What they get:** Full ATAK over VPN -- identical to being on local WiFi. Live position sharing, GeoChat, markers, missions, everything. They appear on the map as a full team member.

**Use cases:**

- You (the node operator) connecting from home to manage your own server
- A co-operator in another city who helps run operations
- A SAR team lead who needs to participate from a remote EOC
- Pre-positioned team members before traveling to the node location

### Requirements

The remote user needs two apps on their Android phone:

1. **Tailscale** (Play Store) -- VPN client
2. **ATAK-CIV** (Play Store) -- tactical awareness

### Operator steps

**Step 1: Generate a VPN auth key (on tactical Pi)**

Headscale runs as a systemd service (not Docker). Use the binary directly.

```
[SSH -- tactical-lan]
sudo headscale preauthkeys create -c /opt/tactical-node/config/headscale/config.yaml --user 2 --expiration 24h
```

User IDs: `1` = admin (infrastructure), `2` = community (event attendees). For a one-time op use `--expiration 24h`. For a standing reusable key:

```
[SSH -- tactical-lan]
sudo headscale preauthkeys create -c /opt/tactical-node/config/headscale/config.yaml --user 2 --reusable --expiration 2160h
```

List current keys: `sudo headscale preauthkeys list -c /opt/tactical-node/config/headscale/config.yaml`

**Step 2: Send the user these instructions**

```
1. Install Tailscale from the Play Store
2. Open Tailscale > tap profile icon > Accounts > three-dot menu > "Use an alternate server"
3. Enter: https://m2vpn.capableenough.org
4. Paste the auth key I sent you
5. Tailscale connects -- you now have a VPN tunnel to the node

6. Open ATAK > Settings > Network > TAK Servers > Add
   Server: 192.168.8.20
   Port: 8089
   Protocol: SSL
   Check "Enroll for Client Certificate"
   Uncheck "Use default SSL/TLS Certificates"
   Truststore password: atakatak

7. Set your callsign: Settings > My Preferences > Callsign
8. You should appear on the shared map within seconds.
```

**Step 3: Verify the connection**

```
[SSH -- tactical-lan]
sudo headscale nodes list -c /opt/tactical-node/config/headscale/config.yaml
```

Confirm their device appears with an assigned IP (100.64.x.x range).

**Step 4: Revoke access when done**

```
[SSH -- tactical-lan]
sudo headscale nodes delete -c /opt/tactical-node/config/headscale/config.yaml --identifier <id>
```

The user's Tailscale immediately disconnects. No residual access.

### Security notes

- Each auth key is tied to an expiration -- it cannot be reused after it expires
- You control exactly who has access and can revoke instantly
- VPN traffic is encrypted end-to-end (WireGuard)
- The Headscale server only accepts connections with valid pre-auth keys
- Subnet routes (`192.168.8.0/24`) are already approved on both Pis -- remote users reach LAN services as if local
- Remote users should use `--accept-routes=true` in Tailscale to route to the LAN subnet

---

## Quick Reference

| | Path A: Local WiFi | Path B: Clearnet Browser | Path C: VPN + ATAK |
|---|---|---|---|
| **Location** | At the node | Anywhere with internet | Anywhere with internet |
| **App required** | ATAK-CIV | Browser only | Tailscale + ATAK-CIV |
| **Appears on map** | Yes | No | Yes |
| **GeoChat** | Yes | No | Yes |
| **Voice (Mumble)** | Yes | No | Yes (with Mumla) |
| **Meshtastic relay** | Yes (with radio) | No | No (no radio in range) |
| **Onboard time** | 2-5 min | Under 60 sec | 5-10 min |
| **Operator effort** | Hand them a QR code | Add email to approved list | Generate key, send instructions |
| **Who decides** | Anyone can join | Operator approves email | Operator generates key per person |
| **Revoke access** | They leave WiFi range | Remove email from list | Delete node from Headscale |

---

## Choosing the Right Path

**Default answer: Path A.** If they're here, they get ATAK on the WiFi. That's what the node is for.

**Remote viewer: Path B.** Fast, no friction, no app install. Good enough for most remote needs. If someone asks "can I see the map from home?" -- this is the answer.

**Remote operator: Path C.** Only when someone specifically needs to be a full participant on the ATAK map from a remote location. You personally set this up for them. They don't self-serve. You control the key, you control the expiration, you control the revocation.

---

## Element Chat -- The Glue

Regardless of path, all team members should join **Element** for persistent text communication:

- **Clearnet:** `https://communitynode.yourdomain.com`
- **On WiFi:** `http://192.168.8.10:8080` (direct to node)
- **Tor:** `.onion` address (see secrets reference)

Element works from anywhere, on any device, with full encryption. It's the coordination channel that ties all three paths together. ATAK is the map. Element is the chat.

---

v1.0
