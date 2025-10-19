"""Inspect McRent API responses to understand price format"""
import asyncio
import json
from scrapers.tier1_scrapers import McRentScraper

async def inspect_api():
    print("\nInspecting McRent API responses...")
    print("="*60)
    
    scraper = McRentScraper(use_browserless=False)
    result = await scraper.scrape()
    
    print(f"\nAPIs Detected: {len(scraper.pricing_endpoints)}")
    print(f"Responses Captured: {len(scraper.api_responses)}")
    
    if scraper.pricing_endpoints:
        print("\nPricing Endpoints:")
        for i, endpoint in enumerate(scraper.pricing_endpoints[:5], 1):
            print(f"  {i}. {endpoint['url']}")
    
    if scraper.api_responses:
        print("\nAPI Responses:")
        for i, resp in enumerate(scraper.api_responses, 1):
            print(f"\n--- Response {i} ---")
            print(f"URL: {resp['url']}")
            print(f"Status: {resp['status']}")
            print(f"Data type: {type(resp['data'])}")
            
            # Print data structure
            if isinstance(resp['data'], dict):
                print(f"Keys: {list(resp['data'].keys())}")
                
                # Print first few entries
                for key, value in list(resp['data'].items())[:3]:
                    print(f"  {key}: {str(value)[:100]}...")
                
                # Save full response for analysis
                filename = f"mcrent_api_response_{i}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(resp['data'], f, indent=2)
                print(f"Full response saved to: {filename}")
            
            elif isinstance(resp['data'], list):
                print(f"List with {len(resp['data'])} items")
                if resp['data']:
                    print(f"First item: {str(resp['data'][0])[:200]}...")
    
    print(f"\n{('='*60)}\n")

if __name__ == "__main__":
    asyncio.run(inspect_api())







