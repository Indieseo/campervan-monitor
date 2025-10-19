"""
Hunt for Apollo Motorhomes booking API or alternative access methods
"""

import asyncio
import sys
import json
from playwright.async_api import async_playwright
from loguru import logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def hunt_apollo_api():
    """
    Hunt for API endpoints and network requests
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - API/NETWORK HUNTER")
    print("="*80 + "\n")
    
    api_calls = []
    
    async with async_playwright() as p:
        print("[1/4] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            locale='en-US',
        )
        
        page = await context.new_page()
        
        # Capture network requests
        def handle_request(request):
            api_calls.append({
                'url': request.url,
                'method': request.method,
                'type': request.resource_type
            })
        
        def handle_response(response):
            url = response.url
            # Look for API calls
            if any(keyword in url.lower() for keyword in ['api', 'graphql', 'booking', 'price', 'vehicle', 'search']):
                print(f"      [API] {response.status} {response.request.method} {url}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # Anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)
        
        print("[2/4] Loading Apollo site and monitoring network...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=60000)
            print("      Page loaded")
            
            # Wait and let JavaScript load
            print("      Waiting 10 seconds for JavaScript to load...")
            await asyncio.sleep(10)
            
            # Scroll to trigger lazy loading
            print("      Scrolling to trigger content loading...")
            for i in range(5):
                await page.evaluate(f'window.scrollTo(0, {i * 500})')
                await asyncio.sleep(1)
            
            print("\n[3/4] Analyzing captured network requests...")
            
            # Filter interesting requests
            api_requests = [r for r in api_calls if any(k in r['url'].lower() for k in ['api', 'graphql', 'booking', 'price', 'vehicle'])]
            json_requests = [r for r in api_calls if r['type'] in ['xhr', 'fetch']]
            
            print(f"      Total requests: {len(api_calls)}")
            print(f"      API-related: {len(api_requests)}")
            print(f"      XHR/Fetch: {len(json_requests)}")
            
            if api_requests:
                print("\n      API Endpoints found:")
                seen_urls = set()
                for req in api_requests[:20]:
                    if req['url'] not in seen_urls:
                        print(f"         {req['method']}: {req['url']}")
                        seen_urls.add(req['url'])
            
            if json_requests:
                print("\n      XHR/Fetch requests:")
                seen_urls = set()
                for req in json_requests[:20]:
                    if req['url'] not in seen_urls:
                        print(f"         {req['method']}: {req['url'][:100]}")
                        seen_urls.add(req['url'])
            
            print("\n[4/4] Checking page for booking widgets/iframes...")
            
            # Look for iframes (often used for booking widgets)
            iframes = await page.query_selector_all('iframe')
            print(f"      Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes[:10]):
                try:
                    src = await iframe.get_attribute('src')
                    name = await iframe.get_attribute('name') or 'unnamed'
                    print(f"         {i+1}. {name}: {src}")
                except:
                    continue
            
            # Look for data attributes that might contain API info
            print("\n      Looking for data attributes...")
            data_attrs = await page.evaluate('''() => {
                const attrs = new Set();
                document.querySelectorAll('[data-api], [data-endpoint], [data-url], [data-booking]').forEach(el => {
                    Object.keys(el.dataset).forEach(key => {
                        if (key.includes('api') || key.includes('url') || key.includes('booking')) {
                            attrs.add(key + ': ' + el.dataset[key]);
                        }
                    });
                });
                return Array.from(attrs);
            }''')
            
            if data_attrs:
                for attr in data_attrs[:10]:
                    print(f"         {attr}")
            else:
                print("         No relevant data attributes found")
            
            # Check for window variables
            print("\n      Checking for JavaScript config objects...")
            config = await page.evaluate('''() => {
                const configs = {};
                if (window.__NEXT_DATA__) configs.nextData = 'Present';
                if (window.__APOLLO_STATE__) configs.apolloState = 'Present';
                if (window.config) configs.config = 'Present';
                if (window.API_URL) configs.apiUrl = window.API_URL;
                if (window.BOOKING_URL) configs.bookingUrl = window.BOOKING_URL;
                return configs;
            }''')
            
            if config:
                print(f"         Found: {json.dumps(config, indent=10)}")
            else:
                print("         No obvious config objects")
            
            # Take screenshot
            await page.screenshot(path='data/screenshots/apollo_api_hunt.png', full_page=True)
            print("\n      Screenshot: apollo_api_hunt.png")
            
            # Get page text to check for booking info
            text = await page.evaluate('() => document.body.innerText')
            
            if 'cloudflare' in text.lower() or 'verifying' in text.lower():
                print("\n      [WARNING] Cloudflare challenge detected")
                print("      Page might not have loaded fully")
            else:
                print("\n      [OK] Page loaded successfully (no Cloudflare detected)")
            
            print("\n" + "="*80)
            print("NETWORK ANALYSIS COMPLETE")
            print("="*80)
            
            # Keep open
            print("\nKeeping browser open for 10 seconds...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(hunt_apollo_api())





