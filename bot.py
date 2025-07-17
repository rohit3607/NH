import asyncio
import sys
from playwright.async_api import async_playwright

async def main(url):
    print(f"[INFO] Navigating to: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Track clicked buttons to avoid re-clicks
        clicked_buttons = set()

        await page.goto(url)
        step = 1

        while True:
            current_url = page.url
            print(f"[STEP {step}] Current URL: {current_url}")

            # STEP 1: Wait before clicking first CONTINUE
            if step == 1:
                print(f"[STEP 1] Waiting 15s before clicking first CONTINUE...")
                await asyncio.sleep(15)

                retries = 0
                while retries < 3:
                    try:
                        button = await page.query_selector("text=CONTINUE")
                        if button:
                            await button.scroll_into_view_if_needed()
                            await button.click()
                            print(f"[STEP 1] Clicking button: CONTINUE")
                            await page.wait_for_load_state("networkidle", timeout=10000)
                            break
                        else:
                            raise Exception("Button not found")
                    except Exception as e:
                        retries += 1
                        print(f"[WARN] Button not clickable or not found. Retrying in 10s... (Retry {retries}/3)")
                        await asyncio.sleep(10)
                else:
                    print("[ERROR] Failed to click CONTINUE after 3 retries. Exiting.")
                    await browser.close()
                    return

                # Wait for URL change
                for _ in range(10):
                    await asyncio.sleep(2)
                    if page.url != current_url:
                        print("[INFO] URL changed → Proceeding to Step 2")
                        break
                else:
                    print("[WARN] Still on same URL after CONTINUE.")
                    break

                step = 2

            # STEP 2
            elif step == 2:
                print(f"[STEP 2] Waiting 15s before clicking first button...")
                await asyncio.sleep(15)

                buttons = await page.query_selector_all("button, a")
                clicked_any = False

                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).strip()
                        if text and text not in clicked_buttons and "GO TO LINK" in text.upper():
                            clicked_buttons.add(text)
                            print(f"[STEP 2] Clicking first button: {text}")
                            await btn.scroll_into_view_if_needed()
                            await btn.click()
                            await page.wait_for_timeout(3000)
                            clicked_any = True
                            break
                    except Exception:
                        continue

                if page.url != current_url:
                    print("[INFO] URL changed → Final redirect reached")
                    break
                elif not clicked_any:
                    print("[WARN] No unclicked button found. Retrying...")
                    await asyncio.sleep(5)
                else:
                    print("[STEP 2] Still on same URL. Staying in Step 2")

        print(f"[SUCCESS] Final URL: {page.url}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bot.py <url>")
    else:
        asyncio.run(main(sys.argv[1]))