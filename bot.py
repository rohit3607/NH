import time
import cloudscraper
from bs4 import BeautifulSoup

class DDLException(Exception):
    pass

def transcript(url: str, DOMAIN: str, ref: str, sltime: int, proxy: str = None) -> str:
    code = url.rstrip("/").split("/")[-1]
    scraper = cloudscraper.create_scraper()
    if proxy:
        scraper.proxies.update({"http": proxy, "https": proxy})

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Referer': ref
    }

    # Step 1: GET page
    res = scraper.get(f"{DOMAIN}/{code}", headers=headers, timeout=15)
    if "Just a moment" in res.text:
        raise DDLException("❌ Cloudflare protection detected. Try another proxy or wait.")

    # Step 2: Extract form data
    soup = BeautifulSoup(res.text, "html.parser")
    data = {inp['name']: inp['value'] for inp in soup.find_all('input')
            if inp.get('name') and inp.get('value')}

    if not data:
        raise DDLException("❌ No form data found. Page may have changed.")

    # Step 3: Wait to simulate user delay
    time.sleep(sltime)

    # Step 4: POST to get final link
    post_resp = scraper.post(
        f"{DOMAIN}/links/go",
        headers={
            'Referer': f"{DOMAIN}/{code}",
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': headers['User-Agent']
        },
        data=data,
        timeout=15
    )

    try:
        json_data = post_resp.json()
    except Exception:
        raise DDLException("❌ Failed to parse JSON. Response was unexpected.")

    if 'url' in json_data and json_data['url'].strip():
        return json_data['url']
    else:
        raise DDLException(f"❌ Link Extraction Failed. Response JSON: {json_data}")

if __name__ == "__main__":
    try:
        # 📌 Replace with your own working proxy, or set to None to skip proxy
        proxy = "http://156.242.46.69:3129"  # Example public Indian proxy

        direct_link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7,
            proxy=proxy
        )
        print("✅ Final Link:", direct_link)
    except DDLException as e:
        print(str(e))