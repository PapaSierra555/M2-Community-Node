"""Build ccc_meshtastic_onesheet.html — CCC/LFHI branding, portrait, print-ready."""
import qrcode, base64, io, asyncio, os, urllib.request
from playwright.async_api import async_playwright

def make_qr_b64(url):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f0f0f", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def read_local_b64(path, mime="image/png"):
    with open(path, "rb") as f:
        data = f.read()
    return f"data:{mime};base64," + base64.b64encode(data).decode()

def fetch_b64(url, mime=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        data = r.read()
    if mime is None:
        ext = url.split("?")[0].split(".")[-1].lower()
        mime = {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
                "svg":"image/svg+xml","webp":"image/webp"}.get(ext,"image/png")
    return f"data:{mime};base64," + base64.b64encode(data).decode()

FLASHER = "https://raw.githubusercontent.com/meshtastic/web-flasher/main/public/img/devices/"

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")

print("Loading LFHI logo...")
logo_b64 = read_local_b64(os.path.join(ASSETS, "lfhi-logo.png"))

print("Generating QR codes...")
android_qr = make_qr_b64("https://play.google.com/store/apps/details?id=com.geeksville.mesh")
iphone_qr  = make_qr_b64("https://apps.apple.com/us/app/meshtastic/id1586432531")

print("Fetching device SVGs from Meshtastic project...")
techo_svg    = fetch_b64(FLASHER + "t-echo.svg",                "image/svg+xml")
tdeck_svg    = fetch_b64(FLASHER + "t-deck.svg",                "image/svg+xml")
heltec_svg   = fetch_b64(FLASHER + "heltec-mesh-node-t114.svg", "image/svg+xml")
sensecap_svg = fetch_b64(FLASHER + "tracker-t1000-e.svg",       "image/svg+xml")

html_out = os.path.abspath("ccc_meshtastic_onesheet.html")

with open(html_out, "w", encoding="utf-8") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>M2 Community Node — Meshtastic Field Guide</title>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;900&family=Instrument+Sans:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  @page {{ size: letter portrait; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    width: 8.5in; height: 11in;
    font-family: 'Instrument Sans', sans-serif;
    font-size: 11px; line-height: 1.72;
    background: #fff; color: #1a1a1a;
    overflow: hidden;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* ── HEADER ── */
  .hdr {{
    background: #1a1a1a; color: #fff;
    height: 0.82in;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0.32in;
    border-bottom: 3px solid #921212;
  }}
  .hbrand {{ display: flex; align-items: center; gap: 11px; }}
  .hbrand img {{ width: 50px; height: 50px; object-fit: contain; }}
  .org {{ font-family: 'Big Shoulders Display', sans-serif; font-size: 20px; font-weight: 900; line-height: 1; color: #fff; letter-spacing: 0.02em; }}
  .orgsub {{ font-size: 8px; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.55); margin-top: 3px; }}
  .htitle {{ text-align: right; }}
  .htitle h1 {{ font-family: 'Big Shoulders Display', sans-serif; font-size: 18px; font-weight: 900; line-height: 1.1; text-transform: uppercase; letter-spacing: 0.04em; color: #fff; }}
  .htag {{ font-size: 8px; letter-spacing: 0.2em; text-transform: uppercase; color: #921212; margin-top: 4px; font-weight: 700; }}

  /* ── BODY ── */
  .body {{
    display: flex;
    height: calc(11in - 0.82in - 0.52in);
    padding: 0.22in 0.32in 0.18in;
    gap: 0.28in;
  }}

  /* ── COLUMNS ── */
  .lcol {{
    flex: 0.95;
    display: flex; flex-direction: column;
  }}
  .lcol .top {{ flex: 1; }}
  .rcol {{
    flex: 1.05;
    display: flex; flex-direction: column;
    border-left: 2px solid #921212;
    padding-left: 0.24in;
  }}
  .rcol .top {{ flex: 1; }}

  /* ── HEADING HIERARCHY ── */
  h2 {{
    font-family: 'Big Shoulders Display', sans-serif;
    font-size: 13px; font-weight: 900;
    color: #921212; text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 2px solid #921212; padding-bottom: 4px;
    margin-bottom: 9px;
  }}
  h2.section-break {{ margin-top: 0.17in; }}
  h3 {{
    font-family: 'Big Shoulders Display', sans-serif;
    font-size: 11px; font-weight: 700;
    color: #1a1a1a; text-transform: uppercase; letter-spacing: 0.1em;
    border-left: 3px solid #921212; padding-left: 7px;
    margin-top: 13px; margin-bottom: 5px;
  }}
  h4 {{
    font-family: 'Big Shoulders Display', sans-serif;
    font-size: 10px; font-weight: 700;
    color: #555; text-transform: uppercase; letter-spacing: 0.12em;
    margin-top: 11px; margin-bottom: 4px;
  }}

  /* ── BODY TEXT ── */
  p {{ margin-bottom: 8px; color: #333; }}
  p:last-child {{ margin-bottom: 0; }}
  strong {{ color: #1a1a1a; }}
  a {{ color: #921212; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  /* ── LISTS ── */
  ul.plain {{ list-style: none; padding: 0; margin-bottom: 8px; }}
  ul.plain li {{
    padding-left: 14px; position: relative;
    margin-bottom: 5px; color: #333; font-size: 10.5px; line-height: 1.65;
  }}
  ul.plain li::before {{ content: '—'; position: absolute; left: 0; color: #921212; font-weight: 700; }}

  ul.sub {{ list-style: none; padding: 0; margin: 3px 0 4px; }}
  ul.sub li {{
    padding-left: 10px; position: relative;
    font-size: 9.5px; color: #555; margin-bottom: 2px; line-height: 1.5;
  }}
  ul.sub li::before {{ content: '•'; position: absolute; left: 0; color: #921212; }}

  /* ── HARDWARE ── */
  .hw-item {{ display: flex; gap: 8px; margin-bottom: 10px; align-items: flex-start; }}
  .hw-img {{ height: 46px; width: 40px; object-fit: contain; flex-shrink: 0; margin-top: 2px; }}
  .hw-price {{
    font-family: 'Big Shoulders Display', sans-serif;
    font-size: 14px; font-weight: 900; color: #921212;
    flex-shrink: 0; width: 34px; padding-top: 1px;
  }}
  .hw-detail {{ font-size: 10px; color: #333; line-height: 1.5; }}
  .hw-name {{ font-weight: 700; color: #1a1a1a; display: block; margin-bottom: 2px; font-size: 10.5px; }}
  .hw-name a {{ font-weight: 700; color: #1a1a1a; }}
  .hw-name a:hover {{ color: #921212; }}

  /* ── APPS ── */
  .app-row {{ display: flex; gap: 0.2in; margin-top: 8px; margin-bottom: 6px; }}
  .app-item {{ display: flex; gap: 8px; align-items: center; }}
  .app-item img {{ width: 62px; height: 62px; border: 1px solid #ccc; border-radius: 3px; display: block; }}
  .app-lbl {{ font-weight: 700; font-size: 10.5px; }}
  .app-lbl a {{ color: #1a1a1a; }}
  .app-sub {{ font-size: 9px; color: #888; margin-top: 2px; }}
  .app-link {{ font-size: 8.5px; margin-top: 3px; }}
  .app-link a {{ color: #921212; }}

  /* ── NOTE ── */
  .note {{
    margin-top: 9px; padding: 7px 10px;
    border-left: 3px solid #921212;
    background: #f5e8e8;
    border-radius: 0 3px 3px 0;
    font-size: 10px; color: #1a1a1a; line-height: 1.6;
  }}

  /* ── FOOTER ── */
  .ftr {{
    background: #1a1a1a; color: #fff;
    height: 0.52in;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0.32in;
    border-top: 3px solid #921212;
    flex-shrink: 0;
  }}
  .ftr-brand {{ display: flex; align-items: center; gap: 9px; }}
  .ftr-brand img {{ height: 34px; width: 34px; object-fit: contain; flex-shrink: 0; }}
  .ftr-name {{ font-family: 'Big Shoulders Display', sans-serif; font-size: 11px; font-weight: 900; color: #fff; text-transform: uppercase; letter-spacing: 0.08em; line-height: 1; margin-bottom: 3px; }}
  .ftr-contact {{ font-size: 8px; color: rgba(255,255,255,0.55); line-height: 1; }}
  .ftr-contact a {{ color: #c84040; font-weight: 700; text-decoration: none; }}
  .ftr-attr {{ font-size: 7.5px; color: rgba(255,255,255,0.3); text-align: right; line-height: 1.6; }}
  .ftr-attr a {{ color: rgba(255,255,255,0.3); text-decoration: none; }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="hbrand">
    <img src="{logo_b64}" alt="LFHI Logo"/>
    <div>
      <div class="org">M2 Community Node</div>
      <div class="orgsub">Carolina Capabilities Co-Op &nbsp;•&nbsp; LFHI</div>
    </div>
  </div>
  <div class="htitle">
    <h1>Meshtastic Field Guide</h1>
    <div class="htag">Radio Mesh Communications</div>
  </div>
</div>

<!-- BODY -->
<div class="body">

  <!-- ════ LEFT COLUMN ════ -->
  <div class="lcol">
    <div class="top">

      <h2>What is Meshtastic?</h2>
      <p>Meshtastic turns a small handheld radio into a private group messaging device — no cell
      service, no WiFi, no internet required. The radio pairs to a free app on your phone over
      Bluetooth. Everyone on the same network can send and receive text messages, and the network
      stays up even when all other communications fail.</p>
      <p>At an M2 Node deployment, Meshtastic extends your radio reach beyond the node's WiFi
      footprint. Learn more at <a href="https://meshtastic.org">meshtastic.org</a>.</p>

      <h3>Why Meshtastic for Community Preparedness?</h3>
      <p>Meshtastic is free, open-source, and completely off-grid. Radios communicate directly with
      each other — no phone company, no server, no single point of failure. A small group of
      3–5 radios can cover a neighborhood, an event site, or a deployment area with no
      infrastructure at all.</p>

      <h3>How Can I Get Started?</h3>
      <p>At any M2 Node activation, Meshtastic radios will be on the network. Install the free app,
      ask the network operator to add you to the active channel, and you're live. If you'd like
      your own radio for future deployments, see the options to the right.</p>
      <div class="note"><strong>Field note:</strong> Use a dedicated or secondary device when
      possible — an old phone with no SIM card works perfectly. Keep your primary device
      available for other mission needs.</div>

      <h3>Security &amp; Operational Tips</h3>
      <ul class="plain">
        <li>No cell network or internet required — radios talk directly to each other,
        up to several kilometers range depending on terrain.</li>
        <li>Turn on Airplane Mode, then re-enable Bluetooth only. Your phone connects
        to the radio and nothing else.</li>
        <li>An old phone or tablet with no SIM card works perfectly.
        No carrier plan needed.</li>
      </ul>

    </div><!-- /top -->
  </div><!-- /lcol -->

  <!-- ════ RIGHT COLUMN ════ -->
  <div class="rcol">
    <div class="top">

      <h2>App Download</h2>
      <p>Download the free Meshtastic app for your phone. Scan the QR code or search
      <strong>Meshtastic</strong> in your app store.</p>

      <div class="app-row">
        <div class="app-item">
          <img src="{android_qr}" alt="Android QR"/>
          <div>
            <div class="app-lbl"><a href="https://play.google.com/store/apps/details?id=com.geeksville.mesh">Android App</a></div>
            <div class="app-sub">Google Play Store</div>
            <div class="app-link"><a href="https://play.google.com/store/apps/details?id=com.geeksville.mesh">play.google.com</a></div>
          </div>
        </div>
        <div class="app-item">
          <img src="{iphone_qr}" alt="iPhone QR"/>
          <div>
            <div class="app-lbl"><a href="https://apps.apple.com/us/app/meshtastic/id1586432531">iPhone App</a></div>
            <div class="app-sub">Apple App Store</div>
            <div class="app-link"><a href="https://apps.apple.com/us/app/meshtastic/id1586432531">apps.apple.com</a></div>
          </div>
        </div>
      </div>

      <h2 class="section-break">Hardware Options</h2>
      <p>Most devices are ready to use out of the box. Prices listed are approximate.</p>

      <div class="hw-item">
        <img class="hw-img" src="{sensecap_svg}" alt="SenseCAP T1000-E"/>
        <div class="hw-price">$40</div>
        <div class="hw-detail">
          <span class="hw-name"><a href="https://www.seeedstudio.com/SenseCAP-Card-Tracker-T1000-E-for-Meshtastic-p-5913.html">SenseCAP T1000-E</a></span>
          <ul class="sub">
            <li>Credit card size — easy to carry or clip to gear</li>
            <li>Includes GPS location tracking</li>
          </ul>
        </div>
      </div>

      <h4>Heltec T114 — Two Options</h4>

      <div class="hw-item">
        <img class="hw-img" src="{heltec_svg}" alt="Heltec T114"/>
        <div class="hw-price">$43</div>
        <div class="hw-detail">
          <span class="hw-name"><a href="https://store.rokland.com/products/heltec-mesh-node-t114-with-optional-1-14-inch-tft-display?variant=43214881947731">Heltec T114 (Rokland)</a></span>
          <ul class="sub">
            <li>Board only — you supply a battery and case</li>
            <li>Many free 3D-printable case designs available</li>
          </ul>
        </div>
      </div>

      <div class="hw-item">
        <img class="hw-img" src="{heltec_svg}" alt="Heltec T114 Kit"/>
        <div class="hw-price">$50</div>
        <div class="hw-detail">
          <span class="hw-name"><a href="https://www.amazon.com/Heltec-Meshtastic-T114-Crabiner-Bluetooth/dp/B0F3X3WNJP">Heltec T114 Kit (Amazon)</a></span>
          <ul class="sub">
            <li>Best battery life — good for extended field use</li>
            <li>Battery, case, and GPS included — snap together, no soldering</li>
          </ul>
        </div>
      </div>

      <div class="hw-item">
        <img class="hw-img" src="{techo_svg}" alt="LILYGO T-Echo"/>
        <div class="hw-price">$53</div>
        <div class="hw-detail">
          <span class="hw-name"><a href="https://lilygo.cc/products/t-echo-meshtastic">LILYGO T-Echo</a></span>
          <ul class="sub">
            <li>Ready to use out of the box — GPS included, no assembly</li>
            <li>Ships from US or China warehouses</li>
          </ul>
        </div>
      </div>

      <h4>LILYGO T-Deck — No Phone Needed</h4>
      <p style="font-size:9.5px; color:#666; margin-bottom:5px; line-height:1.55;">A fully
      self-contained device with built-in keyboard and screen — no phone required.
      Often out of stock in the US; check before ordering.</p>

      <div class="hw-item">
        <img class="hw-img" src="{tdeck_svg}" alt="LILYGO T-Deck Plus"/>
        <div class="hw-price">$82</div>
        <div class="hw-detail">
          <span class="hw-name"><a href="https://lilygo.cc/products/t-deck-plus-meshtastic?variant=51953085382837">LILYGO T-Deck Plus</a></span>
          <ul class="sub">
            <li>Docs: <a href="https://meshtastic.org/docs/hardware/devices/lilygo/tdeck/" style="color:#921212;">meshtastic.org/docs/…/tdeck</a></li>
          </ul>
        </div>
      </div>

      <p style="margin-top:8px; font-size:8px; color:#bbb; line-height:1.6;">
        Full hardware list: <a href="https://meshtastic.org/docs/hardware/" style="color:#bbb;">meshtastic.org/docs/hardware</a>
      </p>

    </div><!-- /top -->
  </div><!-- /rcol -->

</div><!-- /body -->

<!-- FOOTER -->
<div class="ftr">
  <div class="ftr-brand">
    <img src="{logo_b64}" alt="LFHI"/>
    <div>
      <div class="ftr-name">M2 Community Node</div>
      <div class="ftr-contact">
        <a href="https://www.carolinacapabilitiesco-op.com/">carolinacapabilitiesco-op.com</a>
        &nbsp;•&nbsp;
        <a href="https://lightfighterhomefront.org/">lightfighterhomefront.org</a>
      </div>
    </div>
  </div>
  <div class="ftr-attr">
    Device illustrations © <a href="https://github.com/meshtastic/meshtastic">Meshtastic Project</a>, Apache 2.0<br/>
    <a href="https://meshtastic.org">meshtastic.org</a> &nbsp;•&nbsp; Open Source &nbsp;•&nbsp; CC BY-NC-SA 4.0
  </div>
</div>

</body>
</html>
""")

print(f"HTML written: {html_out}")

async def gen_pdf():
    pdf_out = os.path.abspath("ccc_meshtastic_onesheet.pdf")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("file:///" + html_out.replace("\\", "/"), wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.pdf(
            path=pdf_out,
            format="Letter",
            landscape=False,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        await browser.close()
    print(f"PDF saved: {pdf_out}")

asyncio.run(gen_pdf())
