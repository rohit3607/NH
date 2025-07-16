import asyncio
from playwright.async_api import async_playwright

async def bypass_link(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[STEP 1] Navigating to: {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(15000)  # Wait 15s to let popup finish

        # Step 1: Click "CONTINUE" after waiting
        try:
            btn = await page.wait_for_selector('text=CONTINUE', timeout=5000)
            await btn.click()
            print("[STEP 1] CONTINUE clicked.")
        except Exception:
            print("[WARN] CONTINUE not clickable in step 1.")

        await page.wait_for_load_state('load')
        await page.wait_for_timeout(5000)
        print(f"[STEP 2] Current URL: {page.url}")

        # Step 2: Wait, click DUAL TAP, wait, then click the second version
        try:
            dual_buttons = await page.query_selector_all('text=/DUAL TAP/i')
            if dual_buttons:
                await dual_buttons[0].click()
                print("[STEP 2] First DUAL TAP clicked.")
                await page.wait_for_timeout(10000)  # Wait for second button to appear

                # Find second one
                all_buttons = await page.query_selector_all('text=/DUAL TAP/i')
                if len(all_buttons) >= 2:
                    await all_buttons[-1].click()
                    print("[STEP 2] Second DUAL TAP clicked.")
        except Exception as e:
            print(f"[WARN] Step 2 failed: {e}")

        await page.wait_for_timeout(15000)

        # Step 3: Continue or wait for redirection
        print(f"[STEP 3] Current URL: {page.url}")
        await page.wait_for_timeout(5000)

        # Step 4: Handle final redirection or GET LINK button
        final_url = page.url
        if "vplink.in" in final_url:
            await page.wait_for_timeout(8000)
            try:
                get_link_btn = await page.query_selector('text=/GET LINK/i')
                if get_link_btn:
                    await get_link_btn.scroll_into_view_if_needed()
                    await get_link_btn.wait_for_element_state("visible")
                    await get_link_btn.wait_for_element_state("enabled")
                    await get_link_btn.click()
                    print("[STEP 4] GET LINK clicked.")
                    await page.wait_for_timeout(5000)
                    final_url = page.url
            except Exception:
                print("[WARN] GET LINK button not found.")

        print(f"[SUCCESS] Final Resolved URL: {final_url}")
        await browser.close()
        return final_url

# Run example
if __name__ == "__main__":
    input_url = "https://vplink.in/UNqtJ1lP"
    asyncio.run(bypass_link(input_url))