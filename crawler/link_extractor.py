import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkExtractor:
    def __init__(self, base_url):
        self.base_url = base_url

    def _setup_driver(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        return driver

    def wait_for_page_load(self, driver, timeout=30):
        try:
            WebDriverWait(driver, timeout).until_not(
                EC.presence_of_element_located((By.XPATH, "//div[@class='center' and .//p[text()='Loading...']]"))
            )
            if driver.current_url:
                print("✅ Page loaded.")
        except Exception:
            print("⚠️ Warning: Loader may not have disappeared within timeout. Continuing anyway.")

    def scrape_links(self, debug=False):
        """
        Decides whether to use get_all_links_from_class or get_all_links based on presence of `.option` elements.
        Returns links list.
        """
        driver = self._setup_driver(headless=True)
        try:
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            has_options = len(driver.find_elements(By.CSS_SELECTOR, ".option")) > 0
            if debug:
                print(f"🧠 Detected '.option' elements: {has_options}")

        except Exception as e:
            print(f"❌ Error detecting page content: {e}")
            driver.quit()
            return []

        driver.quit()

        if has_options:
            if debug:
                print("🧠 Using get_all_links_from_class()")
            return self.get_all_links_from_class()
        else:
            if debug:
                print("🧠 Using get_all_links()")
            return self.get_all_links()

    def get_all_links(self):
        driver = self._setup_driver(headless=True)
        try:
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            link_elements = driver.find_elements(By.TAG_NAME, "a")
            links = {elem.get_attribute("href") for elem in link_elements if elem.get_attribute("href")}
            return list(links)
        finally:
            driver.quit()

    def get_all_links_from_class(self):
        driver = self._setup_driver(headless=True)
        links = []
        try:
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
            )
            original_url = driver.current_url
            option_elements = driver.find_elements(By.CSS_SELECTOR, ".option")

            for index in range(len(option_elements)):
                try:
                    option_elements = driver.find_elements(By.CSS_SELECTOR, ".option")  # refresh list
                    option = option_elements[index]

                    inner_html = driver.execute_script("return arguments[0].innerHTML;", option)
                    driver.execute_script("arguments[0].click();", option)

                    WebDriverWait(driver, 10).until(lambda d: d.current_url != original_url)
                    new_url = driver.current_url

                    links.append((inner_html.strip(), new_url))
                    print(f"[{index}] Clicked element, navigated to: {new_url}")

                    driver.get(original_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".option"))
                    )
                except Exception as e:
                    print(f"[{index}] Error clicking element: {e}")

            print("\n✅ Unique Navigation Links Found:")
            for link in sorted(set(links)):
                print(link)

            return sorted(set(url for _, url in links))
        finally:
            driver.quit()

    def get_link_record_cat(self):
        from seleniumwire import webdriver as wire_webdriver  # selenium-wire required here
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = wire_webdriver.Chrome(options=options)
        results = []

        try:
            driver.get(self.base_url)
            self.wait_for_page_load(driver)
            original_url = driver.current_url

            option_elements = driver.find_elements(By.CSS_SELECTOR, ".option")

            for index in range(len(option_elements)):
                try:
                    option_elements = driver.find_elements(By.CSS_SELECTOR, ".option")  # refresh list
                    option = option_elements[index]
                    menu_text = option.text.strip()

                    driver.requests.clear()
                    driver.execute_script("arguments[0].click();", option)
                    self.wait_for_page_load(driver)
                    WebDriverWait(driver, 10).until(lambda d: d.current_url != original_url)

                    navigated_url = driver.current_url
                    cat_tags = []

                    for req in driver.requests:
                        if req.url and ("doubleclick.net/activity" in req.url or "fls.doubleclick.net/activityi" in req.url):
                            parsed_url = urlparse(req.url)
                            query = parse_qs(parsed_url.query)
                            if 'cat' in query:
                                cat_tags.extend(query['cat'])

                    results.append({
                        'menu_text': menu_text,
                        'navigated_url': navigated_url,
                        'cat_tags': list(set(cat_tags))
                    })

                    print(f"[{index}] Menu: {menu_text}")
                    print(f"     Navigated to: {navigated_url}")
                    print(f"     CAT Tags: {', '.join(cat_tags) if cat_tags else 'None'}")
                    print("-----------------------------------------------------")

                    driver.get(original_url)
                    self.wait_for_page_load(driver)

                except Exception as e:
                    print(f"[{index}] Error clicking element: {e}")
        finally:
            driver.quit()

        return results
