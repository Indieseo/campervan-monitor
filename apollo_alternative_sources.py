"""
Try alternative data sources for Apollo prices
- Mobile site
- PDF rate sheets
- Google search results
- Cached pages
"""

import asyncio
import sys
import requests
import json
import re
from datetime import datetime

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def try_direct_requests():
    """Try direct HTTP requests (simpler, might work)"""
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - ALTERNATIVE DATA SOURCES")
    print("="*80 + "\n")
    
    print("[Method 1] Trying direct HTTP requests with browser headers...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Cache-Control': 'max-age=0',
    }
    
    # Try various Apollo URLs
    test_urls = [
        'https://www.apollocamper.com/usa',
        'https://www.apollocamper.com/usa/rv-rental',
        'https://www.apollocamper.com/motorhome-rental',
        'https://booking.apollocamper.com',
    ]
    
    for url in test_urls:
        try:
            print(f"\n   Trying: {url}")
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Check if Cloudflare blocked
                if 'cloudflare' in content.lower() and 'challenge' in content.lower():
                    print("      [BLOCKED] Cloudflare challenge")
                else:
                    print(f"      [OK] Got {len(content)} chars")
                    
                    # Look for prices
                    prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', content)
                    if prices:
                        print(f"      Prices found: {prices[:10]}")
                    
                    # Save for analysis
                    with open(f'data/apollo_direct_{url.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                        print(f"      Saved to: data/apollo_direct_{url.split("/")[-1]}.html")
        except Exception as e:
            print(f"      Error: {str(e)[:50]}")
    
    print("\n[Method 2] Looking for PDF rate sheets...")
    
    pdf_urls = [
        'https://www.apollocamper.com/rates',
        'https://www.apollocamper.com/pricing',
        'https://www.apollocamper.com/pdf/rates.pdf',
        'https://www.apollocamper.com/documents/rates.pdf',
        'https://www.apollocamper.com/usa/rates',
    ]
    
    for url in pdf_urls:
        try:
            response = requests.head(url, headers=headers, timeout=5)
            print(f"      {url}: {response.status_code}")
            if response.status_code == 200:
                print(f"         [FOUND] Content-Type: {response.headers.get('Content-Type')}")
        except:
            pass
    
    print("\n[Method 3] Trying mobile site (often less protected)...")
    
    mobile_headers = headers.copy()
    mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    
    mobile_urls = [
        'https://www.apollocamper.com',
        'https://m.apollocamper.com',
        'https://mobile.apollocamper.com',
    ]
    
    for url in mobile_urls:
        try:
            print(f"\n      Trying: {url}")
            response = requests.get(url, headers=mobile_headers, timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200 and 'cloudflare' not in response.text.lower():
                print(f"      [SUCCESS] Mobile site accessible!")
                prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', response.text)
                if prices:
                    print(f"      Prices: {prices[:15]}")
        except Exception as e:
            print(f"      Error: {str(e)[:30]}")
    
    print("\n[Method 4] Checking booking API directly with cookies...")
    
    # The booking API might work with the right setup
    api_url = "https://booking.apollocamper.com/api/vehicles"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        print(f"      API Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                print(f"      [SUCCESS] API returned data!")
                print(f"      {json.dumps(data, indent=2)[:500]}...")
            except:
                print(f"      Response: {response.text[:200]}")
    except Exception as e:
        print(f"      Error: {e}")
    
    print("\n[Method 5] Looking for Apollo on price comparison sites...")
    
    comparison_sites = [
        'https://www.motorhomerepublic.com/apollo',
        'https://www.compareandtravel.com/apollo',
        'https://www.rvshare.com/apollo',
    ]
    
    for url in comparison_sites:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if 'apollo' in response.text.lower():
                    print(f"      [FOUND] {url}")
                    prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', response.text)
                    if prices:
                        print(f"         Prices: {prices[:10]}")
        except:
            pass
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("If direct methods failed due to Cloudflare, the browser-based")
    print("approach with persistent context is the best option.")
    print("Run: python apollo_cloudflare_bypass.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    try_direct_requests()





