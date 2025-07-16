import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


async def bypass_shortlink(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logging.info(f"Resolving: {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except PlaywrightTimeoutError:
            raise Exception("Initial page load timeout.")

        logging.info(f"Initial page loaded: {page.url}")

        visited_urls = set()
        max_steps = 5
        final_url = None

        # Try up to 5 button-click-redirect steps
        for _ in range(max_steps):
            found = False
            for button_text in ["Get Link", "Download", "Click here", "Continue", "Generate Link"]:
                try:
                    button = await page.wait_for_selector(f"text={button_text}", timeout=3000)
                    if button:
                        logging.info(f"Looking for button with text: {button_text}")
                        await button.click()
                        await page.wait_for_timeout(3000)  # wait for redirect/load
                        await page.wait_for_load_state("domcontentloaded", timeout=10000)
                        new_url = page.url
                        if new_url not in visited_urls:
                            visited_urls.add(new_url)
                            logging.info(f"Redirected to: {new_url}")
                            if new_url.startswith("http") and new_url != url:
                                final_url = new_url
                        found = True
                        break
                except PlaywrightTimeoutError:
                    continue
                except Exception:
                    continue

            if not found:
                break

        await browser.close()

        if final_url:
            logging.info(f"[SUCCESS] Final Resolved URL: {final_url}")
            return final_url
        else:
            raise Exception("Could not bypass the link successfully.")


async def main():
    url = "https://vplink.in/UNqtJ1lP"  # Replace with any default URL you want
    try:
        final = await bypass_shortlink(url)
        print(f"\n✅  Final Link: {final}")
    except Exception as e:
        print(f"\n❌  Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())