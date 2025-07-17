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

        clicked_buttons = set()
        max_steps = 20
        step = 1

        while step <= max_steps:
            print(f"[STEP {step}] Current URL: {page.url}")
            await page.wait_for_timeout(1000)

            # Check if it's the final vplink destination
            if "vplink.in" in page.url and "go" in page.url:
                print("[INFO] Detected final vplink.in 'go' page. Waiting 10s...")
                await page.wait_for_timeout(10000)

                # Attempt to extract href from a button or anchor with link text
                buttons = await page.locator("a, button").all()
                for btn in buttons:
                    try:
                        text = (await btn.inner_text()).strip().upper()
                        if any(key in text for key in ["GET LINK", "GO TO LINK", "CONTINUE"]):
                            href = await btn.get_attribute("href")
                            if href and not href.startswith("javascript"):
                                print(f"[SUCCESS] Final link extracted: {href}")
                                await browser.close()
                                return href
                            else:
                                # fallback: click it if no href
                                await btn.scroll_into_view_if_needed()
                                await btn.click(timeout=10000)
                                await page.wait_for_timeout(3000)
                                print(f"[INFO] Button clicked, URL now: {page.url}")
                                if not page.url.startswith("about:blank"):
                                    print(f"[SUCCESS] Final link: {page.url}")
                                    await browser.close()
                                    return page.url
                    except:
                        continue

                # fallback: just return the current page url
                print(f"[FALLBACK] Returning current page URL: {page.url}")
                await browser.close()
                return page.url

            # Click all unclicked buttons every 10s
            buttons = await page.locator("a, button").all()
            clicked = False
            for btn in buttons:
                try:
                    text = (await btn.inner_text()).strip()
                    if text in clicked_buttons:
                        continue
                    print(f"[INFO] Clicking button: {text}")
                    await btn.scroll_into_view_if_needed()
                    await btn.click(timeout=10000)
                    clicked_buttons.add(text)
                    clicked = True
                    await page.wait_for_timeout(3000)
                    break
                except Exception as e:
                    continue

            if not clicked:
                print("[INFO] No new clickable button found. Waiting 10s...")
                await page.wait_for_timeout(10000)

            step += 1

        print("[ERROR] Max steps exceeded without resolving vplink.")
        await browser.close()
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bypass.py <vplink_url>")
        sys.exit(1)

    link = sys.argv[1]
    final_link = asyncio.run(bypass_vplink(link))
    if final_link:
        print(f"\n✅ Bypassed Link: {final_link}")
    else:
        print("\n❌ Failed to bypass the link.")