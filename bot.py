import asyncio
from playwright.async_api import async_playwright
import sys

async def wait_for_navigation_or_timeout(page, timeout=30):
    try:
        await page.wait_for_navigation(timeout=timeout * 1000)
    except:
        pass  # Ignore timeout, we’ll manually check URL

async def run(link):
    print(f"[INFO] Navigating to: {link}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(link)

        previous_url = ""
        clicked_buttons_step2 = set()

        # --------------------- STEP 1 ---------------------
        for step1_try in range(3):
            current_url = page.url
            print(f"[STEP 1] Current URL: {current_url}")

            if "vplink" not in current_url:
                print("[INFO] URL changed → Proceeding to Step 2")
                break

            print("[STEP 1] Waiting 15s before clicking first CONTINUE...")
            await asyncio.sleep(15)

            buttons = await page.locator("text=CONTINUE").all()
            if not buttons:
                print(f"[WARN] 'CONTINUE' button not found. Retrying in 10s... (Retry {step1_try+1}/3)")
                await asyncio.sleep(10)
                continue

            for btn in buttons:
                try:
                    print("[STEP 1] Clicking button: CONTINUE")
                    await btn.click(timeout=5000)
                    await wait_for_navigation_or_timeout(page)
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"[ERROR] Step 1 click failed: {e}")

        # --------------------- STEP 2 ---------------------
        for step2_try in range(10):
            current_url = page.url
            print(f"[STEP 2] Current URL: {current_url}")

            if current_url != previous_url and "kaomojihub" not in current_url:
                print("[INFO] URL changed → Likely completed.")
                break

            previous_url = current_url
            print("[STEP 2] Waiting 15s before clicking button...")
            await asyncio.sleep(15)

            buttons = await page.locator("button, a").all()

            clicked = False
            for btn in buttons:
                try:
                    text = await btn.inner_text()
                    if text and "GO TO LINK" in text.upper():
                        if text in clicked_buttons_step2:
                            continue
                        print(f"[STEP 2] Clicking button: {text.strip()}")
                        await btn.click(timeout=5000)
                        clicked_buttons_step2.add(text)
                        await wait_for_navigation_or_timeout(page)
                        await asyncio.sleep(2)
                        clicked = True
                        break
                except:
                    continue

            if not clicked:
                print("[STEP 2] No clickable 'GO TO LINK' button found. Retrying...")

        # Final URL
        final_url = page.url
        print(f"[✅ DONE] Final URL: {final_url}")

        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bot.py <url>")
    else:
        asyncio.run(run(sys.argv[1]))