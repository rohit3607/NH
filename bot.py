import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time


async def test_proxy(proxy_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://httpbin.org/ip", proxy=proxy_url, timeout=10) as resp:
                data = await resp.json()
                print(f"[SUCCESS] Proxy works: {data}")
                return True
    except Exception as e:
        print(f"[ERROR] Proxy failed: {proxy_url} | {e}")
        return False


async def transcript(url: str, DOMAIN: str, ref: str, sltime: int = 7, proxy: str = None) -> str:
    try:
        async with aiohttp.ClientSession(headers={
            "referer": ref,
            "origin": DOMAIN,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }) as session:
            # Step 1
            async with session.get(url, proxy=proxy, timeout=10) as r:
                html = await r.text()
                soup = BeautifulSoup(html, "html.parser")
                _token = soup.find("input", {"name": "_token"})["value"]
                alias = soup.find("input", {"name": "alias"})["value"]

            # Step 2
            await asyncio.sleep(sltime)
            async with session.post(
                DOMAIN + "/links/go",
                data={"_token": _token, "alias": alias},
                headers={"x-requested-with": "XMLHttpRequest"},
                proxy=proxy,
                timeout=10
            ) as r:
                res_json = await r.json()
                return res_json.get("url", "❌ Final URL not found!")

    except Exception as e:
        return f"[❌ ERROR] {e}"


async def main():
    proxies = [
        "http://103.47.93.248:8080",
        "http://103.172.70.50:8080",
        "http://103.169.70.50:8080",
        "http://103.148.33.234:8080",
        # Add more proxies here
    ]

    working_proxy = None
    for proxy in proxies:
        print(f"🔍 Testing proxy: {proxy}")
        if await test_proxy(proxy):
            working_proxy = proxy
            break

    if working_proxy:
        print(f"✅ Using working proxy: {working_proxy}")
    else:
        print("⚠️ No working proxies found. Trying without proxy.")
        working_proxy = None

    final_link = await transcript(
        url="https://vplink.in/UNqtJ1lP",
        DOMAIN="https://vplink.in/",
        ref="https://kaomojihub.com/",
        sltime=7,
        proxy=working_proxy
    )

    print(f"\n🎯 Final Bypassed Link: {final_link}")


if __name__ == "__main__":
    asyncio.run(main())