"""
Advanced Cloudflare Bypass for Apollo Motorhomes and Similar Sites
Uses stealth techniques, proper browser fingerprinting, and intelligent waiting
"""

import asyncio
import sys
from typing import Optional, Dict
from playwright.async_api import Page, Browser, BrowserContext
from loguru import logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class CloudflareBypassScraper:
    """
    Advanced scraper with Cloudflare bypass capabilities
    
    Techniques used:
    1. Realistic browser fingerprinting
    2. Proper viewport and headers
    3. Mouse movements and human-like behavior
    4. Intelligent challenge detection and waiting
    5. CDP (Chrome DevTools Protocol) for stealth
    """
    
    def __init__(self, company_name: str, target_url: str):
        self.company_name = company_name
        self.target_url = target_url
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def launch_stealth_browser(self) -> Browser:
        """Launch browser with stealth configuration to avoid detection"""
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        
        # Launch with stealth args
        browser = await playwright.chromium.launch(
            headless=False,  # Cloudflare detects headless easily
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=BlockInsecurePrivateNetworkRequests',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--start-maximized',
            ]
        )
        
        logger.info(f"✅ Launched stealth browser for {self.company_name}")
        return browser
    
    async def create_stealth_context(self, browser: Browser) -> BrowserContext:
        """Create browser context with realistic fingerprinting"""
        
        # Realistic user agent (recent Chrome on Windows)
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
            color_scheme='light',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        logger.info(f"✅ Created stealth context with realistic fingerprinting")
        return context
    
    async def inject_stealth_scripts(self, page: Page):
        """Inject JavaScript to mask automation detection"""
        
        # Override navigator.webdriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Override plugins
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        # Override languages
        await page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        # Override chrome detection
        await page.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)
        
        # Override permissions
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        logger.debug("✅ Injected stealth scripts")
    
    async def detect_cloudflare_challenge(self, page: Page) -> bool:
        """Detect if Cloudflare challenge is present"""
        
        # Check for common Cloudflare indicators
        indicators = [
            'Just a moment',
            'Checking your browser',
            'Please wait',
            'Cloudflare',
            'cf-browser-verification',
            'cf-challenge',
            'ray id'
        ]
        
        try:
            content = await page.content()
            content_lower = content.lower()
            
            for indicator in indicators:
                if indicator.lower() in content_lower:
                    logger.warning(f"🔍 Cloudflare challenge detected: '{indicator}'")
                    return True
            
            # Check for specific elements
            cf_selectors = [
                '#challenge-running',
                '.cf-browser-verification',
                '#cf-challenge-running',
                '[id*="cloudflare"]',
                '[class*="cloudflare"]'
            ]
            
            for selector in cf_selectors:
                if await page.locator(selector).count() > 0:
                    logger.warning(f"🔍 Cloudflare element found: {selector}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Challenge detection error: {e}")
            return False
    
    async def wait_for_cloudflare_clearance(self, page: Page, max_wait: int = 30):
        """Wait for Cloudflare challenge to complete"""
        
        logger.info("⏳ Waiting for Cloudflare clearance...")
        
        start_time = asyncio.get_event_loop().time()
        check_interval = 1  # Check every second
        
        while (asyncio.get_event_loop().time() - start_time) < max_wait:
            # Check if challenge is still present
            if not await self.detect_cloudflare_challenge(page):
                logger.info("✅ Cloudflare challenge cleared!")
                return True
            
            # Wait a bit
            await asyncio.sleep(check_interval)
            logger.debug(f"⏳ Still waiting... ({int(asyncio.get_event_loop().time() - start_time)}s)")
        
        logger.warning(f"⚠️ Cloudflare challenge did not clear after {max_wait}s")
        return False
    
    async def simulate_human_behavior(self, page: Page):
        """Simulate human-like mouse movements and scrolling"""
        
        try:
            # Random mouse movement
            await page.mouse.move(100, 100)
            await asyncio.sleep(0.1)
            await page.mouse.move(500, 300)
            await asyncio.sleep(0.1)
            await page.mouse.move(800, 600)
            
            # Scroll down slowly
            await page.evaluate("""
                window.scrollTo({
                    top: 200,
                    behavior: 'smooth'
                });
            """)
            await asyncio.sleep(0.5)
            
            await page.evaluate("""
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            """)
            await asyncio.sleep(0.5)
            
            logger.debug("✅ Simulated human behavior")
            
        except Exception as e:
            logger.debug(f"Human behavior simulation error: {e}")
    
    async def bypass_and_scrape(self) -> Dict:
        """Main method to bypass Cloudflare and scrape the site"""
        
        logger.info(f"🚀 Starting Cloudflare bypass for {self.company_name}")
        logger.info(f"🌐 Target: {self.target_url}")
        
        result = {
            'success': False,
            'cloudflare_detected': False,
            'cloudflare_bypassed': False,
            'page_content': None,
            'final_url': None,
            'screenshots': [],
            'error': None
        }
        
        try:
            # Launch stealth browser
            self.browser = await self.launch_stealth_browser()
            self.context = await self.create_stealth_context(self.browser)
            self.page = await self.context.new_page()
            
            # Inject stealth scripts
            await self.inject_stealth_scripts(self.page)
            
            # Navigate to target
            logger.info(f"🌐 Navigating to {self.target_url}")
            
            try:
                response = await self.page.goto(
                    self.target_url,
                    wait_until='domcontentloaded',
                    timeout=30000
                )
                logger.info(f"✅ Initial navigation complete (Status: {response.status if response else 'N/A'})")
            except Exception as e:
                logger.error(f"❌ Navigation failed: {e}")
                result['error'] = str(e)
                return result
            
            # Wait a bit for page to load
            await asyncio.sleep(2)
            
            # Take screenshot 1: Initial state
            screenshot_path = f"data/screenshots/{self.company_name}_initial_cloudflare.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            result['screenshots'].append(screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            # Check for Cloudflare challenge
            has_challenge = await self.detect_cloudflare_challenge(self.page)
            result['cloudflare_detected'] = has_challenge
            
            if has_challenge:
                logger.warning("🛡️ Cloudflare challenge detected!")
                
                # Simulate human behavior while waiting
                await self.simulate_human_behavior(self.page)
                
                # Wait for Cloudflare to clear
                cleared = await self.wait_for_cloudflare_clearance(self.page, max_wait=30)
                result['cloudflare_bypassed'] = cleared
                
                if cleared:
                    logger.info("✅ Successfully bypassed Cloudflare!")
                    
                    # Wait for content to load
                    await asyncio.sleep(3)
                    
                    # Take screenshot 2: After bypass
                    screenshot_path = f"data/screenshots/{self.company_name}_after_bypass.png"
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    result['screenshots'].append(screenshot_path)
                    logger.info(f"📸 Screenshot saved: {screenshot_path}")
                else:
                    logger.error("❌ Failed to bypass Cloudflare")
                    return result
            else:
                logger.info("✅ No Cloudflare challenge detected!")
                result['cloudflare_bypassed'] = True
            
            # Get final page state
            result['final_url'] = self.page.url
            result['page_content'] = await self.page.content()
            result['success'] = True
            
            logger.info(f"✅ Successfully scraped {self.company_name}")
            logger.info(f"📄 Final URL: {result['final_url']}")
            logger.info(f"📏 Content length: {len(result['page_content'])} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Bypass failed: {e}")
            result['error'] = str(e)
            return result
            
        finally:
            # Cleanup
            if self.page:
                try:
                    # Final screenshot
                    screenshot_path = f"data/screenshots/{self.company_name}_final_state.png"
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    result['screenshots'].append(screenshot_path)
                    logger.info(f"📸 Final screenshot: {screenshot_path}")
                except:
                    pass
            
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            
            logger.info(f"🧹 Cleanup complete for {self.company_name}")


