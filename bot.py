import time
import cloudscraper
from bs4 import BeautifulSoup

class DDLException(Exception):
    pass

def transcript(url: str, DOMAIN: str, ref: str, sltime: int = 7) -> str:
    code = url.rstrip("/").split("/")[-1]
    scraper = cloudscraper.create_scraper()
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                'Chrome/125.0.0.0 Safari/537.36'
    scraper.headers.update({'User-Agent': useragent, 'Referer': ref})

    print("[STEP 1] GET initial page...")
    resp = scraper.get(f"{DOMAIN}/{code}")
    html = resp.text

    if 'Just a moment' in html:
        raise DDLException("❌ Cloudflare protection triggered")

    soup = BeautifulSoup(html, "html.parser")
    data = {inp['name']: inp['value']
            for inp in soup.find_all('input')
            if inp.get('name') and inp.get('value')}

    if not data:
        raise DDLException("❌ Form fields not found; page may have changed")

    print(f"[STEP 2] Waiting {sltime}s to mimic user interaction...")
    time.sleep(sltime)

    print("[STEP 3] Posting to obtain final link...")
    resp2 = scraper.post(
        f"{DOMAIN}/links/go",
        data=data,
        headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': f"{DOMAIN}/{code}"}
    )

    try:
        json_data = resp2.json()
    except Exception:
        raise DDLException(f"❌ JSON parse failed: {resp2.text[:200]}...")

    if 'url' in json_data and json_data['url']:
        return json_data['url']
    raise DDLException(f"❌ Link not found in JSON: {json_data}")

if __name__ == "__main__":
    try:
        link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7
        )
        print("✅ Final Link:", link)
    except DDLException as e:
        print("❌ Error:", e)