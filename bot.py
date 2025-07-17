import asyncio
from playwright.async_api import async_playwright
import time

async def bypass_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        print(f"[STEP 1] Current URL: {page.url}")
        await asyncio.sleep(15)

        # Click CONTINUE button if found
        try:
            print("[STEP 2] Clicking 'CONTINUE'...")
            await page.click('text="CONTINUE"', timeout=10000)
            await page.wait_for_load_state("load")
        except:
            print("[WARN] CONTINUE button not found")

        await asyncio.sleep(8)
        print(f"[STEP 3] Current URL: {page.url}")

        # Try clicking DUAL TAP multiple times
        try:
            print("[STEP 4] Clicking 'DUAL TAP TO \"GO TO LINK\"' 3 times")
            for _ in range(3):
                await asyncio.sleep(2)
                await page.click('text="DUAL TAP TO \\"GO TO LINK\\""', timeout=8000)
        except:
            print("[WARN] Dual Tap button failed")

        # Now wait for "Get Link" to appear
        print("[STEP 5] Waiting for 'Get Link' button...")
        try:
            await page.wait_for_selector('a:has-text("Get Link")', timeout=20000)
            link_element = await page.query_selector('a:has-text("Get Link")')
            final_url = await link_element.get_attribute("href")
            print(f"[✅ SUCCESS] Final URL: {final_url}")
        except:
            print("[❌ FAILED] Get Link button not found.")
            final_url = None

        await browser.close()
        return final_url


# For testing
if __name__ == "__main__":
    test_url = "https://vplink.in/aUMMULUS"
    final = asyncio.run(bypass_vplink(test_url))
    print(f"\n[FINAL RESULT]: {final}")