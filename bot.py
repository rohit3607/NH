import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import logging

logging.basicConfig(level=logging.INFO)
TARGET_BUTTONS = [
    "Get Link", "Download", "Click here", "Continue", "Generate Link"
]

async def bypass_link(url: str, wait_time: int = 7) -> str:
    logging.info(f"[INFO] Starting to bypass: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, timeout=60000)
            logging.info(f"[INFO] Initial page loaded: {page.url}")

            # Wait for the redirect chain to start
            await asyncio.sleep(wait_time)

            # Click through all intermediate steps
            for button_text in TARGET_BUTTONS:
                try:
                    logging.info(f"[INFO] Looking for button with text: {button_text}")
                    btn = await page.wait_for_selector(f"text={button_text}", timeout=5000)
                    if btn:
                        await btn.click()
                        logging.info(f"[INFO] Clicked: {button_text}")
                        await asyncio.sleep(3)
                except PlaywrightTimeoutError:
                    logging.warning(f"[WARN] Button not found: {button_text}")
                    continue

            await asyncio.sleep(4)

            final_url = page.url
            logging.info(f"[SUCCESS] Final Resolved URL: {final_url}")
            return final_url

        except Exception as e:
            raise Exception(f"Bypass Failed: {str(e)}")
        finally:
            await browser.close()

# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python bypass.py <shortlink>")
    else:
        final_link = asyncio.run(bypass_link(sys.argv[1]))
        print(f"\n✅  Final Link: {final_link}")