"""Quick test of a single scraper to verify fixes"""
import asyncio
import sys
from scrapers.tier1_scrapers import GoboonyScrap

async def test_single():
    print("\n" + "="*60)
    print("Testing Goboony Scraper with Fixed Timeouts")
    print("="*60 + "\n")
    
    scraper = GoboonyScrap(use_browserless=False)  # Use local browser for reliability
    
    try:
        result = await scraper.scrape()
        
        print(f"\n✅ SUCCESS!")
        print(f"   Company: {result.get('company_name')}")
        print(f"   Price: EUR{result.get('base_nightly_rate')}")
        print(f"   Extraction Method: {result.get('extraction_method', 'N/A')}")
        print(f"   Is Estimated: {result.get('is_estimated')}")
        print(f"   Data Completeness: {result.get('data_completeness_pct')}%")
        print(f"   Review Count: {result.get('review_count')}")
        print(f"   Fleet Size: {result.get('fleet_size_estimate')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_single())
    if result:
        print("\n" + "="*60)
        print("✅ Test Passed - Scraper is working!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ Test Failed")
        print("="*60)
        sys.exit(1)

