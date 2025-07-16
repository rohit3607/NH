from aiohttp import ClientSession, ClientTimeout
from asyncio import run, sleep as asleep
from bs4 import BeautifulSoup

class DDLException(Exception):
    pass

async def transcript(url: str, DOMAIN: str, ref: str, sltime: int) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/125.0.0.0 Safari/537.36'
    )
    
    headers = {
        'User-Agent': useragent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }

    timeout = ClientTimeout(total=20)

    async with ClientSession(timeout=timeout) as session:
        # Step 1: GET the page
        try:
            async with session.get(f"{DOMAIN}/{code}", headers=headers) as res:
                html = await res.text()
        except Exception as e:
            raise DDLException(f"Initial GET failed: {e}")

        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find('title')

        if title_tag and 'Just a moment' in title_tag.text:
            raise DDLException("Cloudflare protection detected")

        # Extract form data
        data = {
            inp.get('name'): inp.get('value') 
            for inp in soup.find_all('input') 
            if inp.get('name') and inp.get('value')
        }

        cookies = res.cookies

        # Step 2: Wait for required time
        await asleep(sltime)

        # Step 3: POST to extract the final URL
        try:
            async with session.post(
                f"{DOMAIN}/links/go",
                data=data,
                headers={
                    'Referer': f"{DOMAIN}/{code}",
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': useragent
                },
                cookies=cookies
            ) as resp:
                if 'application/json' in resp.headers.get('Content-Type', ''):
                    json_data = await resp.json()
                    if 'url' in json_data:
                        return json_data['url']
                    else:
                        raise DDLException("No URL found in response")
                else:
                    text = await resp.text()
                    raise DDLException(f"Unexpected Response Content: {text[:100]}")
        except Exception as e:
            raise DDLException(f"Link Extraction Failed: {str(e)}")

# Run the function
async def main():
    try:
        link = await transcript(
            "https://vplink.in/UNqtJ1lP",
            "https://vplink.in",
            "https://kaomojihub.com/",
            7
        )
        print("Bypassed Link:", link)
    except DDLException as e:
        print("❌ Error:", e)

run(main())