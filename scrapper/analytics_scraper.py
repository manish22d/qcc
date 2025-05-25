import json
import re
import time
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class AnalyticsScraper:
	def __init__(self, url, headless=True, tag_keys=None, url_filters=None):
		self.url = url
		self.headless = headless
		self.driver = self._init_driver(headless)
		self.tag_keys = tag_keys if tag_keys else ['cat']
		self.url_filters = url_filters if url_filters else ['doubleclick.net', 'fls.doubleclick.net']

	def _init_driver(self, headless):
		chrome_options = Options()
		chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
		if headless:
			chrome_options.add_argument('--headless=new')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument('--window-size=1920,1080')
		return webdriver.Chrome(options=chrome_options)

	def _get_network_requests(self):
		logs = self.driver.get_log("performance")
		requests = []
		for entry in logs:
			try:
				message = json.loads(entry["message"])["message"]
				method = message["method"]
				if method == "Network.requestWillBeSent":
					url = message["params"]["request"]["url"]
					requests.append(url)
				elif method == "Network.responseReceived":
					url = message["params"]["response"]["url"]
					requests.append(url)
				elif method == "Network.webSocketFrameSent":
					if "params" in message and "response" in message["params"]:
						url = message["params"]["response"]["url"]
						requests.append(url)
			except Exception:
				continue
		return list(set(requests))
	
	def wait_for_page_load(self, timeout=30):
		try:
			WebDriverWait(self.driver, timeout).until_not(
				EC.presence_of_element_located((By.XPATH, "//div[@class='center' and .//p[text()='Loading...']]"))
			)
			if self.driver.current_url:
				print("✅ Page loaded.")
		except Exception:
			print("⚠️ Warning: Loader may not have disappeared within timeout. Continuing anyway.")
	def _extract_activity_params(self, url):
		print("extracting param from -> ", url)
		if not any(d in url for d in self.url_filters):
			return None
		path_part = url.split('doubleclick.net')[-1].split('fls.doubleclick.net')[-1]
		param_str = ''
		for sep in [';', '?']:
			if sep in path_part:
				param_str = path_part.split(sep, 1)[1]
				break
		if not param_str:
			return None
		param_str = param_str.split('#')[0]
		matched_params = []
		print("param_str", param_str)
		for token in re.split(r'[;&]', param_str):
			if '=' in token:
				key, val = token.split('=', 1)
				if key in self.tag_keys:
					matched_params.append(unquote(val))
		print("returning ->", matched_params)
		return matched_params

	def _wait_for_activities(self, timeout=15):
		start_time = time.time()
		last_count = 0
		stable_count = 0
		collected_urls = []
		while time.time() - start_time < timeout:
			current_urls = self._get_network_requests()
			print("all url-> ")
			print(current_urls)
			for url in current_urls:
				if url not in collected_urls:
					collected_urls.append(url)
			current_activities = [url for url in current_urls if any(f in url for f in self.url_filters)]
			print("filtered url ->")
			print(current_activities)
			if len(current_activities) > last_count:
				last_count = len(current_activities)
				stable_count = 0
			else:
				stable_count += 1
				if stable_count >= 2:
					break
			time.sleep(1)
		return collected_urls

	def run(self):
		try:
			self.driver.get(self.url)
			self.wait_for_page_load()
			phase1_urls = self._wait_for_activities(10)
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
			time.sleep(1)
			phase2_urls = self._wait_for_activities(5)
			all_urls = list(set(phase1_urls + phase2_urls))
			activity_tags = []
			for url in all_urls:
				if any(domain in url for domain in self.url_filters):
					params = self._extract_activity_params(url)
					if params:
						activity_tags.extend(params)
						print("output param", params)
			return {
				"url": self.url,
				"activity_tags": activity_tags,
				"total_requests": len(all_urls),
				"doubleclick_requests": sum(1 for url in all_urls if any(f in url for f in self.url_filters)),
				"sample_urls": [url for url in all_urls if any(f in url for f in self.url_filters)][:5]
			}
		except Exception as e:
			return {
				"url": self.url,
				"activity_tags": [],
				"error": str(e)
			}
		finally:
			self.driver.quit()
