import asyncio
from playwright.async_api import async_playwright
import time, sys

async def bypass_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        step = 1
        first_page = True

        previously_clicked_texts = set()

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
            special_dual_tap_clicked = False

            while retry_count < max_retries and not clicked:
                buttons = await page.locator("button, a").all()

                for button in buttons:
                    try:
                        text = (await button.inner_text()).strip().upper()

                        if text in previously_clicked_texts:
                            continue  # skip already clicked buttons

                        if step == 2 and any(key in text for key in ["DUAL TAP", "CLICK HERE"]):
                            print(f"[INFO] Step 2 Special Button Found: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            special_dual_tap_clicked = True
                            clicked = True
                            previously_clicked_texts.add(text)
                            break

                        elif text in ["CONTINUE", "GET LINK", "GO TO LINK"]:
                            print(f"[INFO] Found button: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            clicked = True
                            previously_clicked_texts.add(text)
                            break
                    except:
                        continue

                if not clicked:
                    retry_count += 1
                    print(f"[WARN] Button not clickable or not found. Retrying in 10s... (Retry {retry_count}/{max_retries})")
                    await page.wait_for_timeout(10000)

            if not clicked:
                print("[ERROR] Could not click button after retries. Ending.")
                break

            if special_dual_tap_clicked:
                print("[INFO] Waiting 5s after clicking Dual Tap...")
                await page.wait_for_timeout(5000)

                # After waiting, find a new button (not previously clicked)
                new_buttons = await page.locator("button, a").all()
                for btn in reversed(new_buttons):  # bottom-first
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if text in previously_clicked_texts:
                            continue
                        if any(key in text for key in ["GO TO LINK", "CLICK HERE", "CONTINUE", "DUAL TAP"]):
                            print(f"[INFO] Clicking newly appeared button: {text}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=10000)
                            await page.wait_for_timeout(5000)
                            previously_clicked_texts.add(text)
                            break
                    except:
                        continue

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