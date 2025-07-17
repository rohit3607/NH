import asyncio
from playwright.async_api import async_playwright


async def handle_step_1(page):
    print("[STEP 1] Waiting 20s...")
    await page.wait_for_timeout(20000)

    button = await page.query_selector("button, a")
    if button:
        print("[STEP 1] Clicking first button")
        await button.click()
        await page.wait_for_timeout(5000)
    else:
        print("[STEP 1] No button found")

    print(f"[STEP 1] URL: {page.url}")
    return page.url


async def handle_step_2(page):
    print("[STEP 2] Started Step 2")
    max_retries = 3

    for attempt in range(max_retries):
        print(f"[STEP 2] Attempt {attempt + 1}/{max_retries}")
        current_url = page.url
        await page.wait_for_timeout(15000)  # wait 15s

        # First button
        first_button = await page.query_selector("button, a")
        if first_button:
            print("[STEP 2] Clicking first button")
            await first_button.click()
            await page.wait_for_timeout(4000)

            # Scroll & wait for second button
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

            all_buttons = await page.query_selector_all("button, a")
            for btn in all_buttons:
                try:
                    text = (await btn.inner_text()).lower()
                    if any(x in text for x in ["continue", "final", "go to", "visit", "get link"]):
                        print(f"[STEP 2] Clicking second button: {text.strip()}")
                        await btn.click()
                        await page.wait_for_timeout(5000)
                        break
                except:
                    continue

        if page.url != current_url:
            print(f"[STEP 2] Redirected to: {page.url}")
            return page.url

        print("[STEP 2] Still on same page. Retrying...")

    raise Exception("[STEP 2] Failed after 3 retries")


async def handle_step_3(page):
    print("[STEP 3] Waiting 15s before interaction...")
    await page.wait_for_timeout(15000)

    # Try clicking a visible button
    buttons = await page.query_selector_all("button, a")
    clicked = False
    for btn in buttons:
        try:
            text = (await btn.inner_text()).lower()
            if any(x in text for x in ["continue", "get link", "go", "final"]):
                print(f"[STEP 3] Clicking button: {text.strip()}")
                await btn.click()
                clicked = True
                break
        except:
            continue

    # If not clicked, wait for redirect
    if not clicked:
        print("[STEP 3] No clickable button. Waiting for redirect...")
        await page.wait_for_timeout(10000)

    # Final wait after landing
    await page.wait_for_timeout(10000)
    final_url = page.url
    print(f"[STEP 3] Landed on: {final_url}")

    if "vplink" in final_url:
        print("[STEP 3] vplink detected. Looking for final link...")
        anchors = await page.query_selector_all("a")
        for a in anchors:
            try:
                text = (await a.inner_text()).lower()
                href = await a.get_attribute("href")
                if "get" in text and href and href.startswith("http"):
                    print(f"[STEP 3] Found final URL: {href}")
                    return href
            except:
                continue

    print(f"[STEP 3] Returning current URL: {final_url}")
    return final_url


async def bypass(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        print(f"[STEP 0] Opened: {url}")

        try:
            await handle_step_1(page)
            await handle_step_2(page)
            final = await handle_step_3(page)
        except Exception as e:
            await browser.close()
            raise e

        await browser.close()
        return final


# Example usage
if __name__ == "__main__":
    test_url = "https://vplink.in/aUMMULUS"  # Replace with actual shortlink
    final_link = asyncio.run(bypass(test_url))
    print(f"\n✅ Final Download Link: {final_link}")