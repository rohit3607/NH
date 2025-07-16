import time
import cloudscraper
from bs4 import BeautifulSoup


class DDLException(Exception):
    pass


def transcript(url: str, DOMAIN: str, ref: str, sltime: int, proxy: str = None) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'

    proxies = {
        "http": proxy,
        "https": proxy
    } if proxy else None

    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        "User-Agent": useragent
    })

    try:
        # Step 1: GET page
        res1 = scraper.get(f"{DOMAIN}/{code}", headers={"Referer": ref}, proxies=proxies)
        soup = BeautifulSoup(res1.text, "html.parser")

        if soup.title and soup.title.string == "Just a moment...":
            raise DDLException("Cloudflare protection active. Try again later or use a better proxy.")

        data = {
            inp.get('name'): inp.get('value')
            for inp in soup.find_all('input')
            if inp.get('name') and inp.get('value')
        }

        time.sleep(sltime)

        # Step 2: POST to /links/go
        res2 = scraper.post(
            f"{DOMAIN}/links/go",
            headers={
                "Referer": f"{DOMAIN}/{code}",
                "X-Requested-With": "XMLHttpRequest"
            },
            data=data,
            proxies=proxies
        )

        if res2.headers.get("Content-Type", "").startswith("application/json"):
            json_data = res2.json()
            final_url = json_data.get("url")
            if final_url:
                return final_url
            else:
                raise DDLException("Link Extraction Failed: No 'url' in response")
        else:
            raise DDLException("Link Extraction Failed: Unexpected response format")

    except Exception as e:
        raise DDLException(str(e))


if __name__ == "__main__":
    try:
        # You can leave proxy=None to try without proxy
        proxy = None
        # proxy = "http://user:pass@host:port"
        final = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7,
            proxy=proxy
        )
        print("✅ Final Link:", final)

    except DDLException as e:
        print("❌ Error:", e)