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
        already_clicked_step2 = False

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

            buttons = await page.locator("button, a").all()

            if step == 2 and not already_clicked_step2:
                # Click first button
                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if any(key in text for key in ["DUAL TAP", "CLICK HERE", "GO TO LINK"]):
                            print(f"[STEP 2] Clicking first button: {text}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click(timeout=10000)
                            clicked = True
                            break
                    except:
                        continue

                if clicked:
                    print("[STEP 2] First button clicked. Scrolling and searching for next...")
                    await page.wait_for_timeout(5000)
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(3000)

                    # Find second button with same name
                    buttons = await page.locator("button, a").all()
                    for btn in reversed(buttons):
                        try:
                            text = (await btn.inner_text()).strip().upper()
                            if any(key in text for key in ["DUAL TAP", "CLICK HERE", "GO TO LINK"]):
                                print(f"[STEP 2] Clicking second button: {text}")
                                await btn.scroll_into_view_if_needed()
                                await btn.click(timeout=10000)
                                clicked = True
                                already_clicked_step2 = True
                                break
                        except:
                            continue

            else:
                # Regular click attempt
                while retry_count < max_retries and not clicked:
                    buttons = await page.locator("button, a").all()
                    for button in buttons:
                        try:
                            text = (await button.inner_text()).strip().upper()
                            if any(t in text for t in ["CONTINUE", "GET LINK", "GO TO LINK", "CLICK HERE"]):
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

            # Step 3: Wait and retry click after redirect
            if step == 3:
                print("[STEP 3] Redirected to new page. Waiting 15s...")
                await page.wait_for_timeout(15000)
                buttons = await page.locator("button, a").all()
                for button in buttons:
                    try:
                        text = (await button.inner_text()).strip().upper()
                        if any(t in text for t in ["GET LINK", "CONTINUE", "CLICK HERE", "GO TO LINK"]):
                            print(f"[STEP 3] Clicking button: {text}")
                            await button.scroll_into_view_if_needed()
                            await button.click(timeout=10000)
                            clicked = True
                            break
                    except:
                        continue

            # Step 4: If another redirect without click
            elif step == 4:
                print("[STEP 4] Waiting 8s on final page...")
                await page.wait_for_timeout(8000)

                if "vplink.in" in page.url:
                    links = await page.locator("a").all()
                    for link in links:
                        try:
                            text = (await link.inner_text()).strip().upper()
                            if "GET LINK" in text:
                                href = await link.get_attribute("href")
                                print(f"[SUCCESS] Final Download URL: {href}")
                                await browser.close()
                                return href
                        except:
                            continue

            if "vplink.in" in page.url and "go" in page.url:
                print(f"[SUCCESS] Final Link: {page.url}")
                break

            step += 1
            await page.wait_for_timeout(2000)

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    asyncio.run(bypass_vplink(link))