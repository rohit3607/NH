import asyncio
import sys
from playwright.async_api import async_playwright

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

            # Handle "Continue" or similar buttons
            btn = await page.query_selector("text=Continue") or await page.query_selector("button")
            if btn:
                try:
                    print(f"[INFO] Found button: {await btn.inner_text()}")
                    await btn.click()
                    await page.wait_for_timeout(3000)
                except:
                    print("[WARN] Couldn't click continue button.")
                    break
                continue

            # Handle step with countdown
            if "wait" in page.content().lower():
                print("[INFO] Waiting for timer...")
                await page.wait_for_timeout(15000)

            # Check if final page with Get Link button
            get_link_btn = await page.query_selector("text=Get Link")
            if get_link_btn:
                print("[INFO] Final Page Reached: Waiting for Get Link button to be enabled")
                await page.wait_for_timeout(6000)  # wait 5-6 seconds
                try:
                    await get_link_btn.click()
                    await page.wait_for_load_state('domcontentloaded')
                    print(f"[SUCCESS] Final Resolved URL: {page.url}")
                    return page.url
                except:
                    print("[ERROR] Failed to click Get Link button.")
                    return None

            # Prevent infinite loop
            if "vplink.in" in page.url and "get" not in page.content().lower():
                await page.wait_for_timeout(10000)
                all_buttons = await page.query_selector_all("button")
                for b in all_buttons:
                    try:
                        await b.click()
                        await page.wait_for_timeout(3000)
                    except:
                        continue

            # Safety exit
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