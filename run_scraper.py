# run_scraper.py
import os
import csv
from scrapper.analytics_scraper import AnalyticsScraper
from crawler.link_extractor import LinkExtractor


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


if __name__ == "__main__":
    base_url = "https://www.coke2home.com/toofanibiryanihunt/"

    print(f"🌐 Extracting links from: {base_url}")
    extractor = LinkExtractor(base_url)
    links = extractor.get_all_links()
    print(f"🔗 Found {len(links)} links")

    all_results = []

    for i, link in enumerate(links, 1):
        print(f"\n➡️ ({i}/{len(links)}) Scraping: {link}")
        try:
            scraper = AnalyticsScraper(link)
            result = scraper.run()
            all_results.append(result)
        except Exception as e:
            print(f"❌ Error scraping {link}: {e}")
            all_results.append({
                "url": link,
                "activity_tags": []
            })

    save_to_csv(all_results, "filtered_analytics_data.csv")
