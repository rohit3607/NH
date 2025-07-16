import asyncio
from playwright.async_api import async_playwright
import time

START_URL = "https://vplink.in/aUMMULUS"  # Change this URL as needed

BUTTON_TEXTS = [
    "Get Link",
    "Download",
    "Click here",
    "Continue",
    "Generate Link"
]

async def solve_vplink(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[INFO] Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")

        step = 0
        final_url = None

        while True:
            step += 1
            print(f"[STEP {step}] Current URL: {page.url}")

            # Wait if there's a delay before showing the button
            await page.wait_for_timeout(1000)

            found = False
            for btn_text in BUTTON_TEXTS:
                try:
                    btn = await page.query_selector(f'text="{btn_text}"')
                    if btn:
                        print(f"[INFO] Found button: {btn_text}")
                        if btn_text.lower() == "get link":
                            print("[INFO] Waiting 5 seconds before clicking final Get Link...")
                            await page.wait_for_timeout(5000)
                            href = await btn.get_attribute("href")
                            if href:
                                final_url = href
                                print(f"[SUCCESS] Final Resolved URL: {final_url}")
                                break
                        else:
                            await btn.click()
                            await page.wait_for_load_state("domcontentloaded")
                            found = True
                            break
                except Exception as e:
                    continue

            if final_url:
                break

            if not found:
                print("[WARN] No clickable buttons found on this step. Ending.")
                break

        await browser.close()

        if final_url:
            print(f"✅  Final Link: {final_url}")
        else:
            print("❌  Failed to resolve final link.")

if __name__ == "__main__":
    asyncio.run(solve_vplink(START_URL))