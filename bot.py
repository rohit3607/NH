import cloudscraper
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from asyncio import run, sleep

class DDLException(Exception):
    pass

async def transcript(url: str, DOMAIN: str, ref: str, sltime: int) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    
    # Step 1: Use cloudscraper to bypass Cloudflare and get cookies + headers
    scraper = cloudscraper.create_scraper(browser='chrome')
    full_url = f"{DOMAIN}/{code}"
    res = scraper.get(full_url)
    if 'Just a moment' in res.text:
        raise DDLException("Unable To Bypass Due To Cloudflare Protection")
    
    soup = BeautifulSoup(res.text, "html.parser")
    cookies_dict = scraper.cookies.get_dict()
    headers_dict = {
        'User-Agent': useragent,
        'Referer': ref,
        'X-Requested-With': 'XMLHttpRequest'
    }

    data = {
        inp.get('name'): inp.get('value') 
        for inp in soup.find_all('input') 
        if inp.get('name') and inp.get('value')
    }

    await sleep(sltime)

    # Step 2: Use aiohttp for final POST request with cookies and headers from cloudscraper
    async with ClientSession(cookies=cookies_dict, headers=headers_dict) as session:
        async with session.post(f"{DOMAIN}/links/go", data=data) as resp:
            try:
                if 'application/json' in resp.headers.get('Content-Type', ''):
                    return (await resp.json())['url']
                else:
                    raise DDLException("Unexpected Response Content")
            except Exception as e:
                raise DDLException(f"Link Extraction Failed: {str(e)}")

async def main():
    link = await transcript("https://vplink.in/UNqtJ1lP", "https://vplink.in", "https://kaomojihub.com/", 7)
    print(link)

run(main())