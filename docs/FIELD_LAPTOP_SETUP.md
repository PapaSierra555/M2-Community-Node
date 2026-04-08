# Field Laptop Setup — Getac S400 G2

Primary IT/NetSec support laptop and M2 Community Node admin terminal.

**Hardware:** Getac S400 G2 (semi-rugged, MIL-STD-810G)
**OS:** Ubuntu 24.04.2 LTS
**Reserved IP:** 192.168.8.50 (NodeAdmin WiFi)
**Hostname:** `m2-field`

---

## Phase 1 — Ubuntu Install

### 1.1 Boot from USB
- Power on → press **F12** at Getac logo → select USB drive
- Select **Try or Install Ubuntu**

### 1.2 Pre-install hardware check (live desktop)
Run these before committing to install:
```bash
lspci | grep -i net
lspci | grep -i wifi
ip link show
lspci | grep -i vga
```
If WiFi shows up and connects → proceed. If not, document chipset and resolve first.

### 1.3 Install
- Double-click **Install Ubuntu**
- Installation type: **Minimal** (no LibreOffice, no extras)
- Disk: **Erase and install** (field-only machine)
- Enable **LVM + encryption** (LUKS) — adds boot passphrase, appropriate for field hardware
- Username: `ps`
- Hostname: `m2-field`
- Enable auto-login: No

### 1.4 First boot
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

---

## Phase 2 — Network Setup

### 2.1 Connect to M2 node WiFi
- SSID: `NodeAdmin` (5GHz)
- Password: see `M2_SECRETS.md`
- This is the admin network — both Pis are reachable from here

### 2.2 Reserve static IP on GL.iNet router
1. Open browser → `http://192.168.8.1` → log in
2. Network > LAN > DHCP > Static IP Binding
3. Add binding:
   - MAC address: run `ip link show` on field laptop, copy the MAC for the WiFi interface
   - IP: `192.168.8.50`
   - Hostname: `m2-field`
4. Save → reconnect WiFi to pick up the reservation

### 2.3 Verify IP
```bash
ip addr show
```
Should show `192.168.8.50` on the WiFi interface.

### 2.4 Test node reachability
```bash
ping -c 3 192.168.8.10
ping -c 3 192.168.8.20
ping -c 3 192.168.8.1
```
All three should respond.

---

## Phase 3 — SSH Access to Both Pis

### 3.1 Generate SSH key
```bash
ssh-keygen -t ed25519 -C "m2-field"
```
Accept default path (`~/.ssh/id_ed25519`). Set a passphrase.

### 3.2 Copy key to both Pis
```bash
ssh-copy-id pi@192.168.8.10
ssh-copy-id pi@192.168.8.20
```
Passwords: see `M2_SECRETS.md` (Pi Access section).

### 3.3 SSH config shortcuts
Create `~/.ssh/config`:
```
Host pi1
    HostName 192.168.8.10
    User ps
    IdentityFile ~/.ssh/id_ed25519

Host pi2
    HostName 192.168.8.20
    User ps
    IdentityFile ~/.ssh/id_ed25519
```

### 3.4 Test
```bash
ssh pi1 "hostname && uptime"
ssh pi2 "hostname && uptime"
```

---

## Phase 4 — Tools Install

```bash
sudo apt install -y nmap netcat-openbsd curl git python3 python3-pip wireshark tcpdump
```

```bash
sudo apt install -y net-tools traceroute dnsutils htop tree jq
```

Add user to wireshark group (capture without sudo):
```bash
sudo usermod -aG wireshark ps
```
Log out and back in for group to take effect.

---

