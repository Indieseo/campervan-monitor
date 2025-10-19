"""
ULTIMATE Apollo Motorhomes Cloudflare Bypass
Combining cutting-edge 2024-2025 techniques:
- Advanced fingerprint spoofing
- Network interception to capture real APIs
- Enhanced human behavior simulation
- iframe detection and interaction
"""

import asyncio
import sys
import re
import random
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def ultimate_bypass():
    """
    Ultimate bypass with all advanced techniques
    """
    
    print("\n" + "="*80)
    print("APOLLO - ULTIMATE CLOUDFLARE BYPASS (2024-2025 TECHNIQUES)")
    print("="*80 + "\n")
    
    captured_apis = []
    prices_found = []
    
    async with async_playwright() as p:
        print("[1/12] Launching with MAXIMUM stealth...")
        
        # Launch with extensive stealth flags
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=150,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process,VizDisplayCompositor',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--disable-default-apps',
                '--no-first-run',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--force-color-profile=srgb',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
            permissions=['geolocation', 'notifications'],
            color_scheme='light',
            device_scale_factor=1,
        )
        
        page = await context.new_page()
        
        print("[2/12] Injecting ADVANCED anti-detection scripts...")
        
        # ULTIMATE stealth injection - spoofing everything
        await page.add_init_script("""
            // Core webdriver removal
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete navigator.__proto__.webdriver;
            
            // Comprehensive plugin spoofing
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format'},
                        {name: 'Native Client', filename: 'internal-nacl-plugin', description: 'Native Client Executable'}
                    ];
                    return Object.setPrototypeOf(plugins, PluginArray.prototype);
                }
            });
            
            // Language spoofing
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'language', {get: () => 'en-US'});
            
            // Chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {
                    isInstalled: false,
                    InstallState: {DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed'},
                    RunningState: {CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running'}
                }
            };
            
            // Hardware spoofing
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            
            // Canvas fingerprint randomization
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' && this.width === 0 && this.height === 0) {
                    return originalToDataURL.apply(this, arguments);
                }
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                }
                context.putImageData(imageData, 0, 0);
                return originalToDataURL.apply(this, arguments);
            };
            
            // WebGL fingerprint spoofing
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';  // UNMASKED_VENDOR_WEBGL
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER_WEBGL
                return getParameter.apply(this, arguments);
            };
            
            // Audio context fingerprint
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const originalCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
                AudioContext.prototype.createDynamicsCompressor = function() {
                    const compressor = originalCreateDynamicsCompressor.apply(this, arguments);
                    if (compressor.threshold) compressor.threshold.value = -50;
                    if (compressor.knee) compressor.knee.value = 40;
                    if (compressor.ratio) compressor.ratio.value = 12;
                    if (compressor.attack) compressor.attack.value = 0.003;
                    if (compressor.release) compressor.release.value = 0.25;
                    return compressor;
                };
            }
            
            // Battery API spoofing
            Object.defineProperty(navigator, 'getBattery', {
                get: () => async () => ({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                })
            });
            
            // Connection spoofing
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false
                })
            });
            
            // Screen properties
            Object.defineProperty(screen, 'availWidth', {get: () => 1920});
            Object.defineProperty(screen, 'availHeight', {get: () => 1040});
            Object.defineProperty(screen, 'width', {get: () => 1920});
            Object.defineProperty(screen, 'height', {get: () => 1080});
            Object.defineProperty(screen, 'colorDepth', {get: () => 24});
            Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
        """)
        
        print("[3/12] Setting up network interception...")
        
        # Intercept ALL network requests to find APIs
        async def handle_route(route):
            request = route.request
            url = request.url
            
            # Log API calls
            if 'api' in url.lower() or 'graphql' in url.lower():
                print(f"    [API] {request.method} {url[:80]}")
                captured_apis.append({'method': request.method, 'url': url})
            
            await route.continue_()
        
        await page.route('**/*', handle_route)
        
        # Capture responses
        async def handle_response(response):
            url = response.url
            if 'api' in url.lower() or ('apollo' in url.lower() and response.status == 200):
                try:
                    if 'json' in response.headers.get('content-type', '').lower():
                        body = await response.text()
                        if len(body) > 100 and len(body) < 1000000:
                            # Look for prices in response
                            prices = re.findall(r'"price":\s*(\d+(?:\.\d{2})?)', body)
                            if prices:
                                print(f"    [PRICE API] Found prices in {url[:50]}: {prices[:5]}")
                                for p in prices:
                                    try:
                                        val = float(p)
                                        if 20 <= val <= 2000:
                                            prices_found.append(val)
                                    except:
                                        pass
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[4/12] Navigating to main site first...")
        
        try:
            # Start from main site to establish session
            await page.goto('https://www.apollocamper.com/', wait_until='networkidle', timeout=60000)
            print("    Main site loaded")
            
            await asyncio.sleep(3)
            
            # Human behavior
            print("\n[5/12] Simulating human browsing...")
            for _ in range(3):
                x = random.randint(300, 1500)
                y = random.randint(200, 800)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            await page.evaluate('window.scrollTo({top: 500, behavior: "smooth"})')
            await asyncio.sleep(2)
            
            print("[6/12] Clicking Check Availability...")
            
            check_btn = await page.query_selector('button:has-text("CHECK AVAILABILITY"), a:has-text("CHECK AVAILABILITY")')
            if check_btn:
                await check_btn.click()
                await asyncio.sleep(5)
                print("    Clicked! Waiting for booking page...")
            
            # Now we should be on booking subdomain
            current_url = page.url
            print(f"\n[7/12] Current URL: {current_url}")
            
            # Wait for React app to fully load
            print("[8/12] Waiting for React app (networkidle)...")
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(5)
            
            await page.screenshot(path='data/screenshots/apollo_ultimate_1.png', full_page=True)
            
            # Look for iframes
            print("\n[9/12] Checking for iframes...")
            frames = page.frames
            print(f"    Found {len(frames)} frames total")
            
            for i, frame in enumerate(frames):
                try:
                    frame_url = frame.url
                    if frame_url and 'apollo' in frame_url:
                        print(f"    Frame {i}: {frame_url}")
                        
                        # Try to interact with iframe content
                        frame_content = await frame.content()
                        if len(frame_content) > 1000:
                            print(f"      Content length: {len(frame_content)}")
                            
                            # Look for inputs in iframe
                            iframe_inputs = await frame.query_selector_all('input')
                            print(f"      Inputs in iframe: {len(iframe_inputs)}")
                except:
                    pass
            
            print("\n[10/12] Clicking 'Where would you like to travel?' button...")
            
            travel_btn = await page.query_selector('button:has-text("Where would you like to travel")')
            if travel_btn:
                await travel_btn.click()
                print("    Clicked!")
                await asyncio.sleep(10)  # Longer wait for modal/overlay
                
                await page.screenshot(path='data/screenshots/apollo_ultimate_2_clicked.png', full_page=True)
                
                # Check for modal/overlay
                print("\n[11/12] Looking for modal/overlay...")
                
                # Common modal selectors
                modals = await page.query_selector_all('[role="dialog"], .modal, [class*="modal"], [class*="overlay"], [class*="popup"]')
                print(f"    Found {len(modals)} potential modals")
                
                for modal in modals:
                    try:
                        is_visible = await modal.is_visible()
                        if is_visible:
                            print("    [FOUND] Visible modal!")
                            
                            # Find inputs in modal
                            modal_inputs = await modal.query_selector_all('input, select')
                            print(f"    Modal has {len(modal_inputs)} inputs")
                            
                            # Try to fill them
                            for inp in modal_inputs:
                                try:
                                    placeholder = await inp.get_attribute('placeholder')
                                    inp_type = await inp.get_attribute('type')
                                    print(f"      Input: type={inp_type}, placeholder={placeholder}")
                                    
                                    if placeholder and 'location' in placeholder.lower():
                                        await inp.click()
                                        await asyncio.sleep(1)
                                        await inp.fill('United States')
                                        print("      Filled: United States")
                                        await asyncio.sleep(3)
                                except:
                                    continue
                    except:
                        continue
            
            print("\n[12/12] Final extraction...")
            
            await asyncio.sleep(5)
            final_text = await page.evaluate('() => document.body.innerText')
            
            # Extract any visible prices
            visible_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', final_text)
            for p in visible_prices:
                try:
                    val = float(p.replace(',', ''))
                    if 20 <= val <= 2000:
                        prices_found.append(val)
                except:
                    pass
            
            await page.screenshot(path='data/screenshots/apollo_ultimate_final.png', full_page=True)
            
            # Summary
            print("\n" + "="*80)
            print("RESULTS - ULTIMATE BYPASS")
            print("="*80)
            
            print(f"\nCaptured {len(captured_apis)} API calls:")
            for api in captured_apis[:15]:
                print(f"  {api['method']} {api['url'][:80]}")
            
            if prices_found:
                unique_prices = sorted(set(prices_found))
                print(f"\n>>> SUCCESS! FOUND {len(unique_prices)} REAL PRICES!")
                print()
                for price in unique_prices:
                    print(f"    ${price:.2f}")
                
                if len(unique_prices) > 0:
                    print(f"\n>>> STATISTICS:")
                    print(f"    Lowest:  ${min(prices_found):.2f}")
                    print(f"    Highest: ${max(prices_found):.2f}")
                    print(f"    Average: ${sum(prices_found)/len(prices_found):.2f}")
            else:
                print("\n>>> NO PRICES IN AUTOMATED FLOW")
                print("    However, booking.apollocamper.com IS accessible")
                print("    The form requires manual interaction to trigger price API")
            
            print("\n" + "="*80)
            print("BROWSER OPEN FOR 120 SECONDS - TRY MANUALLY")
            print("="*80 + "\n")
            
            for i in range(120, 0, -1):
                print(f"Closing in {i:03d}s... (Try clicking and searching manually!)", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(ultimate_bypass())





