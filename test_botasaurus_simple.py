"""
Test Botasaurus on Apollo Motorhomes - Cloudflare Bypass
Simplified version without emoji for Windows compatibility
"""
from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
import time

@browser(
    reuse_driver=False,
    block_images=False,
    headless=False,  # Start visible
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def test_apollo_visible(driver: Driver, data):
    """Test with visible browser"""
    print("Navigating to Apollo Motorhomes...")
    
    driver.get("https://apollocamper.com/")
    time.sleep(5)
    
    html = driver.page_html
    title = driver.title
    
    cloudflare_found = "Just a moment" in html or "Checking your browser" in html
    
    print("\n" + "="*60)
    print("TEST 1: VISIBLE BROWSER")
    print("="*60)
    print(f"Title: {title}")
    print(f"HTML Length: {len(html)} chars")
    print(f"Cloudflare: {'DETECTED' if cloudflare_found else 'BYPASSED'}")
    print("="*60)
    
    driver.save_screenshot("data/screenshots/botasaurus_visible.png")
    print("Screenshot saved: data/screenshots/botasaurus_visible.png")
    
    return {"success": not cloudflare_found, "mode": "visible"}


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,  # TRUE HEADLESS - the real test!
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def test_apollo_headless(driver: Driver, data):
    """Test with TRUE headless browser"""
    print("\nTesting TRUE HEADLESS mode...")
    
    driver.get("https://apollocamper.com/")
    time.sleep(5)
    
    html = driver.page_html
    title = driver.title
    
    cloudflare_found = "Just a moment" in html or "Checking your browser" in html
    
    print("\n" + "="*60)
    print("TEST 2: HEADLESS BROWSER")
    print("="*60)
    print(f"Title: {title}")
    print(f"HTML Length: {len(html)} chars")
    print(f"Cloudflare: {'DETECTED' if cloudflare_found else 'BYPASSED'}")
    print("="*60)
    
    driver.save_screenshot("data/screenshots/botasaurus_headless.png")
    print("Screenshot saved: data/screenshots/botasaurus_headless.png")
    
    return {"success": not cloudflare_found, "mode": "headless"}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BOTASAURUS CLOUDFLARE BYPASS TEST")
    print("Testing Apollo Motorhomes")
    print("="*60 + "\n")
    
    # Test 1: Visible
    print("Running TEST 1: Visible Browser...")
    result1 = test_apollo_visible()
    
    if result1 and result1.get('success'):
        print("\n[SUCCESS] Test 1 passed - Visible mode works!")
        
        # Test 2: Headless
        print("\nRunning TEST 2: Headless Browser...")
        result2 = test_apollo_headless()
        
        if result2 and result2.get('success'):
            print("\n" + "="*60)
            print("COMPLETE SUCCESS!")
            print("Botasaurus bypassed Cloudflare in HEADLESS mode!")
            print("="*60)
        else:
            print("\n[PARTIAL] Visible works, headless blocked")
    else:
        print("\n[FAILED] Test 1 failed - even visible mode has issues")
    
    print("\nTest complete! Check screenshots in data/screenshots/")




