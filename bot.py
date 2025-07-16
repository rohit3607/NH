import asyncio
from playwright.async_api import async_playwright
import time

BUTTON_SELECTORS = [
    'text=CONTINUE',
    'text="Dual Tap To \\"Go To Link\\""',
    'text="Click here"',
    'text=Go To Link'
]

async def click_with_retry(page, selector, retries=3, wait=10):
    for attempt in range(1, retries + 1):
        try:
            btn = await page.wait_for_selector(selector, timeout=10000)
            await btn.scroll_into_view_if_needed()
            await btn.click()
            print(f"[INFO] Clicked button: {selector}")
            return True
        except Exception:
            print(f"[WARN] Button not clickable or not found. Retrying in {wait}s... (Retry {attempt}/{retries})")
            await asyncio.sleep(wait)
    print("[ERROR] Could not click button after retries. Ending.")
    return False

async def bypass_redirect(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[INFO] Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        step = 1

        while True:
            current_url = page.url
            print(f"[STEP {step}] Current URL: {current_url}")

            # First step wait
            if step == 1:
                print("[INFO] Waiting 15s before clicking first CONTINUE...")
                await asyncio.sleep(15)

                if not await click_with_retry(page, 'text=CONTINUE'):
                    break

            else:
                # Wait 15s for popup ads to settle
                print("[INFO] Waiting 15s before clicking any button...")
                await asyncio.sleep(15)

                # Try all known button selectors
                clicked = False
                for selector in BUTTON_SELECTORS:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            print(f"[INFO] Found button: {await btn.inner_text()}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click()
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    print("[WARN] No known button found. Retrying in 10s...")
                    await asyncio.sleep(10)
                    continue

            await page.wait_for_timeout(5000)  # Wait 5s after click
            if page.url == current_url:
                print("[WARN] URL didn't change. Retrying step...")
                continue

            step += 1

            # Break on external redirect (non-intermediate page)
            if not any(domain in page.url for domain in ['movieverse.life', 'kaomojihub.com', 'sudyon']):
                print(f"[✅ SUCCESS] Final URL: {page.url}")
                break

        await browser.close()

# Run this
if __name__ == "__main__":
    url = "https://vplink.in/aUMMULUS"  # replace with your actual input URL
    asyncio.run(bypass_redirect(url))