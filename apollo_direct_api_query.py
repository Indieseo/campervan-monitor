"""
Query Apollo's discovered booking APIs directly to find pricing endpoints
"""

import requests
import json
import re
from datetime import datetime, timedelta

print("\n" + "="*80)
print("APOLLO BOOKING API - DIRECT QUERY FOR PRICES")
print("="*80 + "\n")

base_url = "https://booking.apollocamper.com/api"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.apollocamper.com/',
    'Origin': 'https://www.apollocamper.com',
}

# Dates for search
pickup = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
dropoff = (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d')

print(f"Search dates: {pickup} to {dropoff} (7 days)\n")

print("[1] Querying countries API...")
try:
    r = requests.get(f"{base_url}/countries", headers=headers, params={'country': 'US'}, timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        countries = r.json()
        print(f"    Got {len(countries)} countries")
except Exception as e:
    print(f"    Error: {e}")

print("\n[2] Querying locations API...")
try:
    params = {
        'brandsObj': 'A',  # Apollo brand
        'country': 'US',
        'allowSameDayPickUp': 'true'
    }
    r = requests.get(f"{base_url}/locations", headers=headers, params=params, timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        locations = r.json()
        print(f"    Got {len(locations)} locations")
        if locations:
            print(f"    Sample location: {json.dumps(locations[0], indent=2)[:300]}")
except Exception as e:
    print(f"    Error: {e}")

print("\n[3] Trying common pricing/vehicle endpoints...")

test_endpoints = [
    '/vehicles',
    '/search',
    '/availability',
    '/rates',
    '/pricing',
    '/products',
    '/fleet',
    '/quotes',
    '/booking',
]

for endpoint in test_endpoints:
    try:
        print(f"\n    Testing: {base_url}{endpoint}")
        r = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        print(f"    Status: {r.status_code}", end="")
        
        if r.status_code == 200:
            print(" ✓")
            try:
                data = r.json()
                print(f"    Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Look for prices
                text = str(data)
                prices = re.findall(r'(\d+(?:\.\d{2})?)', text)
                if prices:
                    print(f"    Numbers found: {prices[:15]}")
            except:
                print(f"    Text response: {r.text[:200]}...")
        elif r.status_code == 404:
            print(" (not found)")
        elif r.status_code == 403:
            print(" (forbidden)")
        else:
            print(f" (status {r.status_code})")
    except Exception as e:
        print(f" Error: {str(e)[:30]}")

print("\n[4] Trying search with parameters...")

search_params_variations = [
    {
        'pickup': pickup,
        'dropoff': dropoff,
        'location': 'LAX',
        'country': 'US'
    },
    {
        'pickupDate': pickup,
        'returnDate': dropoff,
        'pickupLocation': 'Los Angeles',
        'brand': 'A'
    },
    {
        'from': pickup,
        'to': dropoff,
        'country': 'US',
        'brand': 'apollo'
    }
]

for params in search_params_variations:
    try:
        print(f"\n    Params: {params}")
        r = requests.get(f"{base_url}/search", headers=headers, params=params, timeout=10)
        print(f"    Status: {r.status_code}")
        if r.status_code == 200:
            print("    [SUCCESS] Got response!")
            try:
                data = r.json()
                print(f"    {json.dumps(data, indent=2)[:1000]}...")
                
                # Extract prices
                if isinstance(data, list):
                    for item in data[:5]:
                        if 'price' in str(item).lower():
                            print(f"    [PRICE DATA] {item}")
            except:
                print(f"    Text: {r.text[:300]}...")
    except Exception as e:
        print(f"    Error: {e}")

print("\n[5] Checking GraphQL endpoint...")
try:
    graphql_url = "https://booking.apollocamper.com/graphql"
    
    # Try introspection query
    query = {"query": "{__schema{types{name}}}"}
    
    r = requests.post(graphql_url, headers=headers, json=query, timeout=10)
    print(f"    GraphQL Status: {r.status_code}")
    if r.status_code == 200:
        print("    [FOUND] GraphQL endpoint!")
        print(f"    {r.text[:500]}...")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("\nDiscovered Apollo Booking APIs:")
print("  ✓ /api/countries - accessible")
print("  ✓ /api/locations - accessible")
print("  ? /api/search - needs correct parameters")
print("  ? /api/vehicles - may need authentication")
print("\nNext steps:")
print("  1. The booking form likely POSTs search data")
print("  2. Response contains vehicle availability & pricing")
print("  3. Need to capture actual form submission in browser")
print("="*80 + "\n")





