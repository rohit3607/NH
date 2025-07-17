import asyncio
from playwright.async_api import async_playwright

async def scroll_and_click(button):
    await button.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
    await asyncio.sleep(1.5)  # give time to scroll
    await button.click()

async def handle_step_1(page):
    print("[STEP 1] Clicking first 'CONTINUE' button...")
    button = await page.wait_for_selector("text=CONTINUE", timeout=15000)
    await scroll_and_click(button)
    await asyncio.sleep(3)

async def handle_step_2(page):
    print("[STEP 2] Waiting for second button...")
    await asyncio.sleep(5)  # let the second button load
    buttons = await page.query_selector_all("button")
    if len(buttons) < 2:
        raise Exception("Not enough buttons found for Step 2")

    print("[STEP 2] Clicking second button...")
    await scroll_and_click(buttons[1])
    await asyncio.sleep(3)

async def handle_step_3(page):
    print("[STEP 3] Waiting for final redirect or button...")
    await asyncio.sleep(15)

    try:
        final_button = await page.wait_for_selector("button", timeout=10000)
        print("[STEP 3] Final button found, clicking...")
        await scroll_and_click(final_button)
    except:
        print("[STEP 3] No final button found. Waiting for redirect...")
        await asyncio.sleep(10)

    current_url = page.url
    print(f"[INFO] Redirected to: {current_url}")

    if "vplink" in current_url:
        print("[INFO] Found vplink in URL. Extracting final link button...")
        get_link_btn = await page.query_selector("a[href*='vplink']")
        final_url = await get_link_btn.get_attribute("href")
        print(f"[SUCCESS] Final URL: {final_url}")
        return final_url
    else:
        raise Exception("Redirected URL does not contain 'vplink'")

async def bypass(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        try:
            await handle_step_1(page)
            await handle_step_2(page)
            final_link = await handle_step_3(page)
            return final_link
        except Exception as e:
            raise e
        finally:
            await browser.close()


# Example usage
if __name__ == "__main__":
    test_url = "https://vplink.in/aUMMULUS"  # Replace with actual shortlink
    final_link = asyncio.run(bypass(test_url))
    print(f"\n✅ Final Download Link: {final_link}")