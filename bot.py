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

    scraper = cloudscraper.create_scraper(
        browser={
            'custom': useragent
        },
        delay=10,
        interpreter='nodejs',
    )

    # Step 1: GET initial page
    res = scraper.get(f"{DOMAIN}/{code}", headers={"User-Agent": useragent}, proxies=proxies)
    html = res.text

    # Step 2: GET again with Referer
    res = scraper.get(f"{DOMAIN}/{code}", headers={"Referer": ref, "User-Agent": useragent}, proxies=proxies)
    html = res.text
    cookies = res.cookies

    # Step 3: Check if cloudflare block
    soup = BeautifulSoup(html, "html.parser")
    if soup.find("title") and soup.find("title").text.strip() == "Just a moment...":
        raise DDLException("Cloudflare Protected. Try different proxy.")

    # Step 4: Extract form data
    data = {
        inp.get('name'): inp.get('value') 
        for inp in soup.find_all('input') 
        if inp.get('name') and inp.get('value')
    }

    time.sleep(sltime)

    # Step 5: POST to /links/go
    headers = {
        "Referer": f"{DOMAIN}/{code}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": useragent
    }

    response = scraper.post(
        f"{DOMAIN}/links/go",
        data=data,
        headers=headers,
        cookies=cookies,
        proxies=proxies
    )

    try:
        json_data = response.json()
        if "url" in json_data:
            return json_data["url"]
        else:
            raise DDLException(f"Unexpected response format: {json_data}")
    except Exception as e:
        raise DDLException(f"Link Extraction Failed: {e}")

# Example usage
if __name__ == "__main__":
    try:
        proxy = "http://qbwkdsxg:bb7kcdf9n214@38.154.227.167:5868"  # Optional
        final_link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7,
            proxy=proxy  # Can be None
        )
        print("✅ Final Link:", final_link)
    except DDLException as e:
        print("❌ Error:", e)