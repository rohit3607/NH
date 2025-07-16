import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DDLException(Exception):
    pass

def transcript(url: str, DOMAIN: str, ref: str, sltime: int = 7) -> str:
    code = url.rstrip("/").split("/")[-1]
    full_url = f"{DOMAIN}/{code}"

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument(f"user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

    try:
        driver = uc.Chrome(options=options)

        # Step 1: Open main page
        driver.get(full_url)
        sleep(2)

        if "Just a moment..." in driver.title:
            raise DDLException("Unable to bypass Cloudflare protection")

        # Step 2: Parse hidden form
        soup = BeautifulSoup(driver.page_source, "html.parser")
        inputs = soup.find_all("input")
        data = {i.get("name"): i.get("value") for i in inputs if i.get("name") and i.get("value")}

        # Step 3: Sleep (wait for required delay)
        sleep(sltime)

        # Step 4: Submit form manually using JS
        js_script = f"""
        fetch('{DOMAIN}/links/go', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': '{full_url}'
            }},
            body: new URLSearchParams({data})
        }}).then(res => res.json()).then(res => {{
            document.body.innerHTML = '<a id="result" href="' + res.url + '">Final Link</a>';
        }}).catch(err => {{
            document.body.innerHTML = '<div id="result">Failed</div>';
        }});
        """
        driver.execute_script(js_script)
        sleep(3)

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "result"))
            )
            result = element.get_attribute("href")
        except:
            raise DDLException("Link Extraction Failed")

        driver.quit()
        return result

    except Exception as e:
        raise DDLException(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        final_link = transcript(
            url="https://vplink.in/UNqtJ1lP",
            DOMAIN="https://vplink.in",
            ref="https://kaomojihub.com",
            sltime=7
        )
        print(f"✅ Final Link: {final_link}")
    except DDLException as e:
        print(str(e))