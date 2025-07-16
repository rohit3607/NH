import asyncio
import sys
from playwright.async_api import async_playwright

async def solve_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded")
        current_url = page.url
        last_url = ""
        step = 1

        try:
            while True:
                print(f"[STEP {step}] Current URL: {current_url}")

                # Exit if on final domain (vplink.in)
                if "vplink.in" in current_url and "get" in (await page.content()).lower():
                    print("[INFO] Final VPLINK page detected.")
                    await page.wait_for_timeout(5000)  # 5 sec wait
                    get_link = await page.query_selector('a:has-text("GET LINK")')
                    if get_link:
                        final_url = await get_link.get_attribute("href")
                        print(f"✅ Final URL: {final_url}")
                        await browser.close()
                        return final_url
                    else:
                        print("❌ GET LINK button not found.")
                        break

                # STEP 1: Initial Continue button
                btn = await page.query_selector('button:has-text("CONTINUE"), a:has-text("CONTINUE")')
                if btn:
                    print(f"[INFO] Found button: CONTINUE")
                    await btn.click()
                    await page.wait_for_timeout(3000)
                elif "step2" not in locals():  # STEP 2: dual click logic
                    print("[STEP 2] Waiting 15s for button...")
                    await page.wait_for_timeout(15000)
                    dual_btn = await page.query_selector('button, a')
                    if dual_btn:
                        print("[STEP 2] Dual clicking...")
                        await dual_btn.click()
                        await page.wait_for_timeout(2000)
                        await dual_btn.click()
                    step2 = True
                elif "step3" not in locals():  # STEP 3: wait 10s + continue
                    print("[STEP 3] Waiting 10s for next continue...")
                    await page.wait_for_timeout(10000)
                    cont_btn = await page.query_selector('button:has-text("CONTINUE"), a:has-text("CONTINUE")')
                    if cont_btn:
                        print("[STEP 3] Clicking CONTINUE...")
                        await cont_btn.click()
                    step3 = True
                else:
                    print("[INFO] Trying fallback button search...")
                    any_btn = await page.query_selector('button, a')
                    if any_btn:
                        await any_btn.click()

                # Detect if stuck in same page
                await page.wait_for_timeout(3000)
                new_url = page.url
                if new_url == current_url:
                    print("[WARN] URL did not change, avoiding infinite loop.")
                    break
                current_url = new_url
                step += 1

        except Exception as e:
            print(f"❌ Error: {e}")

        await browser.close()
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        asyncio.run(solve_vplink(url))
    else:
        print("Usage: python3 bot.py <vplink_url>")