async def test_apollo_bypass():
    """Test Cloudflare bypass on Apollo Motorhomes"""
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - CLOUDFLARE BYPASS TEST")
    print("="*80 + "\n")
    
    scraper = CloudflareBypassScraper(
        company_name="Apollo Motorhomes",
        target_url="https://www.apollocamper.com/"
    )
    
    result = await scraper.bypass_and_scrape()
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Success:              {'YES' if result['success'] else 'NO'}")
    print(f"Cloudflare Detected:  {'YES' if result['cloudflare_detected'] else 'NO'}")
    print(f"Cloudflare Bypassed:  {'YES' if result['cloudflare_bypassed'] else 'NO'}")
    print(f"Final URL:            {result['final_url']}")
    print(f"Screenshots:          {len(result['screenshots'])} captured")
    
    for idx, path in enumerate(result['screenshots'], 1):
        print(f"  {idx}. {path}")
    
    if result['error']:
        print(f"Error:                {result['error']}")
    
    if result['page_content']:
        print(f"Content Length:       {len(result['page_content'])} characters")
        
        # Check for actual content
        if 'apollo' in result['page_content'].lower():
            print("[OK] Confirmed: Apollo content loaded!")
        else:
            print("[WARN] Warning: Apollo content not detected in page")
    
    print("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_apollo_bypass())

