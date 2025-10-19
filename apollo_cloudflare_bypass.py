"""
Advanced Cloudflare bypass techniques for Apollo Motorhomes
Using multiple strategies
"""

import asyncio
import sys
import json
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import time

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def bypass_apollo_cloudflare():
    """
    Advanced Cloudflare bypass with multiple strategies
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - ADVANCED CLOUDFLARE BYPASS")
    print("="*80 + "\n")
    
    async with async_playwright() as p:
        print("[Strategy 1] Using Chrome with persistent context (like real user)")
        
        # Use persistent context (simulates real browser session)
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./temp_browser_profile",
            headless=False,
            slow_mo=200,  # Slower = more human-like
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--window-size=1920,1080',
            ],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Los_Angeles',
            geolocation={'latitude': 34.0522, 'longitude': -118.2437},  # LA
            permissions=['geolocation'],
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Enhanced anti-detection
        await page.add_init_script("""
            // Remove webdriver traces
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {0: {type: "application/x-google-chrome-pdf"}, description: "Portable Document Format", filename: "internal-pdf-viewer", length: 1, name: "Chrome PDF Plugin"},
                    {0: {type: "application/pdf"}, description: "Portable Document Format", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", length: 1, name: "Chrome PDF Viewer"},
                    {0: {type: "application/x-nacl"}, 1: {type: "application/x-pnacl"}, description: "Native Client Executable", filename: "internal-nacl-plugin", length: 2, name: "Native Client"}
                ]
            });
            
            // Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Add realistic properties
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        """)
        
        print("\n[Step 1] Loading homepage and waiting for Cloudflare...")
        
        try:
            # Navigate with very long timeout
            await page.goto('https://www.apollocamper.com/', wait_until='domcontentloaded', timeout=90000)
            print("      Page loaded")
            
            # CRITICAL: Wait longer and simulate human behavior
            print("\n[Step 2] Simulating human behavior during Cloudflare check...")
            
            # Wait and do random mouse movements
            for i in range(20):
                await asyncio.sleep(1)
                
                # Random mouse movements
                x = 300 + (i * 50) % 800
                y = 200 + (i * 30) % 500
                await page.mouse.move(x, y, steps=10)
                
                # Check if Cloudflare cleared
                content = await page.content()
                text = await page.evaluate('() => document.body.innerText')
                
                is_blocked = any(phrase in text.lower() for phrase in [
                    'just a moment',
                    'checking your browser',
                    'verifying you are human',
                    'cloudflare'
                ])
                
                if not is_blocked and len(content) > 50000:
                    print(f"\n      [SUCCESS] Cloudflare cleared after {i+1} seconds!")
                    break
                
                if i % 5 == 0:
                    print(f"      [{i+1:02d}s] Still waiting...", end='\r')
                
                # Small scroll
                if i % 3 == 0:
                    await page.evaluate(f"window.scrollTo(0, {i * 20})")
            
            print("\n\n[Step 3] Checking page status...")
            
            final_content = await page.content()
            final_text = await page.evaluate('() => document.body.innerText')
            
            still_blocked = any(phrase in final_text.lower() for phrase in [
                'just a moment',
                'checking your browser',
                'verifying you are human'
            ])
            
            if still_blocked:
                print("      [STILL BLOCKED] Cloudflare challenge not cleared")
                print("      This may require CAPTCHA solving or manual intervention")
                await page.screenshot(path='data/screenshots/apollo_blocked.png', full_page=True)
            else:
                print("      [SUCCESS] Page loaded successfully!")
                
                # Now try to get prices
                print("\n[Step 4] Looking for prices on page...")
                
                # Extract dollar amounts
                prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', final_text)
                if prices:
                    price_values = []
                    for p in prices:
                        try:
                            val = float(p.replace(',', ''))
                            if 30 <= val <= 500:
                                price_values.append(val)
                        except:
                            pass
                    
                    if price_values:
                        print(f"\n      [PRICES FOUND] {len(price_values)} prices:")
                        print(f"      {sorted(set(price_values))}")
                
                # Look for booking widget
                print("\n[Step 5] Looking for booking form...")
                search_btn = await page.query_selector('button:has-text("Search"), input[type="submit"], button:has-text("Check")')
                if search_btn:
                    print("      Found search button - page is interactive!")
                
                # Take screenshot
                await page.screenshot(path='data/screenshots/apollo_success.png', full_page=True)
                print("      Screenshot: apollo_success.png")
                
                # Try to navigate to USA-specific page
                print("\n[Step 6] Trying USA-specific page...")
                try:
                    await page.goto('https://www.apollocamper.com/usa/rv-rental', wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(5)
                    
                    usa_text = await page.evaluate('() => document.body.innerText')
                    usa_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', usa_text)
                    
                    if usa_prices:
                        print(f"      USA page prices: {usa_prices[:10]}")
                    
                    await page.screenshot(path='data/screenshots/apollo_usa.png', full_page=True)
                except Exception as e:
                    print(f"      Could not load USA page: {str(e)[:50]}")
            
            print("\n" + "="*80)
            print("KEEPING BROWSER OPEN FOR 30 SECONDS")
            print("Try to manually interact with the page if needed")
            print("="*80 + "\n")
            
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(bypass_apollo_cloudflare())





