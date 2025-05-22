from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class LinkExtractor:
	def __init__(self, base_url):
		self.base_url = base_url
	
	def get_all_links(self):
		chrome_options = Options()
		# chrome_options.add_argument('--headless')
		driver = webdriver.Chrome(options=chrome_options)
		driver.implicitly_wait(10)
		driver.get(self.base_url)
		
		link_elements = driver.find_elements(By.TAG_NAME, "a")
		links = [elem.get_attribute("href") for elem in link_elements if elem.get_attribute("href")]
		
		driver.quit()
		return list(set(links))  # remove duplicates
	
	def get_all_links_stubbed(self):
		links = ["https://www.coke2home.com/toofanibiryanihunt/",
		         "https://www.coke2home.com/toofanibiryanihunt/vote",
		         "https://www.coke2home.com/toofanibiryanihunt/auth",
		         "https://www.coke2home.com/toofanibiryanihunt/dashboard",
		         "https://www.coke2home.com/toofanibiryanihunt/play",
		         "https://www.coke2home.com/toofanibiryanihunt/hte",
		         "https://www.coke2home.com/toofanibiryanihunt/faqs",
		         "https://www.coke2home.com/toofanibiryanihunt/outlets"]
		return list(set(links))
