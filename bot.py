from aiohttp import ClientSession
from asyncio import run
from bs4 import BeautifulSoup
from asyncio import sleep as asleep

class DDLException(Exception):
    pass

async def transcript(url: str, DOMAIN: str, ref: str, sltime, proxy: str = None) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'

    async with ClientSession() as session:

        async with session.get(
            f"{DOMAIN}/{code}", 
            headers={'User-Agent': useragent},
            proxy=proxy
        ) as res:
            html = await res.text()

        async with session.get(
            f"{DOMAIN}/{code}", 
            headers={'Referer': ref, 'User-Agent': useragent},
            proxy="http://103.172.70.50:8080"  # <-- proxy used here
        ) as res:
            html = await res.text()
            cookies = res.cookies

        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find('title')

        if title_tag and title_tag.text == 'Just a moment...':
            return "Unable To Bypass Due To Cloudflare Protected"
        
        data = {
            inp.get('name'): inp.get('value') 
            for inp in soup.find_all('input') 
            if inp.get('name') and inp.get('value')
        }

        await asleep(sltime)

        async with session.post(
            f"{DOMAIN}/links/go",
            data=data,
            headers={
                'Referer': f"{DOMAIN}/{code}",
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': useragent
            },
            cookies=cookies,
            proxy=proxy  # <-- proxy used here too
        ) as resp:
            try:
                if 'application/json' in resp.headers.get('Content-Type', ''):
                    return (await resp.json())['url']
            except Exception:
                raise DDLException("Link Extraction Failed")

async def main():
    proxy = "http://qbwkdsxg:bb7kcdf9n214@38.154.227.167:5868"
    link = await transcript("https://vplink.in/UNqtJ1lP", "https://vplink.in/", "https://kaomojihub.com/", 7 , proxy = proxy)
    print(link)

run(main())