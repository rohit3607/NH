import asyncio
import sys
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

async def resolve_vplink(url):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until='domcontentloaded')
        step = 1

        while True:
            print(f"[STEP {step}] Current URL: {page.url}")
            step += 1

            # Try to find "Continue" or other buttons
            btn = await page.query_selector("text=Continue") or await page.query_selector("button")
            if btn:
                try:
                    print(f"[INFO] Found button: {await btn.inner_text()}")
                    await btn.click()
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"[WARN] Button not clickable yet. Retrying after 15 seconds... ({str(e)})")
                    await page.wait_for_timeout(15000)
                    try:
                        await btn.click()
                        await page.wait_for_timeout(3000)
                    except Exception as e:
                        print("[ERROR] Still couldn't click button after retry.")
                        break
                continue

            # Handle "Get Link" page
            get_link_btn = await page.query_selector("text=Get Link")
            if get_link_btn:
                print("[INFO] Final Page Reached: Waiting for Get Link button to be enabled")
                await page.wait_for_timeout(6000)
                try:
                    await get_link_btn.click()
                    await page.wait_for_load_state('domcontentloaded')
                    print(f"[SUCCESS] Final Resolved URL: {page.url}")
                    return page.url
                except Exception as e:
                    print(f"[ERROR] Failed to click Get Link button. Retrying after 15 seconds... ({str(e)})")
                    await page.wait_for_timeout(15000)
                    try:
                        await get_link_btn.click()
                        await page.wait_for_load_state('domcontentloaded')
                        print(f"[SUCCESS] Final Resolved URL: {page.url}")
                        return page.url
                    except:
                        print("[ERROR] Still couldn't click Get Link after retry.")
                        return None

            # Handle cases where it's stuck
            if "vplink.in" in page.url and "get" not in (await page.content()).lower():
                print("[INFO] Possibly waiting for ad steps, trying to click any button...")
                await page.wait_for_timeout(10000)
                all_buttons = await page.query_selector_all("button")
                for b in all_buttons:
                    try:
                        await b.click()
                        await page.wait_for_timeout(3000)
                    except:
                        continue

            # Stop infinite loop
            if step > 10:
                print("[FAIL] Too many steps, exiting.")
                return None

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bot.py <shortlink>")
        sys.exit(1)

    url = sys.argv[1]
    final_url = asyncio.run(resolve_vplink(url))

    if final_url:
        print(f"✅   Final Link: {final_url}")
    else:
        print("❌   Failed to resolve final link.")