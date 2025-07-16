import sys
import asyncio
from playwright.async_api import async_playwright

async def bypass_vplink(url):
    print(f"[INFO] Navigating to: {url]")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        last_url = ""
        step = 1
        seen_urls = set()

        while True:
            current_url = page.url
            print(f"[STEP {step}] Current URL: {current_url}")

            # Avoid looping on same URL
            if current_url in seen_urls:
                print("❌  Stuck in loop. Aborting.")
                break
            seen_urls.add(current_url)

            # Final step: official vplink.in domain
            if "vplink.in" in current_url and "/go/" not in current_url:
                print("[INFO] Waiting 5s for final Get Link button...")
                await page.wait_for_timeout(5000)
                try:
                    btn = await page.wait_for_selector("a#generate", timeout=10000)
                    final = await btn.get_attribute("href")
                    print(f"✅ Final URL: {final}")
                except:
                    print("❌ Could not find final Get Link button.")
                break

            # First Page: Wait 15s before clicking Continue
            if step == 1:
                print("[INFO] Waiting 15s before clicking first CONTINUE...")
                await page.wait_for_timeout(15000)

            # Click the "Continue" button if available
            try:
                button = await page.query_selector("a:has-text('Continue')")
                if button:
                    print("[INFO] Found button: CONTINUE")
                    await button.click()
                else:
                    print("[WARN] Couldn't click continue button.")
                    break
            except:
                print("[WARN] Error clicking continue.")
                break

            # Second page (double tap logic)
            if step == 2:
                print("[INFO] Double tap logic with 5s delay...")
                await page.wait_for_timeout(5000)
                for _ in range(2):
                    try:
                        button = await page.query_selector("a:has-text('Continue')")
                        if button:
                            await button.click()
                            await page.wait_for_timeout(1000)
                    except:
                        pass

            # Third page: wait 10 seconds
            if step == 3:
                print("[INFO] Waiting 10s before clicking Continue...")
                await page.wait_for_timeout(10000)

            await page.wait_for_timeout(3000)
            step += 1

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
    else:
        asyncio.run(bypass_vplink(sys.argv[1]))