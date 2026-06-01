"""
Flatten and print-ready all M2 PDFs.
- garbage=4: max object deduplication and removal
- deflate=True: compress all streams
- clean=True: sanitize content streams (removes redundant operators)
- Fonts are already embedded by ReportLab TTFont; this verifies and preserves that.
"""
import os
import glob
import fitz  # PyMuPDF

PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../pdf")

def flatten(path):
    tmp = path + ".flat"
    doc = fitz.open(path)
    # Verify font embedding before save
    fonts_ok = True
    for page in doc:
        for f in page.get_fonts(full=True):
            if f[3] == "" and f[4] not in ("Type3",):
                print(f"  WARN unembedded font on {os.path.basename(path)}: {f[3]}")
                fonts_ok = False
    doc.save(
        tmp,
        garbage=4,
        deflate=True,
        clean=True,
        linear=False,
        no_new_id=False,
    )
    doc.close()
    before = os.path.getsize(path)
    os.replace(tmp, path)
    after = os.path.getsize(path)
    status = "OK " if fonts_ok else "WARN"
    print(f"  {status}  {os.path.basename(path):40s}  {before//1024:>5} KB  ->  {after//1024:>5} KB")

if __name__ == "__main__":
    pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    print(f"Flattening {len(pdfs)} PDFs in {os.path.abspath(PDF_DIR)}\n")
    for p in pdfs:
        flatten(p)
    print("\nDone.")
