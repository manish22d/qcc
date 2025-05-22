# run_scraper.py
import os
import csv
from scrapper.analytics_scraper import AnalyticsScraper
from crawler.link_extractor import LinkExtractor
from concurrent.futures import ThreadPoolExecutor, as_completed


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
                "activity_tags": "; ".join(row["activity_tags"])  # Store cat values as joined string
            })

    print(f"✅ Data saved to {full_path }")

def scrape_url(link):
    try:
        scraper = AnalyticsScraper(link)
        return scraper.run()
    except Exception as e:
        print(f"❌ Error scraping {link}: {e}")
        return {"url": link, "activity_tags": []}


if __name__ == "__main__":
    base_url = "https://www.tayyarijeetki.in/faqs#"

    print(f"🌐 Extracting links from: {base_url}")
    extractor = LinkExtractor(base_url)
    links = extractor.get_all_links()
    print(f"🔗 Found {len(links)} links")
    print(links)

    all_results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:  # You can tune max_workers
        future_to_url = {executor.submit(scrape_url, link): link for link in links}
        
        for i, future in enumerate(as_completed(future_to_url), 1):
            result = future.result()
            print(f"✅ ({i}/{len(links)}) Done: {result['url']}")
            all_results.append(result)
    
    save_to_csv(all_results, "filtered_analytics_data.csv")