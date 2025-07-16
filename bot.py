from aiohttp import ClientSession
from bs4 import BeautifulSoup
from asyncio import sleep as asleep

class DDLException(Exception):
    """Custom exception for direct download link errors."""
    pass

async def vplink(url: str, domain: str = "https://vplink.in/", ref: str = "https://kaomojihub.com/", sltime: int = 5) -> str:
    """
    Async bypass function for vplink.in.
    """
    print(f"[INFO] Starting bypass for: {url}")
    code = url.rstrip("/").split("/")[-1]
    print(f"[DEBUG] Extracted code: {code}")

    useragent = (
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    )

    async with ClientSession() as session:
        print(f"[INFO] Sending initial GET request to {domain}{code}")
        async with session.get(
            f"{domain}{code}",
            headers={'User-Agent': useragent}
        ) as res:
            html = await res.text()
            print(f"[DEBUG] First GET status: {res.status}")

        print(f"[INFO] Sending second GET request with referer")
        async with session.get(
            f"{domain}{code}",
            headers={'Referer': ref, 'User-Agent': useragent}
        ) as res:
            html = await res.text()
            print(f"[DEBUG] Second GET status: {res.status}")

        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find('title')
        if title_tag:
            print(f"[DEBUG] Page Title: {title_tag.text.strip()}")
        else:
            print("[WARN] Title tag not found!")

        if title_tag and title_tag.text.strip() == 'Just a moment...':
            raise DDLException("❌ Cloudflare protection triggered.")

        data = {
            inp.get('name'): inp.get('value')
            for inp in soup.find_all('input')
            if inp.get('name') and inp.get('value')
        }

        print(f"[INFO] Extracted {len(data)} input fields for POST data: {list(data.keys())}")

        print(f"[INFO] Sleeping for {sltime}s before sending POST request...")
        await asleep(sltime)

        print(f"[INFO] Sending POST request to {domain}links/go")
        async with session.post(
            f"{domain}links/go",
            data=data,
            headers={
                'Referer': f"{domain}{code}",
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': useragent
            }
        ) as resp:
            print(f"[DEBUG] POST status: {resp.status}")
            try:
                content_type = resp.headers.get('Content-Type', '')
                print(f"[DEBUG] Response content-type: {content_type}")

                if 'application/json' in content_type:
                    json_resp = await resp.json()
                    print(f"[DEBUG] JSON Response: {json_resp}")

                    if json_resp.get("status") != "success" or not json_resp.get("url"):
                        raise DDLException(f"Server returned error: {json_resp.get('message', 'Unknown error')}")

                    print(f"[SUCCESS] Final URL: {json_resp['url']}")
                    return json_resp["url"]
                else:
                    raise DDLException("Response is not JSON or missing 'url'.")
            except Exception as e:
                raise DDLException(f"❌ Link extraction failed: {e}")

async def unshort(url):
    """
    Main async function to unshorten supported URLs.
    """
    print(f"[INFO] Unshortening: {url}")
    if "vplink.in" in url.lower():
        return await vplink(url)
    else:
        raise DDLException("Unsupported URL!")

# Example standalone test
if __name__ == "__main__":
    import asyncio

    async def main():
        try:
            test_url = "https://vplink.in/HYZr3OLG"  # Change this to your test URL
            print(f"[TEST] Testing URL: {test_url}")
            final_link = await unshort(test_url)
            print(f"\n✅ Final Direct Download Link: {final_link}")
        except DDLException as e:
            print(f"\n❌ Error occurred: {e}")

    asyncio.run(main())