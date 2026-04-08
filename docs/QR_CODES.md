# QR Codes

This project uses two separate QR code workflows — one for printed documents, one for vinyl cutting. They are intentionally separate because the requirements are different.

---

## Physical Cutouts — 4 Essential SVGs

These are the only QR codes that need to be physically cut from vinyl and affixed to the kiosk panel. Everything else is reachable from the community page once someone is connected.

| Label | Encodes | Why it's on the panel |
|-------|---------|----------------------|
| **WIFI** | `WIFI:T:WPA;S:CommunityNode;P:...` | First step — connects phone to the node |
| **COMMUNITY** | `https://yourdomain.com` | Entry point — all other services are linked from here |
| **ELEMENT WEB** | `https://communitynode.yourdomain.com` | Encrypted chat via clearnet (no WiFi required) |
| **ATAK CONNECT** | `https://atakenroll.yourdomain.com:8447` | ATAK certificate enrollment |

The `svg/WebQrCodes/` directory contains example SVGs for reference. **You must generate your own** — your URLs (clearnet domain, .onion addresses) will be different. Use mini-qr as described below.

---

## For Printed Documents (PDFs, field cards)

Generated automatically by script. Run this any time URLs or IPs change:

```bash
python scripts/generate_qr.py
```

Output goes to `svg/` as individual SVGs embedded in the PDF generators. You do not need to touch these manually.

---

## For Vinyl Cutting (Cricut)

**Use [mini-qr](https://github.com/lyqht/mini-qr) — not the script.**

The script-generated QR SVGs use standard square modules that are too small and too numerous to weed cleanly from vinyl. mini-qr produces organic, rounded QR codes that are far easier to weed and look better on the rack labels.

### Where to Run It

mini-qr is a web app. Run it locally (no install needed):

```bash
git clone https://github.com/lyqht/mini-qr
cd mini-qr
npm install
npm run dev
```

Or use the hosted version at the Vercel deployment linked from the repo.

### Your URL List

Create a simple reference list of your node's URLs before generating QR codes:

| QR Label | URL to encode |
|----------|---------------|
| WIFI | `WIFI:T:WPA;S:CommunityNode;P:YOUR_WIFI_PASSWORD;;` |
| COMMUNITY | `https://yourdomain.com` |
| ELEMENT WEB | `https://communitynode.yourdomain.com` |
| ATAK CONNECT | `https://atakenroll.yourdomain.com:8447` |
| TOR ELEMENT | your `.onion` address (from `SERVICE_MAP.md`) |

The `qr-code-config.json` in `svg/WebQrCodes/` contains the style settings used for the reference set — import it into mini-qr to reproduce the same look.

### Workflow

1. Open mini-qr
2. Import `qr-code-config.json` to restore style settings (dot type, colors, size)
3. For each URL in your list, paste the value into mini-qr and export as SVG
4. Save exported SVGs to `svg/WebQrCodes/`

### When URLs Change

If .onion addresses or IPs change (e.g. after Tor key loss — see DISASTER_RECOVERY.md):

1. Get the new .onion addresses from Pi #1 (see `SERVICE_MAP.md` for commands)
2. Regenerate the affected QR codes in mini-qr
3. Replace the old SVGs in `svg/WebQrCodes/`
4. Reprint or recut any physical labels that used the old addresses

### Vinyl Cutting Notes

- **Single layer** on dark surface: cut white vinyl in the QR module pattern, apply directly to rack. No alignment needed.
- **Two layer** on light surface: white base square first, then black modules aligned to edges.
- Weed the negative space (what you remove), keep the modules (what you keep).
- Clean surface with IPA before applying. Let dry 30 seconds.

---

## Full QR Code Inventory

All 11 QR codes in the project. The 4 marked **[PANEL]** are the physical cutouts.

| Label | Encodes | Notes |
|-------|---------|-------|
| **WIFI** ⬅ PANEL | WiFi string | Auto-connect to guest network |
| **COMMUNITY** ⬅ PANEL | `https://yourdomain.com` | Community info page |
| **ELEMENT WEB** ⬅ PANEL | `https://communitynode.yourdomain.com` | Element via clearnet |
| **ATAK CONNECT** ⬅ PANEL | Enrollment URL | ATAK certificate enrollment |
| ELEMENT LAN | `http://192.168.8.10:8080` | Element on local WiFi — kiosk modal only |
| TOR ELEMENT | `.onion` URL | Element via Tor browser — kiosk modal only |
| TOR COMMUNITY | `.onion` URL | Community page via Tor — kiosk modal only |
| ATAK ANDROID | Google Play URL | Download ATAK CIV — kiosk modal only |
| ITAK IOS | App Store URL | Download iTAK — kiosk modal only |
| MESHTASTIC | GitHub releases URL | Meshtastic ATAK plugin — kiosk modal only |
| MUMLA | Google Play URL | Download Mumla (Mumble) — kiosk modal only |

Your actual URLs go in your own URL list (see Workflow above). The `svg/WebQrCodes/` SVGs are examples only.
