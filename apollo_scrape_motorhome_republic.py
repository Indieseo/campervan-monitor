"""
Scrape Apollo prices from Motorhome Republic (aggregator site)
"""

import requests
import re

print("\n" + "="*80)
print("APOLLO MOTORHOMES - PRICES FROM MOTORHOME REPUBLIC")
print("="*80 + "\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

url = 'https://www.motorhomerepublic.com/apollo'

try:
    print(f"Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        content = response.text
        
        # Extract all prices
        prices_found = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', content)
        
        print(f"Found {len(prices_found)} price mentions")
        
        # Filter to reasonable daily rates
        daily_rates = []
        for p in prices_found:
            try:
                value = float(p.replace(',', ''))
                if 30 <= value <= 500:
                    daily_rates.append(value)
            except:
                pass
        
        if daily_rates:
            print(f"\n[SUCCESS] APOLLO REAL PRICES FROM MOTORHOME REPUBLIC:")
            print("="*80)
            unique_prices = sorted(set(daily_rates))
            for price in unique_prices:
                print(f"   ${price:.2f}/day")
            
            print(f"\nPRICE STATISTICS:")
            print(f"   Lowest:  ${min(daily_rates):.2f}/day")
            print(f"   Highest: ${max(daily_rates):.2f}/day")
            print(f"   Average: ${sum(daily_rates)/len(daily_rates):.2f}/day")
            print("="*80)
        else:
            print("No daily rates found in expected range")
        
        # Look for specific Apollo vehicle mentions
        print("\nLooking for Apollo vehicle types...")
        apollo_mentions = re.findall(r'.{0,50}apollo.{0,50}', content, re.I)
        for mention in apollo_mentions[:10]:
            text = mention.strip()
            if text and len(text) < 200:
                print(f"   {text}")
        
        # Save HTML for analysis
        with open('data/motorhome_republic_apollo.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\nSaved to: data/motorhome_republic_apollo.html")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")

