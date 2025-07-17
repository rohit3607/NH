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
        already_clicked_step2 = False
        clicked_elements = set()

        while True:
            current_url = page.url
            print(f"[STEP {step}] Current URL: {current_url}")
            await page.wait_for_timeout(1000)

            if first_page:
                print("[STEP 1] Waiting 15s before clicking first CONTINUE...")
                await page.wait_for_timeout(15000)
                first_page = False

            retry_count = 0
            max_retries = 3
            clicked = False

            buttons = await page.locator("button, a").all()

            # -------- STEP 2 SPECIAL HANDLING -------- #
            if step == 2 and not already_clicked_step2:
                print("[STEP 2] Waiting 15s before clicking first button...")
                await page.wait_for_timeout(15000)

                # Click first valid button
                for i, btn in enumerate(buttons):
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if any(key in text for key in ["DUAL TAP", "CLICK HERE", "GO TO LINK"]):
                            element_key = f"step2-first-{i}"
                            if element_key not in clicked_elements:
                                print(f"[STEP 2] Clicking first button: {text}")
                                await btn.scroll_into_view_if_needed()
                                await btn.click(timeout=10000)
                                clicked_elements.add(element_key)
                                clicked = True
                                break
                    except:
                        continue

                if clicked:
                    print("[STEP 2] First button clicked. Scrolling and searching for second button...")
                    await page.wait_for_timeout(5000)
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(3000)

                    # Find and click second button
                    buttons = await page.locator("button, a").all()
                    for i, btn in enumerate(reversed(buttons)):
                        try:
                            text = (await btn.inner_text()).strip().upper()
                            if any(key in text for key in ["DUAL TAP", "CLICK HERE", "GO TO LINK"]):
                                element_key = f"step2-second-{i}"
                                if element_key not in clicked_elements:
                                    print(f"[STEP 2] Clicking second button: {text}")
                                    await btn.scroll_into_view_if_needed()
                                    await btn.click(timeout=10000)
                                    clicked_elements.add(element_key)
                                    already_clicked_step2 = True
                                    clicked = True
                                    break
                        except:
                            continue

            # -------- STEP 3: Retry Click After Redirect -------- #
            elif step == 3:
                print("[STEP 3] Waiting 15s before retrying click...")
                await page.wait_for_timeout(15000)
                buttons = await page.locator("button, a").all()
                for i, button in enumerate(buttons):
                    try:
                        text = (await button.inner_text()).strip().upper()
                        if any(t in text for t in ["GET LINK", "CONTINUE", "CLICK HERE", "GO TO LINK"]):
                            element_key = f"step3-{i}"
                            if element_key not in clicked_elements:
                                print(f"[STEP 3] Clicking button: {text}")
                                await button.scroll_into_view_if_needed()
                                await button.click(timeout=10000)
                                clicked_elements.add(element_key)
                                clicked = True
                                break
                    except:
                        continue

            # -------- STEP 4: Auto Redirect to Final Page -------- #
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

            # -------- REGULAR BUTTON CLICK RETRY -------- #
            else:
                while retry_count < max_retries and not clicked:
                    buttons = await page.locator("button, a").all()
                    for i, button in enumerate(buttons):
                        try:
                            text = (await button.inner_text()).strip().upper()
                            if any(t in text for t in ["CONTINUE", "GET LINK", "GO TO LINK", "CLICK HERE"]):
                                element_key = f"step{step}-{i}"
                                if element_key not in clicked_elements:
                                    print(f"[STEP {step}] Clicking button: {text}")
                                    await button.scroll_into_view_if_needed()
                                    await button.click(timeout=10000)
                                    clicked_elements.add(element_key)
                                    clicked = True
                                    break
                        except:
                            continue

                    if not clicked:
                        retry_count += 1
                        print(f"[WARN] Button not clickable or not found. Retrying in 10s... (Retry {retry_count}/{max_retries})")
                        await page.wait_for_timeout(10000)

            # -------- FINAL PAGE CHECK -------- #
            if "vplink.in" in page.url and "go" in page.url:
                print(f"[SUCCESS] Final Redirect URL: {page.url}")
                break

            # -------- STEP TRANSITION CHECK -------- #
            await page.wait_for_timeout(3000)
            new_url = page.url

            if new_url != current_url:
                print(f"[INFO] URL changed → Proceeding to Step {step + 1}")
                step += 1
            else:
                print(f"[WARN] Still on same URL. Staying in Step {step}")

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    asyncio.run(bypass_vplink(link))