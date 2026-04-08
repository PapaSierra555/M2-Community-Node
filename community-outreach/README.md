# M2 Community Node — Outreach Materials

Print-ready materials for introducing the M2 Community Node at events, chapter meetings, and mutual aid gatherings. All materials are CC BY-NC-SA 4.0.

---

## Documents

| File | Format | Purpose |
|---|---|---|
| `M2_Snapshot.pdf` | US Letter, 2 pages | Node overview — services, capabilities, hardware specs, deployment scenarios |
| `M2_PACE_Card.pdf` | US Letter, 1 page | PACE framework reference — which M2 service maps to each comms tier |
| `M2_Build_Summary.pdf` | US Letter, 1 page | Build cost tiers, BOM summary, skills required |
| `M2_New_Member_Card.pdf` | 3.5×5.5 in, 2 sides | Laminated onboarding card — WiFi credentials, connection methods, quick reference |

---

## Regenerating PDFs

All PDFs are generated from Python scripts in `scripts/`. Requirements: `reportlab`, `qrcode`.

```
pip install reportlab qrcode[pil]
```

Run all:
```
cd community-outreach/scripts
python generate_m2_snapshot.py
python generate_pace_card.py
python generate_build_summary.py
python generate_new_member_card.py
```

Output lands in `community-outreach/pdf/`.

---

## Assets

Photos and logos used by the generation scripts are in `assets/`:

| File | Use |
|---|---|
| `node-photo.jpg` | Hero shot — used in README and outreach materials |
| `node-ccc.jpg`, `node-detail-1.jpg`, `node-detail-2.jpg`, `node-side.jpg`, `node-top.jpg` | Detail photos for snapshot and summary |
| `lfhi-logo.png` | LFHI partner badge |

---

## Target Audience

**Primary:** Community preparedness groups, SAR teams, neighborhood mutual aid, and emergency response organizations evaluating off-grid comms on the PACE framework.

**Secondary:** Builders evaluating whether the M2 platform fits their technical capability and budget.

---

## Printing Notes

- `M2_New_Member_Card.pdf` — print duplex on card stock (3.5×5.5 in), laminate. Fits standard business card holders. Hand out at events.
- All other docs — US Letter, single-sided. Print in color for maximum impact.
- For vinyl panel labels and QR cutouts, see `svg/` directory and `docs/QR_CODES.md`.

---

*CC BY-NC-SA 4.0*
