import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from time import sleep
import logging

logging.basicConfig(level=logging.INFO)

class DDLException(Exception):
    pass

def transcript_with_chrome(url: str, DOMAIN: str, ref: str, sltime: int = 7) -> str:
    code = url.rstrip("/").split("/")[-1]
    full_url = f"{DOMAIN}/{code}"
    logging.info(f"[1] Loading: {full_url}")

    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = uc.Chrome(options=options, use_subprocess=True)
    
    try:
        driver.get(full_url)
        sleep(3)
        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        if soup.title and 'Just a moment' in soup.title.text:
            raise DDLException("❌ Cloudflare challenge still present.")

        form = soup.find("form")
        if not form:
            raise DDLException("❌ Form not found on page")

        data = {}
        for inp in form.find_all("input"):
            if inp.get("name") and inp.get("value"):
                data[inp["name"]] = inp["value"]

        logging.info(f"[2] Extracted form data: {data}")
        sleep(sltime)

        driver.execute_script("""
            document.querySelector('form').submit();
        """)
        sleep(3)

        final_html = driver.page_source
        soup = BeautifulSoup(final_html, "html.parser")
        a_tag = soup.find("a", string="Click here to download")

        if a_tag and a_tag.get("href"):
            logging.info("✅ Final link extracted successfully.")
            return a_tag["href"]
        else:
            raise DDLException("❌ Failed to find final download link")

    finally:
        driver.quit()

# Run it like normal
if __name__ == "__main__":
    try:
        link = transcript_with_chrome(
            "https://vplink.in/UNqtJ1lP",
            "https://vplink.in",
            "https://kaomojihub.com",
            sltime=7
        )
        print(f"✅ Final Link:\n{link}")
    except DDLException as e:
        print(f"❌ Error: {e}")