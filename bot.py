import time
import cloudscraper
from bs4 import BeautifulSoup

class DDLException(Exception):
    pass

def transcript(url: str, DOMAIN: str, ref: str, sltime: int, proxy: str = None) -> str:
    code = url.rstrip("/").split("/")[-1]
    useragent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'

    # Setup proxy dict if provided
    proxies = {"http": proxy, "https": proxy} if proxy else None

    scraper = cloudscraper.create_scraper(
        browser={'custom': useragent},
        delay=10,
    )

    if proxies:
        scraper.proxies = proxies

    # Step 1: Initial GET request to get HTML and cookies
    response = scraper.get(f"{DOMAIN}/{code}", headers={'User-Agent': useragent}, allow_redirects=True)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find('title')

    if title_tag and title_tag.text == 'Just a moment...':
        return "Unable To Bypass Due To Cloudflare Protection"

    # Step 2: Collect hidden form input data
    data = {
        inp.get('name'): inp.get('value') 
        for inp in soup.find_all('input') 
        if inp.get('name') and inp.get('value')
    }

    # Wait for the required time before submitting the form
    time.sleep(sltime)

    # Step 3: POST to /links/go to get final link
    post_headers = {
        'Referer': f"{DOMAIN}/{code}",
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': useragent
    }

    post_url = f"{DOMAIN}/links/go"
    post_resp = scraper.post(post_url, data=data, headers=post_headers)

    try:
        if post_resp.headers.get("Content-Type", "").startswith("application/json"):
            return post_resp.json().get("url")
        else:
            raise DDLException("Unexpected response format")
    except Exception as e:
        raise DDLException(f"Link Extraction Failed: {e}")

# ---------- Usage ----------
if __name__ == "__main__":
    proxy = "http://qbwkdsxg:bb7kcdf9n214@38.154.227.167:5868"  # Optional proxy
    try:
        direct_link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com/",
            sltime=7,
            proxy=proxy
        )
        print("✅ Direct Link:", direct_link)
    except Exception as e:
        print("❌ Error:", str(e))