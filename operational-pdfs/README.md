# M2 Community Node — Operational PDFs

> **These are templates, not your documents.**
>
> The PDFs in this directory were generated from the reference build (192.168.8.x IPs, placeholder domains). They are included so you can see what the finished output looks like. **Before you deploy, regenerate them with your own instance values** — your IPs, domain, WiFi credentials, and event name. See below.

---

## Documents

| File | Format | Purpose |
|---|---|---|
| `M2_Community_Node_Runbook.pdf` | US Letter, ~20 pages | Field operations runbook — POST checklist, service procedures, remote access, quick reference credential table |
| `M2_ATAK_FieldCard.pdf` | 3.5×5.5 in (x2), landscape US Letter | Laminated ATAK setup card — manual and QR enrollment steps, front/back |
| `M2_Community_Node_Build_Book.pdf` | US Letter, multi-page | Full build reference — condensed from BUILD_GUIDE.md for offline use |
| `M2_Community_Node_Troubleshooting.pdf` | US Letter | Troubleshooting reference — common failure modes and recovery steps |
| `M2_Rack_Wiring_Diagram.pdf` | US Letter, landscape | 1U/2U rack wiring diagram — power, data, and RF cabling |

---

## Regenerating for Your Build

All PDFs are generated from Python scripts in `scripts/`. Requirements: `reportlab`.

```
pip install reportlab
```

**Step 1 — Set your instance values.**

Copy `instance.conf.template` to `instance.conf` and fill in your values:

```
cp instance.conf.template instance.conf
nano instance.conf
```

Key fields that affect the PDFs:
- `NODE1_IP`, `NODE2_IP` — your Pi IPs
- `BASE_DOMAIN`, `ELEMENT_DOMAIN`, `HEADSCALE_DOMAIN` — your domains
- `EVENT_NAME`, `EVENT_DATE`, `EVENT_LOCATION` — printed on field card and runbook cover

Credentials (WiFi passwords, enrollment usernames/passwords) are read from `instance.conf` or environment variables — see each script header for the full variable list.

**Step 2 — Run the generators.**

```
cd scripts
python generate_runbook.py
python generate_field_card.py
python generate_build_book.py
python generate_reference_pdfs.py
python generate_m2_wiring_diagram.py
```

Output lands in `operational-pdfs/`.

---

## Printing Notes

- `M2_ATAK_FieldCard.pdf` — print landscape on US Letter, cut down the center, laminate each half. Fits standard 4×6 pouches.
- `M2_Community_Node_Runbook.pdf` — print US Letter, duplex or single-sided. Spiral bind or saddle-stitch for field use.
- `M2_Community_Node_Build_Book.pdf` — print US Letter, single-sided. Three-hole punch, binder.
- All others — US Letter, single-sided.

---

*CC BY-NC-SA 4.0*
