import asyncio
from playwright.async_api import async_playwright
import time, sys

async def bypass_vplink(url: str):
    print(f"[INFO] Navigating to: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        step = 1
        first_page = True

        while True:
            print(f"[STEP {step}] Current URL: {page.url}")
            await page.wait_for_timeout(1000)

            if first_page:
                print("[INFO] Waiting 15s before clicking first CONTINUE...")
                await page.wait_for_timeout(15000)
                first_page = False

            retry_count = 0
            max_retries = 3
            clicked = False

            while retry_count < max_retries and not clicked:
                # Collect all button and anchor elements
                elements = await page.locator("button, a").all()

                for element in elements:
                    try:
                        text = (await element.inner_text()).strip().upper()

                        valid_texts = ["CONTINUE", "GET LINK"]
                        # Add step-specific extra buttons
                        if step == 2:
                            valid_texts += ["DUAL TAP TO \"GO TO LINK\"", "CLICK HERE"]

                        if text in valid_texts:
                            print(f"[INFO] Found button: {text}")
                            await element.scroll_into_view_if_needed()
                            await element.click(timeout=10000)
                            clicked = True

                            # Wait based on step or button
                            if text == "GET LINK":
                                await page.wait_for_timeout(3000)
                            elif step == 2 and text.startswith("DUAL TAP"):
                                await page.wait_for_timeout(5000)
                            elif step == 3:
                                await page.wait_for_timeout(5000)
                            elif step == 4:
                                await page.wait_for_timeout(10000)
                            break

                    except Exception:
                        continue

                if not clicked:
                    retry_count += 1
                    print(f"[WARN] Button not clickable or not found. Retrying in 10s... (Retry {retry_count}/{max_retries})")
                    await page.wait_for_timeout(10000)

            if not clicked:
                print("[ERROR] Could not click button after retries. Ending.")
                break

            await page.wait_for_timeout(2000)

            if "vplink.in" in page.url and "go" in page.url:
                print(f"[SUCCESS] Final Link: {page.url}")
                break

            step += 1

        await browser.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    asyncio.run(bypass_vplink(link))