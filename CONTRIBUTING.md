# Contributing to M2 Community Node

This is a documentation-first project. There is no application code to maintain — the deliverables are build guides, BOMs, ops docs, config templates, and support tooling (PDF generators, QR scripts, status bots).

Contributions are welcome. The bar is correctness and clarity.

---

## What Needs Help

- **Build corrections** — if a step is wrong, outdated, or unclear, open an issue or PR against the relevant file in `docs/`
- **Hardware updates** — parts go out of stock; ASIN substitutions and pricing corrections in `docs/HARDWARE_BOM.md` are always useful
- **Troubleshooting additions** — if you hit a problem not covered in `docs/TROUBLESHOOTING.md`, add it
- **New service integrations** — additional services that fit the field-portable, community-first model
- **Script improvements** — the PDF generators and ops scripts in `scripts/` are fair game
- **Typos and formatting** — yes, even these

---

## Project Conventions

- **Commands assume Windows 11 + PowerShell** as the operator workstation, SSH'ing into Pi nodes. Note deviations explicitly if you're on Linux or macOS.
- **Docker images must be pinned** to specific tags — never `:latest`
- **OpenTAK Server runs native systemd**, not Docker
- **Credential placeholders** use `CHANGE_ME` or `YOUR_VALUE_HERE` — never real values
- **Secrets are gitignored** — only `*.template.*` files are tracked; never commit filled credentials

---

## How to Contribute

1. Fork the repo
2. Create a branch: `git checkout -b fix/your-description`
3. Make your changes
4. Open a pull request with a clear description of what changed and why

For anything substantial (new sections, restructuring, new services), open an issue first to discuss scope.

---

## Commit Style

Small, focused commits. Message should say *why*, not just *what*:

```
fix: step 7 conduit config — token format changed in v0.7
docs: add Meshtastic 2.6 channel rename procedure to troubleshooting
feat: add cf-access.sh helper for Cloudflare Path B automation
```

---

## Regenerating PDFs

The printable PDFs in `operational-pdfs/` are generated from source docs in `docs/`. The community marketing PDFs in `community-outreach/pdf/` are generated from `community-outreach/scripts/`. If you change a source doc, regenerate the corresponding PDF and include it in your PR.

```bash
# From the repo root
python scripts/generate_build_book.py
python scripts/generate_runbook.py
python scripts/generate_reference_pdfs.py
python scripts/generate_m2_wiring_diagram.py
python scripts/generate_field_card.py
```

PDF generation requires `reportlab` and the font set referenced in each script.

---

## License

All contributions are made under [CC BY-NC-SA 4.0](LICENSE). By submitting a pull request, you agree that your contribution is licensed under the same terms.
