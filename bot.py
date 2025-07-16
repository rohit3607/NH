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
            special_dual_tap_clicked = False
            dual_tap_first = None

            while retry_count < max_retries and not clicked:
                buttons = await page.locator("button, a").all()

                for button in buttons:
                    try:
                        text = (await button.inner_text()).strip().upper()
                        # Handle step 2 special logic
                        if step == 2 and any(key in text for key in ["DUAL TAP", "CLICK HERE"]):
                            if not dual_tap_first:
                                print(f"[INFO] Step 2: Clicking first special button: {text}")
                                await button.scroll_into_view_if_needed()
                                await button.click(timeout=10000)
                                dual_tap_first = button
                                special_dual_tap_clicked = True
                                clicked = True
                                break
                        elif text in ["CONTINUE", "GET LINK", "GO TO LINK"]:
                            print(f"[INFO] Found button: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            clicked = True
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

            # Special handling for 2nd Dual Tap
            if special_dual_tap_clicked:
                print("[INFO] Waiting 5s after first Dual Tap...")
                await page.wait_for_timeout(5000)

                # Click second Dual Tap (should be a new instance)
                new_buttons = await page.locator("button, a").all()
                for btn in new_buttons[::-1]:  # Start from bottom
                    try:
                        if btn == dual_tap_first:
                            continue
                        text = (await btn.inner_text()).strip().upper()
                        if any(key in text for key in ["GO TO LINK", "CLICK HERE", "CONTINUE", "DUAL TAP"]):
                            print(f"[INFO] Clicking second special button: {text}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=10000)
                            await page.wait_for_timeout(15000)  # Wait after second click
                            break
                    except:
                        continue

                # Look for another button after 15s
                more_buttons = await page.locator("button, a").all()
                found = False
                for btn in more_buttons:
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if any(t in text for t in ["CONTINUE", "GO TO LINK", "CLICK HERE"]):
                            print(f"[INFO] Clicking post-DualTap button: {text}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=10000)
                            found = True
                            break
                    except:
                        continue

                if not found:
                    print("[INFO] No button found after 15s. Waiting 10 more seconds...")
                    await page.wait_for_timeout(10000)

            await page.wait_for_timeout(2000)

            # Final Check
            if "vplink.in" in page.url and "go" in page.url:
                print("[INFO] On vplink.in final page. Looking for GET LINK...")
                await page.wait_for_timeout(8000)
                buttons = await page.locator("a").all()
                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if "GET LINK" in text:
                            href = await btn.get_attribute("href")
                            print(f"[SUCCESS] Final Redirect URL: {href}")
                            await browser.close()
                            return
                    except:
                        continue

                # If no button found, fallback to current page
                print(f"[SUCCESS] Final URL: {page.url}")
                await browser.close()
                return

            step += 1

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    asyncio.run(bypass_vplink(link))