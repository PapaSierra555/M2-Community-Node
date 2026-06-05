# M2 Community Node — Field Maintenance & Repair Kit

What to bring for field deployment. Covers the full node stack: rack,
Meshtastic fleet, field laptop, and repair/recovery gear.

---

## Node Rack — Deploy Checklist

- [ ] Comms Pi (192.168.8.10) — verify label
- [ ] Tactical Pi (192.168.8.20) — verify label
- [ ] Router
- [ ] NVMe drive — seated in tactical Pi, verify before pack
- [ ] Kiosk display + mount hardware
- [ ] Micro-HDMI to HDMI cable (comms Pi 5 → display) — braided, not flat
- [ ] Rack enclosure / case / carry bag

---

## Power

- [ ] Pi power supply x2 (labeled, one per Pi)
- [ ] Router power supply
- [ ] Display power supply / adapter
- [ ] Power strip (4+ outlets)
- [ ] Extension cord
- [ ] **SPARE: Pi power supply x1** — most common single-point failure

---

## Network

- [ ] Router WAN uplink — hotspot or ethernet
- [ ] Ethernet patch cables x4 (Pi #1, Pi #2, laptop, spare)
- [ ] **SPARE: Ethernet cable x2**

---

## Meshtastic Fleet

- [ ] T114 x8 — MESH 01–08 (verify labels)
- [ ] T3S3 x3 — PS-01, PS-02, PS-03
- [ ] USB-C charging cables x4
- [ ] USB serial cable — T114 (for re-flash / reconfigure)
- [ ] USB serial cable — T3S3 (for re-flash / reconfigure)
- [ ] Power bank x1

---

## Field Laptop

- [ ] Getac S400 G2 + power supply
- [ ] SSH access to both Pis confirmed before departure

---

## Print Materials

- [ ] Element join cards (cut + laminated)
- [ ] Meshtastic channel QR cards (cut + laminated)
- [ ] Meshtastic device cards front + back (cut + laminated, duplex)
- [ ] **SPARE: 2 extra sets of each** — cards walk, get wet, get lost

---

## Tools

- [ ] Small Phillips screwdriver
- [ ] Small flathead screwdriver
- [ ] Needle-nose pliers
- [ ] Multimeter (power supply and cable fault diagnosis)
- [ ] USB hub (run serial + keyboard simultaneously on one Pi port)
- [ ] Zip ties x20
- [ ] Velcro straps x6
- [ ] Electrical tape
- [ ] Masking tape + marker (relabeling, field notes)

---

## Spare Parts / Recovery

| Part | Failure it covers |
|---|---|
| Spare Pi x1 (either model) | Dead Pi — reimage and reconfigure as either stack |
| Spare microSD x2 (Pi OS imaged, 32GB+) | Corrupted OS — swap and restore |
| USB microSD reader | Writing replacement SD on the field laptop |
| Spare USB-C cable x2 | Charging failure for Meshtastic devices |
| Spare ethernet cable x2 | Cable fault, wrong length |
| Spare Pi power supply x1 | Pi won't boot — PSU is first suspect |

---

## Recovery Procedures (quick reference)

**Pi won't boot → swap SD card:**
1. Pull SD, insert spare (pre-imaged)
2. Boot into new OS, restore from backup or re-run setup
3. Repo + configs on field laptop: `~/SOURCE CONTROL/M2-Community-Node`

**Pi fully dead → hot-swap spare:**
1. Label spare with correct Pi number before inserting
2. Connect to LAN, SSH in, restore from repo
3. Comms stack: `sudo docker compose -f /opt/community-node/docker-compose.yml --profile clearnet up -d`
4. Tactical stack: `sudo docker compose -f /opt/tactical-node/docker-compose.yml up -d`
5. Headscale + OTS: `sudo systemctl start headscale opentakserver`

**Meshtastic device won't connect → reconfigure via serial:**
```
python3 meshtastic/scripts/config_ccc_t114.py   # T114 devices
python3 meshtastic/scripts/config_ccc_t3s3.py   # T3S3 devices
```
Run from project root on field laptop. Plug device via USB serial first.

**Dashboard shows red after boot → wait 2 minutes then check:**
```
ssh ps@192.168.8.10 "sudo docker ps --format 'table {{.Names}}\t{{.Status}}'"
ssh ps@192.168.8.20 "sudo systemctl is-active headscale && sudo systemctl is-active opentakserver"
```
Full boot verification: `docs/POWER_CYCLE.md`

**Mosquitto crash-looping:**
```
ssh ps@192.168.8.20 "sudo docker restart tactical-node-mosquitto-1"
```
If it keeps looping: check `/opt/tactical-node/config/mosquitto/mosquitto.conf` — must have `allow_anonymous true`, no `password_file` line.

---

*Full power cycle procedure: `docs/POWER_CYCLE.md`*
*Credentials: M2_SECRETS.md on field laptop (pull from Obsidian z_Backups/ before departure)*
