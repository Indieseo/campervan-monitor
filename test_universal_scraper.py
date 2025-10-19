"""
Test Universal Botasaurus Scraper on a few competitors
"""

from scrapers.universal_botasaurus_scraper import scrape_competitor

# Test on 3 competitors first
test_competitors = ['Roadsurfer', 'McRent', 'Goboony']

print("\n" + "="*80)
print("TESTING UNIVERSAL BOTASAURUS SCRAPER")
print("Testing on 3 competitors first")
print("="*80 + "\n")

results = []
for company in test_competitors:
    print(f"\n{'='*80}")
    print(f"Testing: {company}")
    print(f"{'='*80}\n")
    
    result = scrape_competitor(company)
    if result:
        results.append(result)
        print(f"\n✅ SUCCESS: {company}")
        print(f"   Price: {result['currency']}{result['base_nightly_rate']}/night")
        print(f"   Completeness: {result['data_completeness_pct']}%")
        print(f"   Estimated: {'Yes' if result.get('is_estimated') else 'No'}")

print("\n" + "="*80)
print(f"TEST COMPLETE: {len(results)}/{len(test_competitors)} succeeded")
print("="*80)

if len(results) == len(test_competitors):
    print("\n✅ All tests passed! Ready to run on all 8 competitors.")
    print("Run: python scrapers/universal_botasaurus_scraper.py")
else:
    print("\n⚠️ Some tests failed. Check logs above.")




