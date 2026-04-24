# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.1] — 2026-04-24

### Added
- `docs/BUILD_OPTIONS.md` — hardware alternatives guide covering Pi 4, Pi 5 8GB, x86_64 mini PCs,
  single-device builds, no-Monero variants, and service dependency map
- Cross-references to BUILD_OPTIONS.md in README, HARDWARE_BOM.md, PREREQUISITES.md, docs/README.md

---

## [1.0.0] — 2026-04-24

First public release. Full release notes: [RELEASE_NOTES.md](RELEASE_NOTES.md)

### Added
- Dual Raspberry Pi 5 build guide (13 phases, every command and config)
- Hardware BOM with part numbers and pricing (~$994 recommended, ~$889 budget)
- Service stack: Matrix/Conduit, Element Web, OpenTAKServer, Headscale, Mumble,
  Meshtastic bridge, Reticulum, Monero full node, Tor, I2P, AdGuard DNS
- Kiosk display — offline maps (PMTiles + DTED2), service health dashboard
- 17 reference docs: build guide, event runbook, ATAK connectivity, disaster recovery,
  troubleshooting, maintenance, network customization, and more
- Print-ready PDFs: build book, runbook, wiring diagram, ATAK field card, outreach materials
- ReportLab PDF generators with bundled OFL fonts
- Matrix status bot (12h digest), ATAK data package builder, QR code generators
- instance.conf template — single file controls all instance-specific values
- Network diagram (docs/M2_Network_Diagram.drawio)
- CC BY-NC-SA 4.0 license
