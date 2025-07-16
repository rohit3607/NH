import sys
import asyncio
from playwright.async_api import async_playwright

async def bypass_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        step = 1
        first_page = True

        while True:
            print(f"[STEP {step}] Current URL: {page.url}")
            await page.wait_for_timeout(1000)

            # Wait 15s only on the first page before any click
            if first_page:
                print("[INFO] Waiting 15s before clicking first CONTINUE...")
                await page.wait_for_timeout(15000)
                first_page = False

            buttons = await page.locator("button, a").all()
            clicked = False

            for button in buttons:
                try:
                    text = (await button.inner_text()).strip().upper()
                    if text in ["CONTINUE", "GET LINK"]:
                        print(f"[INFO] Found button: {text}")
                        await button.scroll_into_view_if_needed()
                        await button.click(timeout=10000)
                        clicked = True

                        # Wait based on step (for known flow)
                        if text == "GET LINK":
                            await page.wait_for_timeout(3000)
                        elif step == 2:
                            await page.wait_for_timeout(5000)  # wait 5s after first CONTINUE
                        elif step == 3:
                            await page.wait_for_timeout(5000)
                        elif step == 4:
                            await page.wait_for_timeout(10000)
                        break
                except Exception as e:
                    continue

            if not clicked:
                print("[WARN] No clickable buttons found on this step. Ending.")
                break

            # Wait a moment after click
            await page.wait_for_timeout(2000)

            # Check if on vplink final domain
            if "vplink.in" in page.url and "go" in page.url:
                print(f"[SUCCESS] Final Link: {page.url}")
                break

            step += 1

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    asyncio.run(bypass_vplink(link))