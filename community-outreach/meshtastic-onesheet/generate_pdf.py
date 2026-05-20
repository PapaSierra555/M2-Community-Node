import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    html_path = os.path.abspath("ccc_meshtastic_onesheet.html").replace("\\", "/")
    pdf_path = os.path.abspath("ccc_meshtastic_onesheet.pdf")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{html_path}", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.pdf(
            path=pdf_path,
            format="Letter",
            landscape=True,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )
        await browser.close()
    print(f"PDF saved: {pdf_path}")

asyncio.run(main())
