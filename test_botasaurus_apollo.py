"""
Test Botasaurus on Apollo Motorhomes - Cloudflare Bypass
Based on PDF analysis showing Botasaurus is most stealthy framework
"""
from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
import time

@browser(
    reuse_driver=False,
    block_images=False,  # Load images for accurate testing
    headless=False,  # Start visible to see what happens
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def scrape_apollo_headless(driver: Driver, data):
    """Test Apollo Motorhomes with Botasaurus"""
    print("🔄 Navigating to Apollo Motorhomes...")
    
    try:
        # Navigate to Apollo
        driver.get("https://apollocamper.com/")
        
        # Wait a bit for page to load
        time.sleep(5)
        
        # Get page content
        html = driver.page_html
        title = driver.title
        
        # Check for Cloudflare challenge
        cloudflare_indicators = [
            "Just a moment",
            "Checking your browser",
            "cf-challenge",
            "challenge-platform"
        ]
        
        cloudflare_detected = any(indicator in html for indicator in cloudflare_indicators)
        
        # Results
        print("\n" + "="*60)
        print("BOTASAURUS TEST RESULTS")
        print("="*60)
        print(f"Page Title: {title}")
        print(f"HTML Length: {len(html)} characters")
        print(f"Cloudflare Challenge: {'❌ DETECTED' if cloudflare_detected else '✅ BYPASSED'}")
        
        if cloudflare_detected:
            print("\n⚠️  Cloudflare challenge page shown")
            print("Waiting 10 more seconds to see if it clears...")
            time.sleep(10)
            html = driver.page_html
            cloudflare_detected = any(indicator in html for indicator in cloudflare_indicators)
            print(f"After waiting: {'❌ STILL BLOCKED' if cloudflare_detected else '✅ CLEARED!'}")
        else:
            print("\n✅ SUCCESS! Apollo page loaded without Cloudflare challenge")
        
        # Save screenshot
        screenshot_path = "data/screenshots/botasaurus_apollo_test.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
        # Try to find some actual content
        try:
            # Look for Apollo-specific elements
            page_text = driver.text
            
            if "apollo" in page_text.lower() or "motorhome" in page_text.lower():
                print("✅ Found Apollo/Motorhome content on page")
            else:
                print("⚠️  No Apollo-specific content found")
                
        except Exception as e:
            print(f"⚠️  Error checking page content: {e}")
        
        print("="*60)
        
        return {
            "success": not cloudflare_detected,
            "title": title,
            "html_length": len(html),
            "cloudflare_detected": cloudflare_detected,
            "url": "https://apollocamper.com/"
        }
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,  # Test in TRUE headless mode!
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def scrape_apollo_truly_headless(driver: Driver, data):
    """Test Apollo in TRUE headless mode - the real test!"""
    print("🔄 Testing TRUE HEADLESS mode...")
    
    try:
        driver.get("https://apollocamper.com/")
        time.sleep(5)
        
        html = driver.page_html
        title = driver.title
        
        cloudflare_indicators = [
            "Just a moment",
            "Checking your browser",
            "cf-challenge",
            "challenge-platform"
        ]
        
        cloudflare_detected = any(indicator in html for indicator in cloudflare_indicators)
        
        print("\n" + "="*60)
        print("BOTASAURUS HEADLESS TEST RESULTS")
        print("="*60)
        print(f"Mode: TRUE HEADLESS")
        print(f"Page Title: {title}")
        print(f"Cloudflare: {'❌ DETECTED' if cloudflare_detected else '✅ BYPASSED'}")
        print("="*60)
        
        driver.save_screenshot("data/screenshots/botasaurus_apollo_headless.png")
        print(f"📸 Headless screenshot saved")
        
        return {
            "success": not cloudflare_detected,
            "mode": "headless",
            "cloudflare_detected": cloudflare_detected
        }
        
    except Exception as e:
        print(f"❌ Headless test error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BOTASAURUS - Apollo Motorhomes Test")
    print("Testing the 'most stealthy' framework from PDF")
    print("="*60 + "\n")
    
    # Test 1: Visible browser first
    print("\n📋 TEST 1: Visible Browser Mode")
    print("-"*60)
    result1 = scrape_apollo_headless()
    
    if result1 and result1.get('success'):
        print("\n✅ Test 1 PASSED: Visible mode works!")
        
        # Test 2: Now try TRUE headless
        print("\n\n📋 TEST 2: Headless Mode (THE REAL TEST)")
        print("-"*60)
        result2 = scrape_apollo_truly_headless()
        
        if result2 and result2.get('success'):
            print("\n" + "="*60)
            print("SUCCESS! BOTASAURUS BYPASSED CLOUDFLARE IN HEADLESS MODE!")
            print("="*60)
        else:
            print("\n⚠️  Headless mode blocked by Cloudflare")
            print("Visible works but headless doesn't (same as Playwright)")
    else:
        print("\n❌ Test 1 FAILED: Even visible mode has issues")
    
    print("\n✅ Testing complete! Check screenshots in data/screenshots/")

