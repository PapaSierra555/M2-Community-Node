# M2 -- ATAK Integration Guide

> **Context:** Community Node (M2) field kit -- ATAK-CIV configuration for
> community emergency response, CERT, SAR, and disaster operations.

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [What ATAK Does Out of the Box](#2-what-atak-does-out-of-the-box)
3. [Recommended Plugins](#3-recommended-plugins)
4. [Data Packages Pre-Loaded on OTS](#4-data-packages-pre-loaded-on-ots)
5. [Volunteer Onboarding Flow](#5-volunteer-onboarding-flow)
6. [Specialist Tools (Self-Install)](#6-specialist-tools-self-install)
7. [Plugins Evaluated and Cut](#7-plugins-evaluated-and-cut)
8. [Community Resources](#8-community-resources)
9. [Sources](#9-sources)

---

## 1. Design Philosophy

A volunteer who just downloaded ATAK should be operational in under 5 minutes. Every plugin that auto-installs is another thing that can break, another prompt to dismiss, another icon to explain. The M2 node prioritizes **reliability and simplicity** over feature count.

Three rules:

1. **If ATAK already does it, don't add a plugin.** ATAK core handles position sharing, chat, markers, drawing, route planning, CASEVAC reports, checklists, track logging, and offline maps. No plugins needed for any of that.
2. **If it requires internet, cut it.** The M2 operates offline or on local WiFi. Plugins that phone home are dead weight.
3. **If it requires hardware the volunteer doesn't have, don't auto-install it.** A Meshtastic plugin is useless without a Meshtastic radio. A drone plugin is useless without a drone.

**Server-side rule:** No new containers on the Pi. The stack is full: OTS, Murmur, Monero, Conduit, Cloudflared, Headscale, Tor, I2P, Mosquitto. Every additional service degrades reliability for the services that matter.

### Correction: OTS Plugin Auto-Push

OTS **cannot** auto-install APK plugins on devices. Android requires user interaction to install APKs. What OTS CAN auto-push are **data packages** -- certificates, server configs, map tiles, KML overlays. Plugins must be installed from the Play Store or sideloaded manually.

The onboarding QR code links to a page with Play Store links for required apps. See [Section 5](#5-volunteer-onboarding-flow).

---

## 2. What ATAK Does Out of the Box

These features are included in ATAK-CIV 5.6.0 with **no plugins and no server**. They work over multicast UDP on any shared WiFi network, or over OTS when a server is available.

### Position Sharing (PLI)

Every ATAK device broadcasts its position automatically. All teammates appear as colored dots on the map. No configuration beyond connecting to the same network or server. Default reporting interval works for most use cases.

### GeoChat

Text messaging within ATAK -- one-to-one, team channels, or broadcast. Messages are CoT objects that work over any transport: server, multicast, or Meshtastic mesh.

### Drawing & Markup

Create shapes (circles, rectangles, polygons, lines, freehand) on the map. Set color, fill, labels. Use for search sectors, hazard zones, evacuation routes, staging areas. All drawings sync to connected devices via server.

### CASEVAC / 9-Line MEDEVAC

Built-in 9-line MEDEVAC report following JFIRE 2016 Appendix G. Includes ZMIST report and HLZ (Helicopter Landing Zone) brief. Creates map markers at casualty location shared to all connected EUDs.

### Route Planning

Multi-waypoint routes with distance/bearing calculations. View route details including total distance and estimated travel time. Not turn-by-turn, but sufficient for point-to-point field navigation.

### Elevation Profile & Line of Sight

Select any route or line to see elevation profile (requires DTED loaded -- already on M2). Enable viewshed analysis for radio relay placement and visual search planning. This is why we built the DTED2 data package.

### ExCheck (Collaborative Checklists)

Checklists hosted on OTS. Create templates for ICS forms, search phase tracking, equipment checks, comms plan verification. All team members see real-time task status. Templates are XML distributed via data packages.

### Track Logging / Breadcrumbs

Continuous GPS track recording. See your path and teammates' paths. Export as KML/GPX. Critical for SAR to verify complete area coverage with no gaps in the search grid.

### Geofencing & Alerts

Attach triggers to any drawn shape. Configure alerts when team members enter or exit a zone. Use for danger zones, search boundaries, or rally point monitoring.

### Coordinate Entry & Conversion

MGRS, UTM, lat/lon (DD, DMS, DDM). Convert between formats. Share precise locations. Set display format per user preference.

### Offline Maps

Import MBTiles, SQLite, GeoPackage, KML/KMZ, GeoTIFF/GeoPDF. The M2 serves PMTiles on port 8080 -- street-level offline maps for FL/SC/NC/VA are already loaded.

### Built-in Plugins (Available from CivTAK, Not Play Store)

| Plugin | Purpose |
|---|---|
| TAK ICU | Peer-to-peer video streaming (no server needed) |
| TAK GeoCam | Geotagged tactical camera |
| Image Markup | Annotate geotagged photos |
| Night Vision | Night-optimized display mode |

Download from [CivTAK](https://www.civtak.org/2020/10/11/built-in-plugins-that-arent-in-the-play-store/). These are optional -- install on team lead devices if needed.

### Icon Sets (Pre-Loaded)

ATAK ships with: FEMA markers, Incident Management symbols, Public Safety Air icons, Responder icons, GeoOps icons, MIL-STD-2525C military symbology. No additional icon packs needed for emergency response.

---

## 3. Recommended Plugins

Two plugins. That's it.

### 3.1 Meshtastic ATAK Plugin

**What:** Bridges ATAK to Meshtastic LoRa mesh radios for off-grid position sharing and text chat. No cellular, no WiFi, no internet required.

| Field | Detail |
|---|---|
| Install | [GitHub Releases](https://github.com/meshtastic/ATAK-Plugin/releases) (match version to ATAK) |
| Version | Match to ATAK version (e.g., 2.5.x for ATAK 5.6) |
| Works offline | Yes -- this IS the offline solution |
| Server required | No |
| Extra hardware | **Yes -- Meshtastic LoRa radio ($35-60)** |

**Who needs it:** Only operators who have their own Meshtastic radio paired to their phone.

> **Most volunteers do NOT need this plugin.** The M2 already has a Heltec V3 radio connected to OTS via the built-in [TAK Meshtastic Gateway](https://docs.opentakserver.io/tak_meshtastic_gateway.html). This server-side gateway bridges mesh traffic to ALL connected ATAK clients automatically -- no per-device plugin needed. The plugin is only for operators who want direct radio-to-phone pairing with their own Meshtastic device.

**Key config (for users with their own radio):**
- Set Meshtastic device role to `TAK` (compressed PLI via ATAK plugin)
- Set to `TAK_TRACKER` for devices without ATAK (standalone GPS beacons)
- Green icon in ATAK = connected; red = binding failed (restart Meshtastic app)

**Install method:** Sideload APK. Not on Play Store. Provide APK file via OTS data package download or USB.

---

### 3.2 VNS (Vehicle Navigation System)

**What:** Turn-by-turn vehicle navigation inside ATAK. Emergency quick-nav feature: one tap to route to a pre-set rally point or casualty collection point. Offline routing available.

| Field | Detail |
|---|---|
| Install | [Google Play Store](https://play.google.com/store/apps/details?id=com.atakmap.android.vns.plugin) |
| Version | 5.6.0 (matches ATAK 5.6) |
| Works offline | Yes (with pre-loaded routing data) |
| Server required | No |
| Extra hardware | No |

**Who needs it:** Team leads running vehicle-based operations (road SAR, logistics, convoy). Not useful for foot-based wilderness SAR.

> The emergency quick-nav to rally point is the only feature that isn't already covered by Google Maps or OsmAnd. For teams that pre-define rally points and casualty collection points, the one-tap routing is genuinely useful.

**Install method:** Play Store. Opt-in only -- team leads install it themselves.

---

## 4. Data Packages Pre-Loaded on OTS

These are what OTS actually pushes to devices. This is the M2's real distribution mechanism.

### Already Deployed

| Package | Contents | Size | Auto-push |
|---|---|---|---|
| DTED2 Florida | 30m elevation data for LOS analysis, slope, viewshed | ~3.25 GB | Via QR scan (DTED.org) |
| PMTiles SE US | Street-level offline maps FL/SC/NC/VA at z14 | ~2-4 GB | Served on port 8080 |
| Community Node marker | CoT event showing M2 HQ position | ~1 KB | Auto (cron push) |

### To Build

| Package | Contents | Purpose | Auto-push |
|---|---|---|---|
| Connection data package | Server URL + certs + preferences | One-file ATAK onboarding | Yes |
| Rally point markers | Pre-set KML with local hospitals, fire stations, shelters | Common operating picture baseline | Yes |
| ATAK-Maps profiles | MOBAC XML sources for USGS topo, satellite, OpenTopo | Additional map layer options | Yes |
| ExCheck SAR template | Grid search phase checklist (custom, no public templates exist) | SAR task tracking | Available on request |

> **Offline map warning:** Selecting a map source in ATAK does NOT make it available offline. Tiles must be pre-cached using ATAK's built-in downloader (max 300,000 tiles per session) or pre-loaded as MBTiles/PMTiles files. The M2's PMTiles are already cached -- no internet required.

---

## 5. Volunteer Onboarding Flow

### Local WiFi (On-Site)

1. Volunteer connects to **CommunityNode** WiFi (password on community page or QR poster)
2. Opens browser, goes to `http://192.168.8.10:8081` (community page)
3. Taps **ATAK-CIV** Play Store link -- installs the app
4. Opens ATAK, sets callsign (name or handle), accepts location permissions
5. Adds server: `192.168.8.20`, port `8088`, TCP, **uncheck SSL/TLS**
6. Map loads with offline tiles, teammate positions appear, Community Node marker visible
7. Volunteer is operational

**Total time: 3-5 minutes.** One app, one server connection. Clean UI.

### Remote (Out of Area)

See BUILD_GUIDE Section 9.1.1 -- Remote Operator Onboarding. Two tiers:

- **Browser only:** `https://tak.yourdomain.com` -- live web map, no install
- **Full ATAK:** Install Tailscale, join Headscale VPN, connect ATAK to `192.168.8.20:8088`

### What NOT to Do

- Do NOT push multiple plugins at once. A first-time user staring at overlays from three different plugins will close the app.
- Do NOT require SSL on first connection. TCP works on trusted LAN. SSL adds cert troubleshooting to onboarding.
- Do NOT assume volunteers have Meshtastic radios. The server-side gateway handles mesh bridging for everyone.

---

## 6. Specialist Tools (Self-Install)

These are documented for teams that bring specialized hardware. They are NOT pre-loaded on OTS, NOT pushed to devices, and NOT part of the standard M2 loadout. Specialists install them themselves.

| Tool | Who | Hardware Required | Install From |
|---|---|---|---|
| OpenAthena | Drone operators | DJI/Autel/Parrot/Skydio drone | [GitHub](https://github.com/Theta-Limited/OpenAthenaAndroid) |
| UAS Tool | Drone operators (DJI) | DJI drone | [CivTAK](https://www.civtak.org/) |
| TAKWatch | Garmin watch owners | Garmin Instinct/Fenix | [GitHub](https://github.com/TDF-PL/TAKWatch) + [Garmin IQ](https://apps.garmin.com/apps/9f3aa645-f24f-49f2-af0f-328b98a7be70) |
| APRSTAK | Licensed ham operators | Ham radio with TNC + APRSDroid | [GitHub](https://github.com/niccellular/aprstak) |

---

## 7. Plugins Evaluated and Cut

These were reviewed during the March 2026 audit and removed from the M2 loadout. Rationale preserved so future builders can make informed decisions for their own deployments.

| Plugin | Verdict | Rationale |
|---|---|---|
| **WASP** (Wide Area Search) | Cut | Wickr was shut down by AWS in early 2024. Plugin hasn't been updated since. Won't install on current-generation devices (Samsung S25, Pixel 9). The Play Store listing (`com.atakmap.android.wickr.plugin`) shows Wickr branding but the backend service no longer exists. Dead software. |
| **HAMMER** (acoustic modem) | Cut | Crashes with Baofeng radios (most common civilian radio). Requires audio cables + per-device tuning. Being deprecated. Meshtastic replaces this use case entirely. [Field test report](https://guntoter.org/2022/03/08/atak-hammer-and-baofengs-the-bad-news/). |
| **FreeTAK Mumla Plugin** | Cut | Mumla standalone app works fine for PTT voice without this plugin. Plugin has unclear maintenance status and may break on ATAK 5.6. A broken PTT overlay is worse than no overlay. Use Mumla directly -- it's a simple app. |
| **OpenTAK ICU** | Cut | Requires adding MediaMTX container to an already-full Pi. Video streaming saturates the WiFi that ATAK needs for position updates. Built-in TAK ICU does peer-to-peer video without a server if genuinely needed. |
| **Wx Report** | Cut | Requires internet for NOAA data. Useless offline. If you have internet, use your phone's weather app. The open-source alternative (ATAK-Weather-Plugin) also requires internet. Check the weather before you deploy. |
| **TAK-CAD** | Cut | Alpha software built for official TAK Server, not OTS. Compatibility unverified. A 5-15 person CERT team needs a whiteboard and a radio, not computer-aided dispatch. ExCheck handles basic task tracking. |
| **LandSAR** | Cut | Requires a Java server on a Pi already running 5+ services. Professional SAR teams that need probability modeling bring their own tools. Community CERT teams doing grid searches use WASP and paper maps. |
| **ADSBCOT** | Cut | Requires RTL-SDR dongle + dump1090 + adsbcot Python package on the Pi. Additional hardware and server components for aircraft tracking that is irrelevant to CERT ground operations. |
| **WiFi2COT** | Cut | One-developer GitHub project with unclear maintenance. The "detect survivor phones via WiFi" concept is theoretical -- if you're close enough to detect WiFi RSSI, you're close enough to shout. Not reliable enough for emergency use. |
| **CloudRF / SOOTHSAYER** | Cut | Requires another Docker container (or paid cloud service) for a pre-planning tool. ATAK's built-in viewshed/line-of-sight analysis covers basic radio coverage questions. Run SOOTHSAYER on a laptop during pre-mission planning if needed. |

---

## 8. Community Resources

### Reference Hubs

| Resource | URL | Contents |
|---|---|---|
| fieldmapper's TAK Gist | [GitHub Gist](https://gist.github.com/fieldmapper/2756ae29bff337ec7bda5d25f310c772) | Comprehensive link collection -- hardware, software, data packages, tutorials |
| CivTAK Files | [civtak.org/files](https://www.civtak.org/files/) | Official community data packages and resources |
| CivTAK Plugins | [civtak.org/category/plugins](https://www.civtak.org/category/plugins/) | Plugin announcements and documentation |
| ATAK-Maps | [GitHub](https://github.com/joshuafuller/ATAK-Maps) | MOBAC XML map source definitions (USGS topo, satellite, OpenTopo) |
| 9M2PJU Plugin List | [GitHub](https://github.com/9M2PJU/ATAK-Civ-Plugins) | Compiled list of CIV plugins with links |

### Training Resources

| Resource | URL | Focus |
|---|---|---|
| Colorado Fire Tech | [cofiretech.gov/introduction-to-tak](https://cofiretech.gov/introduction-to-tak) | Fire/EMS TAK introduction |
| Chaos Koalas | [chaoskoalas.com/atak](https://chaoskoalas.com/atak/) | Getting started with ATAK |
| Constellation Response | [Quick Start Pt1](https://constellationresponse.com/blogs/news/atak-quick-start-guide-pt1) / [Pt2](https://constellationresponse.com/blogs/news/atak-quick-start-guide-pt2-comms-and-offline-maps) | ATAK quick start + offline maps |
| ToughStump | [First Time Setup](https://toughstump.com/2023/12/05/first-time-user-set-up-in-atak/) | First-time user walkthrough |
| BuffaLoRa | [Meshtastic + ATAK SAR Drill](https://buffalora.org/2025/09/14/meshtastic-as-a-plugin-to-atak/) | Real-world SAR drill using Meshtastic + ATAK |

### Data Package Formats

| Format | Use Case |
|---|---|
| .zip (data package) | Bundle of certs, configs, KML, map tiles -- one-file onboarding |
| .kml / .kmz | Map overlays -- search grids, hazard zones, boundaries |
| .mbtiles | Offline map tiles |
| .dpk | Signed data package for TAK Server distribution |

---

## 9. Sources

- [CivTAK / ATAK Community](https://www.civtak.org/)
- [Meshtastic ATAK Plugin Docs](https://meshtastic.org/docs/software/integrations/integrations-atak-plugin/)
- [Meshtastic ATAK Plugin GitHub](https://github.com/meshtastic/ATAK-Plugin)
- [OpenTAKServer Docs](https://docs.opentakserver.io/)
- [TAK Meshtastic Gateway (OTS Docs)](https://docs.opentakserver.io/tak_meshtastic_gateway.html)
- [VNS on Google Play](https://play.google.com/store/apps/details?id=com.atakmap.android.vns.plugin)
- [CivTAK Built-in Plugins](https://www.civtak.org/2020/10/11/built-in-plugins-that-arent-in-the-play-store/)
- [ATAK-Maps GitHub](https://github.com/joshuafuller/ATAK-Maps)
- [Colorado Fire Tech - Introduction to TAK](https://cofiretech.gov/introduction-to-tak)
- [HAMMER Field Test (Gun Toter)](https://guntoter.org/2022/03/08/atak-hammer-and-baofengs-the-bad-news/)
- [BuffaLoRa - Meshtastic + ATAK SAR Drill](https://buffalora.org/2025/09/14/meshtastic-as-a-plugin-to-atak/)
- [Constellation Response - ATAK Quick Start](https://constellationresponse.com/blogs/news/atak-quick-start-guide-pt1)
- [Chaos Koalas - Getting Started with ATAK](https://chaoskoalas.com/atak/)
- [ToughStump - First Time Setup](https://toughstump.com/2023/12/05/first-time-user-set-up-in-atak/)
- [OpenTAKServer Plugin Update Server](https://docs.opentakserver.io/update_server.html)
- [fieldmapper TAK Resources Gist](https://gist.github.com/fieldmapper/2756ae29bff337ec7bda5d25f310c772)
