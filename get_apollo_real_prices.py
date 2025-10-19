"""
Get REAL live prices from Apollo Motorhomes
Navigate to search page and extract actual vehicle prices
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from loguru import logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def get_apollo_real_prices():
    """
    Get real live prices from Apollo Motorhomes
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - REAL LIVE PRICE EXTRACTION")
    print("="*80 + "\n")
    
    # Setup search parameters
    pickup_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d')  # 7-day rental
    
    print(f"Search Parameters:")
    print(f"  Pickup:  {pickup_date}")
    print(f"  Dropoff: {dropoff_date}")
    print(f"  Duration: 7 days")
    print()
    
    async with async_playwright() as p:
        print("[1/5] Launching browser...")
        
        # Launch non-headless for Cloudflare bypass
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--no-sandbox',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )
        
        page = await context.new_page()
        
        # Inject anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}};
        """)
        
        print("[2/5] Navigating to Apollo Motorhomes...")
        
        try:
            # Go to main site
            await page.goto('https://www.apollocamper.com/', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # Check for Cloudflare
            content = await page.content()
            if any(ind in content.lower() for ind in ['just a moment', 'checking your browser']):
                print("      Waiting for Cloudflare clearance...")
                import time
                start = time.time()
                while (time.time() - start) < 60:
                    content = await page.content()
                    if not any(ind in content.lower() for ind in ['just a moment', 'checking your browser']):
                        print(f"      [OK] Cleared after {int(time.time() - start)}s")
                        break
                    await asyncio.sleep(1)
            
            print("[3/5] Looking for search/booking functionality...")
            
            # Take screenshot of homepage
            await page.screenshot(path='data/screenshots/apollo_homepage.png', full_page=True)
            print("      Screenshot: apollo_homepage.png")
            
            # Look for booking/search buttons and links
            await asyncio.sleep(2)
            
            # Try common paths to booking pages
            booking_urls = [
                'https://www.apollocamper.com/motorhome-rental',
                'https://www.apollocamper.com/rv-rental',
                'https://www.apollocamper.com/vehicles',
                'https://www.apollocamper.com/book',
                'https://www.apollocamper.com/search',
            ]
            
            # First, try to find links on the page
            page_text = await page.evaluate('() => document.body.innerText')
            page_html = await page.content()
            
            # Look for "Book", "Search", "Rent", "Vehicles" links
            book_button = await page.query_selector('a[href*="book"], a[href*="search"], a[href*="rent"], a[href*="vehicle"], button:has-text("Book"), button:has-text("Search")')
            
            if book_button:
                print("      [OK] Found booking button/link")
                try:
                    await book_button.click(timeout=10000)
                    await asyncio.sleep(3)
                    print(f"      Navigated to: {page.url}")
                except:
                    print("      Could not click button, trying URL navigation...")
            
            # If still on homepage, try direct URLs
            if 'apollocamper.com' in page.url and len(page.url) < 40:
                print("      Trying direct URLs...")
                for url in booking_urls:
                    try:
                        print(f"      Trying: {url}")
                        response = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        if response and response.status == 200:
                            await asyncio.sleep(2)
                            content = await page.content()
                            if 'price' in content.lower() or 'book' in content.lower():
                                print(f"      [OK] Found booking page: {url}")
                                break
                    except Exception as e:
                        print(f"      [ERROR] {url} - {str(e)[:50]}")
                        continue
            
            print("\n[4/5] Extracting prices from current page...")
            
            # Get all text content
            all_text = await page.evaluate('() => document.body.innerText')
            html_content = await page.content()
            
            # Take screenshot of current page
            current_url = page.url
            screenshot_name = f"data/screenshots/apollo_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_name, full_page=True)
            print(f"      Screenshot: {screenshot_name}")
            
            # Extract prices - comprehensive patterns
            print("\n      Searching for price patterns...")
            
            prices_found = []
            
            # Pattern 1: $XXX per day/night
            pattern1 = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(?:day|night)', all_text, re.IGNORECASE)
            if pattern1:
                print(f"      Pattern 1 ($/day): {pattern1}")
                prices_found.extend([float(p.replace(',', '')) for p in pattern1])
            
            # Pattern 2: From $XXX
            pattern2 = re.findall(r'from\s*\$(\d+(?:,\d{3})*)', all_text, re.IGNORECASE)
            if pattern2:
                print(f"      Pattern 2 (from $): {pattern2}")
                prices_found.extend([float(p.replace(',', '')) for p in pattern2])
            
            # Pattern 3: $XXX/day or $XXX/night
            pattern3 = re.findall(r'\$(\d+(?:,\d{3})*)\s*/\s*(?:day|night)', all_text, re.IGNORECASE)
            if pattern3:
                print(f"      Pattern 3 ($/format): {pattern3}")
                prices_found.extend([float(p.replace(',', '')) for p in pattern3])
            
            # Pattern 4: Just $XXX near vehicle-related words
            lines = all_text.split('\n')
            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in ['vehicle', 'motorhome', 'camper', 'rv', 'class']):
                    # Check this line and next few lines for prices
                    check_lines = '\n'.join(lines[i:min(i+5, len(lines))])
                    pattern4 = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', check_lines)
                    if pattern4:
                        for p in pattern4:
                            price = float(p.replace(',', ''))
                            if 30 <= price <= 1000:  # Reasonable daily/weekly rate
                                prices_found.append(price)
            
            # Pattern 5: Look for price elements in HTML
            price_elements = await page.query_selector_all('[class*="price"], [class*="rate"], [class*="cost"], [id*="price"]')
            if price_elements:
                print(f"      Found {len(price_elements)} price-related elements")
                for elem in price_elements[:20]:  # Check first 20
                    try:
                        elem_text = await elem.inner_text()
                        prices_in_elem = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', elem_text)
                        for p in prices_in_elem:
                            price = float(p.replace(',', ''))
                            if 30 <= price <= 1000:
                                prices_found.append(price)
                    except:
                        continue
            
            print(f"\n[5/5] Results:")
            print(f"      Current URL: {current_url}")
            print(f"      Page length: {len(html_content)} chars")
            
            if prices_found:
                # Filter to reasonable daily rates
                daily_rates = [p for p in prices_found if 30 <= p <= 500]
                if daily_rates:
                    print(f"\n      [SUCCESS] FOUND {len(daily_rates)} REAL PRICES!")
                    print(f"      Prices: {sorted(set(daily_rates))}")
                    print(f"\n      [PRICE RANGE]")
                    print(f"         Lowest:  ${min(daily_rates)}/day")
                    print(f"         Highest: ${max(daily_rates)}/day")
                    print(f"         Average: ${sum(daily_rates)/len(daily_rates):.2f}/day")
                else:
                    prices_all = sorted(set(prices_found))
                    print(f"\n      [WARNING] Found {len(prices_found)} prices but none in daily rate range (30-500)")
                    print(f"      All prices found: {prices_all[:10]}")
            else:
                print(f"\n      [NO PRICES] NO PRICES FOUND")
                print(f"      This might be because:")
                print(f"         - Need to search with specific dates/locations")
                print(f"         - Prices loaded via JavaScript after page load")
                print(f"         - Booking system is on a different domain")
                print(f"         - Need to interact with search form first")
                
                # Show sample of page text
                print(f"\n      Sample page content:")
                sample = all_text[:500].replace('\n', ' ')
                print(f"      {sample}...")
            
            print("\n" + "="*80)
            print("EXTRACTION COMPLETE")
            print("="*80)
            print(f"\nScreenshot saved: {screenshot_name}")
            print("Check the screenshot to see what content is visible.")
            print("="*80 + "\n")
            
            # Keep browser open briefly
            print("Keeping browser open for 5 seconds...")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"\n[ERROR] ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(get_apollo_real_prices())

