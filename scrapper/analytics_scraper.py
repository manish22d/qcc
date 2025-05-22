# analytics_scraper.py

from urllib.parse import unquote

from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver


class AnalyticsScraper:
	def __init__(self, url):
		self.url = url
		self.driver = None
	
	def setup_driver(self):
		chrome_options = Options()
		chrome_options.add_argument('--headless')
		self.driver = webdriver.Chrome(options=chrome_options)
		self.driver.implicitly_wait(10)
	
	def visit_site(self):
		self.driver.get(self.url)
	
	def extract_cat_tags(self):
		cat_tags = []
		
		for req in self.driver.requests:
			if not req.response:
				continue
			url = req.url.lower()
			if "doubleclick.net/activity" in url or "fls.doubleclick.net/activityi" in url:
				if "activityi;" in url:
					tag_part = url.split("activityi;", 1)[-1].split("?", 1)[0]
				elif "activity;" in url:
					tag_part = url.split("activity;", 1)[-1].split("?", 1)[0]
				else:
					continue
				
				for token in tag_part.split(';'):
					if token.startswith("cat="):
						cat_value = unquote(token.split("=", 1)[1])
						cat_tags.append(cat_value)
		
		return cat_tags
	
	def run(self):
		self.setup_driver()
		self.visit_site()
		tags = self.extract_cat_tags()
		self.driver.quit()
		return {
			"url": self.url,
			"activity_tags": tags
		}
