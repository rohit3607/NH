import asyncio
from playwright.async_api import async_playwright

async def wait_and_click(page, selector, timeout=30000):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.locator(selector).click()
        print(f"[INFO] Clicked element: {selector}")
    except Exception as e:
        print(f"[ERROR] Failed to click {selector}: {e}")

async def dismiss_consent_popup(page):
    try:
        # Try closing the consent overlay if it exists
        overlay = page.locator("div.fc-consent-root, div.fc-dialog-overlay")
        if await overlay.is_visible():
            print("[INFO] Consent popup detected, trying to remove it...")
            await page.evaluate("document.querySelector('div.fc-consent-root')?.remove()")
            await page.evaluate("document.querySelector('div.fc-dialog-overlay')?.remove()")
            print("[INFO] Consent popup removed.")
    except Exception as e:
        print(f"[WARN] Could not dismiss consent popup: {e}")

async def run(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"[STEP 1] Opening URL: {url}")
        await page.goto(url)

        # Step 1: Wait 15 seconds
        print("[INFO] Waiting 15s before clicking first CONTINUE...")
        await asyncio.sleep(15)

        # Dismiss overlay blocking click
        await dismiss_consent_popup(page)

        # Click first "CONTINUE" button
        await wait_and_click(page, 'text=CONTINUE')

        # Step 2: Wait for the next page to load
        print("[STEP 2] Waiting for Dual Tap button...")
        await page.wait_for_selector("text=Dual Tap", timeout=10000)
        buttons = await page.locator("text=Dual Tap").all()
        if not buttons:
            print("[ERROR] No Dual Tap buttons found.")
            return

        print("[INFO] Clicking first Dual Tap button...")
        await buttons[0].click()

        # Wait 5 seconds for the second button to appear
        print("[INFO] Waiting 5s for second Dual Tap button to appear...")
        await asyncio.sleep(5)

        # Locate the new button at the bottom
        print("[INFO] Looking for new Dual Tap button...")
        updated_buttons = await page.locator("text=Dual Tap").all()
        if len(updated_buttons) > 1:
            print("[INFO] Clicking second Dual Tap button (bottom one)...")
            await updated_buttons[-1].click()
        else:
            print("[WARN] Only one Dual Tap button found, retrying...")

        # Proceed as needed
        print("[SUCCESS] Completed dual-tap flow.")

        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter URL: ")
    asyncio.run(run(url))