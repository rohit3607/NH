import cloudscraper
from bs4 import BeautifulSoup
import time

class DDLException(Exception):
    pass

def transcript(url: str, DOMAIN: str, ref: str, sltime: int) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'android', 'mobile': True}
    )

    headers = {
        'User-Agent': useragent,
        'Referer': ref,
    }

    # Step 1: Initial GET
    res = scraper.get(f"{DOMAIN}/{code}", headers=headers)
    html = res.text

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")

    if title_tag and "Just a moment" in title_tag.text:
        raise DDLException("Unable to bypass due to Cloudflare")

    # Step 2: Extract form data
    data = {
        inp.get('name'): inp.get('value')
        for inp in soup.find_all('input')
        if inp.get('name') and inp.get('value')
    }

    if not data:
        raise DDLException("No form data found in page.")

    # Step 3: Wait before POST
    time.sleep(sltime)

    # Step 4: POST to /links/go
    post_headers = {
        'User-Agent': useragent,
        'Referer': f"{DOMAIN}/{code}",
        'X-Requested-With': 'XMLHttpRequest',
    }

    resp = scraper.post(f"{DOMAIN}/links/go", data=data, headers=post_headers)

    try:
        json_data = resp.json()
        if 'url' not in json_data:
            raise DDLException(f"No 'url' in response: {json_data}")
        return json_data['url']
    except Exception as e:
        raise DDLException(f"Link Extraction Failed: {e}")

# Example usage
if __name__ == "__main__":
    try:
        final_link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7
        )
        print("✅ Final Link:", final_link)
    except DDLException as e:
        print(f"❌  Error: {e}")