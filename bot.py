import asyncio
from playwright.async_api import async_playwright
import time, sys

BUTTON_SELECTORS = [
    'text=CONTINUE',
    'text="Dual Tap To \\"Go To Link\\""',
    'text="Click here"',
    'text=Go To Link'
]

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

            if first_page:
                print("[INFO] Waiting 15s before clicking first CONTINUE...")
                await page.wait_for_timeout(15000)
                first_page = False

            retry_count = 0
            max_retries = 3
            clicked = False

            while retry_count < max_retries and not clicked:
                buttons = await page.locator("button, a").all()

                for button in buttons:
                    try:
                        text = (await button.inner_text()).strip().upper()

                        # Handle Dual Tap / Click Here logic in step 2
                        if step == 2 and text in ["DUAL TAP TO \"GO TO LINK\"", "CLICK HERE"]:
                            print(f"[STEP 2] Clicking: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            await page.wait_for_timeout(5000)

                            # Try finding the same button again and click
                            buttons2 = await page.locator("button, a").all()
                            for b2 in buttons2:
                                try:
                                    t2 = (await b2.inner_text()).strip().upper()
                                    if t2 == text:
                                        print(f"[STEP 2] Clicking again: {t2}")
                                        await b2.scroll_into_view_if_needed()
                                        await b2.click(timeout=10000)
                                        clicked = True
                                        await page.wait_for_timeout(5000)
                                        break
                                except:
                                    continue
                            break

                        elif text in ["CONTINUE", "GET LINK", "GO TO LINK"]:
                            print(f"[INFO] Found button: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            clicked = True

                            # Wait based on step (approx delays after each button)
                            if text == "GET LINK":
                                await page.wait_for_timeout(3000)
                            elif step == 2:
                                await page.wait_for_timeout(5000)
                            elif step == 3:
                                await page.wait_for_timeout(5000)
                            elif step == 4:
                                await page.wait_for_timeout(10000)
                            break
                    except Exception:
                        continue

                if not clicked:
                    retry_count += 1
                    print(f"[WARN] Button not clickable or not found. Retrying in 10s... (Retry {retry_count}/{max_retries})")
                    await page.wait_for_timeout(10000)

            if not clicked:
                print("[ERROR] Could not click button after retries. Ending.")
                break

            await page.wait_for_timeout(2000)

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