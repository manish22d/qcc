# run_scraper.py
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from crawler.link_extractor import LinkExtractor
from scrapper.analytics_scraper import AnalyticsScraper

app = Flask(__name__)


def save_to_csv(data, filename):
	# Create "report" folder if it doesn't exist
	os.makedirs("report", exist_ok=True)
	full_path = os.path.join("report", filename)
	
	with open(full_path, mode='w', newline='', encoding='utf-8') as file:
		writer = csv.DictWriter(file, fieldnames=["url", "activity_tags"])
		writer.writeheader()
		for row in data:
			writer.writerow({
				"url": row["url"],
				"activity_tags": row["activity_tags"]
			})
	
	print(f"✅ Data saved to {full_path}")


def scrape_url(link):
	try:
		scraper = AnalyticsScraper(link)
		return scraper.run()
	except Exception as e:
		print(f"❌ Error scraping {link}: {e}")
		return {"url": link, "activity_tags": []}


@app.route('/generate_tags', methods=['POST'])
def generate_tags():
	data = request.get_json()
	base_url = data.get('base_url')

	if not base_url:
		return jsonify({"error": "Missing 'base_url' in request body"}), 400

	print(f"🌐 Extracting links from: {base_url}")
	extractor = LinkExtractor(base_url)
	links = extractor.scrape_links()
	print(f"🔗 Found {len(links)} links")
	print(links)
	
	all_results = []
	
	with ThreadPoolExecutor(max_workers=5) as executor:
		future_to_url = {executor.submit(scrape_url, link): link for link in links}
		
		for i, future in enumerate(as_completed(future_to_url), 1):
			result = future.result()
			print(f"✅ ({i}/{len(links)}) Done: {result['url']}")
			all_results.append(result)
	
	# Optionally save to CSV
	save_to_csv(all_results, "filtered_analytics_data.csv")
	return jsonify(all_results)


if __name__ == "__main__":
	app.run(debug=True)
