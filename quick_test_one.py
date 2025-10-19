from scrapers.universal_botasaurus_scraper import scrape_competitor

print("Testing Roadsurfer...")
result = scrape_competitor('Roadsurfer')

if result:
    print(f"\nSUCCESS!")
    print(f"Company: {result['company_name']}")
    print(f"Price: {result['currency']}{result['base_nightly_rate']}/night")
    print(f"Completeness: {result['data_completeness_pct']}%")