## Phase 5 — Repo Clone

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/M2-Community-Node.git ~/M2-Community-Node
```

Keep this current before every deployment:
```bash
cd ~/M2-Community-Node && git pull
```

---

## Phase 6 — Offline Docs Folder

```bash
mkdir -p ~/Field
cp ~/M2-Community-Node/*.pdf ~/Field/
```

Field PDFs:
| File | Purpose |
|------|---------|
| `M2_Community_Node_One_Sheet.pdf` | Event flyer |
| `M2_Community_Node_Build_Book.pdf` | Build handout |
| `M2_Community_Node_Runbook.pdf` | Field ops guide |
| `M2_Rack_Wiring_Diagram.pdf` | Cable reference |
| `M2_ATAK_FieldCard.pdf` | Enrollment card |

Pin `~/Field` to the Files sidebar for fast access.

---

## Phase 7 — Browser Setup (Firefox)

Install bookmarks for all node services. All URLs on NodeAdmin WiFi unless noted.

**Bookmark folder: M2 Node**

| Name | URL |
|------|-----|
| Element (local) | `http://192.168.8.10:8080` |
| Element (clearnet) | `https://communitynode.yourdomain.com` |
| OTS Web Map | `http://192.168.8.20:8080` |
| OTS Web Map (HTTPS) | `https://192.168.8.20:8443` |
| AdGuard Home | `http://192.168.8.1:3000` |
| GL.iNet Router | `http://192.168.8.1` |
| Headscale (M2) | `https://m2vpn.yourdomain.com` |
| Pi #1 — comms | `http://192.168.8.10` |
| Pi #2 — tactical | `http://192.168.8.20` |
| Matrix Federation Test | `https://federationtester.matrix.org` |

Set Firefox homepage to `http://192.168.8.1` (router — first thing to check if network is broken).

---

## Phase 8 — Connectivity Test Checklist

Run this full check before every event:

```bash
# Node reachability
ping -c 2 192.168.8.1
ping -c 2 192.168.8.10
ping -c 2 192.168.8.20

# SSH to both Pis
ssh pi1 "sudo systemctl is-active docker"
ssh pi2 "sudo systemctl is-active opentakserver"

# Service ports
nc -zv 192.168.8.10 8080
nc -zv 192.168.8.20 8080
nc -zv 192.168.8.20 8088
nc -zv 192.168.8.20 8089
nc -zv 192.168.8.20 8446
```

---

## Phase 9 — Lid Label

Print and affix to inside of lid:

```
M2 Community Node — Admin Terminal
NodeAdmin WiFi: [password from secrets]
Pi #1 (comms):    192.168.8.10   ssh pi@192.168.8.10
Pi #2 (tactical): 192.168.8.20   ssh pi@192.168.8.20
Router:           192.168.8.1
This laptop:      192.168.8.50
```

---

## Phase 10 — Pre-Event Checklist

- [ ] `git pull` in `~/M2-Community-Node`
- [ ] `cp ~/M2-Community-Node/*.pdf ~/Field/`
- [ ] SSH connectivity to both Pis confirmed
- [ ] All browser bookmarks loading
- [ ] Wireshark launches without sudo
- [ ] Laptop fully charged

---

## Phase 11 — Core Apps

Install these after first boot:

```bash
sudo apt install -y remmina remmina-plugin-rdp remmina-plugin-vnc
sudo apt install -y smbclient cifs-utils
sudo apt install -y keepassxc
sudo apt install -y code
```

Via browser/installer:
- **Brave** — primary browser, sync bookmarks + passwords via Brave Sync
- **Obsidian** — knowledge base, cross-device sync via Obsidian Sync or Proton Drive
- **ProtonVPN** — download `.deb` from protonvpn.com, install for secure remote sessions

---

## Phase 12 — Security Hardening

### 12.1 Firewall
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
sudo ufw status
```

### 12.2 Automatic security updates
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```
Select Yes when prompted.

### 12.3 SSH hardening (disable password auth, root login)
Edit `/etc/ssh/sshd_config`:
```bash
sudo nano /etc/ssh/sshd_config
```
Set:
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```
```bash
sudo systemctl restart ssh
```

### 12.4 Screen lock
```bash
sudo apt install gnome-screensaver -y
```
Settings > Privacy > Screen Lock: lock after 5 minutes, require password immediately.

### 12.5 fail2ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable --now fail2ban
```

### 12.6 Verify AppArmor is active
```bash
sudo aa-status
```
Should show profiles loaded and enforced. AppArmor is on by default in Ubuntu 24.04.

### 12.7 Verify disk encryption
```bash
lsblk -f | grep crypto
```
Should show `crypto_LUKS` on the main drive if encryption was enabled during install.

---

## Future: Radio Tools (TODO)

These will be added when radio integration is in scope:

- [ ] **CHIRP** — programming cable radio programming (`sudo apt install chirp`)
- [ ] **GNU Radio** — SDR signal processing suite
- [ ] **GQRX** — SDR receiver GUI (RTL-SDR / HackRF)
- [ ] **Direwolf** — software AX.25 TNC for APRS
- [ ] **JS8Call** — keyboard-to-keyboard HF messaging
- [ ] **WSJT-X** — weak signal digital modes (FT8/FT4)
- [ ] **fldigi** — digital mode suite (PSK31, RTTY, etc.)
- [ ] **PySDR** — Python SDR toolkit
- [ ] **Meshtastic CLI** — `pip install meshtastic` — USB serial to Heltec nodes
- [ ] **RNode driver** — Reticulum interface tools for LEFT LoRa node

> Note: Confirm USB serial permissions before event.
> `sudo usermod -aG dialout ps` — required for USB serial access to LoRa nodes.

---


