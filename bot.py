import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def resolve_final_url(start_url: str, wait_for_button_texts=None, timeout: int = 15000) -> str:
    if wait_for_button_texts is None:
        wait_for_button_texts = ["Get Link", "Download", "Click here", "Continue", "Generate Link"]

    print(f"[INFO] Launching browser to resolve: {start_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(start_url, timeout=timeout)
            print(f"[INFO] Initial page loaded: {page.url}")

            # Wait for any button text
            for button_text in wait_for_button_texts:
                try:
                    print(f"[INFO] Looking for button with text: {button_text}")
                    button = await page.wait_for_selector(f'text="{button_text}"', timeout=3000)
                    if button:
                        print(f"[INFO] Clicking button: {button_text}")
                        await button.click()
                        await page.wait_for_timeout(3000)  # let page load
                except PlaywrightTimeoutError:
                    continue  # try next button

            # Wait for potential navigation/redirect
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Try to get current page's URL
            final_url = page.url
            print(f"[SUCCESS] Final Resolved URL: {final_url}")
            return final_url

        except Exception as e:
            print(f"[ERROR] Failed to extract link: {e}")
            raise

        finally:
            await browser.close()

# For testing
if __name__ == "__main__":
    test_url = "https://vplink.in/UNqtJ1lP"  # Replace with your link
    resolved = asyncio.run(resolve_final_url(test_url))
    print(f"\n✅ Final Link: {resolved}")