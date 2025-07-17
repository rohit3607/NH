import asyncio
from playwright.async_api import async_playwright
import sys

async def bypass_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        step = 1
        previously_clicked = set()

        while True:
            print(f"[STEP {step}] Current URL: {page.url}")
            await page.wait_for_timeout(2000)

            # Wait on first page
            if step == 1:
                print("[INFO] Waiting 15s on initial page...")
                await page.wait_for_timeout(15000)

            # Click buttons
            buttons = await page.locator("button, a").all()
            clicked = False

            for button in buttons:
                try:
                    text = (await button.inner_text()).strip().upper()
                    if text in previously_clicked:
                        continue

                    if any(x in text for x in ["DUAL TAP", "CONTINUE", "CLICK HERE", "GO TO LINK", "GET LINK"]):
                        print(f"[INFO] Clicking button: {text}")
                        await button.scroll_into_view_if_needed()
                        await button.click(timeout=10000)
                        previously_clicked.add(text)
                        clicked = True
                        await page.wait_for_timeout(5000)
                        break
                except:
                    continue

            # On the final page with "Get Link" button (visible in video)
            if "vplink.in" in page.url and "go" in page.url:
                print("[INFO] Reached final VPLINK page, waiting 10s...")
                await page.wait_for_timeout(10000)

                final_buttons = await page.locator("a").all()
                for btn in final_buttons:
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        href = await btn.get_attribute("href")

                        if "GET LINK" in text and href and not href.startswith("javascript"):
                            print(f"[SUCCESS] Final Link Found: {href}")
                            await browser.close()
                            return href
                    except:
                        continue

                # fallback
                print("[WARN] Could not extract href, returning current page URL.")
                await browser.close()
                return page.url

            if not clicked:
                print("[WARN] No new button found to click. Waiting 10s...")
                await page.wait_for_timeout(10000)

            step += 1
            if step > 10:
                print("[ERROR] Too many steps, giving up.")
                break

        await browser.close()
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    final_link = asyncio.run(bypass_vplink(link))
    if final_link:
        print(f"\n✅ Bypassed Link: {final_link}")
    else:
        print("\n❌ Failed to bypass the link.")