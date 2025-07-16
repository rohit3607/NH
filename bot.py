import asyncio
from playwright.async_api import async_playwright

async def wait_and_click(page, button_text, timeout=30):
    for attempt in range(3):
        try:
            await page.wait_for_timeout(3000)  # let popups settle
            button = await page.query_selector(f'button:has-text("{button_text}")')
            if button:
                await button.scroll_into_view_if_needed()
                await button.click(timeout=timeout * 1000)
                print(f"[INFO] Clicked button: {button_text}")
                return True
            else:
                print(f"[WARN] Button '{button_text}' not found. Retrying in 10s... (Retry {attempt + 1}/3)")
                await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"[WARN] Error clicking '{button_text}': {e}. Retrying... (Retry {attempt + 1}/3)")
            await page.wait_for_timeout(10000)
    return False

async def run(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print(f"[INFO] Navigating to: {url}")
        await page.goto(url, timeout=60000)
        
        # STEP 1
        print(f"[STEP 1] Current URL: {page.url}")
        print("[INFO] Waiting 15s before clicking first CONTINUE...")
        await page.wait_for_timeout(15000)
        success = await wait_and_click(page, "CONTINUE")
        if not success:
            print("❌ Failed to click CONTINUE in Step 1")
            return

        # Wait for navigation after step 1
        await page.wait_for_load_state("networkidle")
        step2_url = page.url
        print(f"[STEP 2] Current URL: {step2_url}")
        
        # STEP 2
        print("[INFO] Waiting 15s before first DUAL TAP click...")
        await page.wait_for_timeout(15000)
        success = await wait_and_click(page, 'DUAL TAP TO "GO TO LINK"')
        if not success:
            print("❌ Failed to click first DUAL TAP button")
            return

        print("[INFO] Waiting 8s for next DUAL TAP button...")
        await page.wait_for_timeout(8000)

        # Scroll to bottom to help load new button
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Try clicking the second DUAL TAP
        success = await wait_and_click(page, 'DUAL TAP TO "GO TO LINK"')
        if not success:
            print("❌ Failed to click second DUAL TAP button")
            return

        # Wait for navigation again (Step 3)
        await page.wait_for_load_state("networkidle")
        final_url = page.url
        print(f"[STEP 3] Final URL: {final_url}")

        await browser.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 bot.py <vplink_url>")
    else:
        asyncio.run(run(sys.argv[1]))