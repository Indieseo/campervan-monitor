"""
Website Research Tool - Understand Site Structure Before Scraping
Uses Playwright to analyze pages and suggest selectors
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from loguru import logger
import json

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

BASE_DIR = Path(__file__).parent.parent.resolve()
RESEARCH_DIR = BASE_DIR / "research"
RESEARCH_DIR.mkdir(exist_ok=True)


async def research_website(url: str, company_name: str):
    """
    Research a website to understand its structure
    - Takes screenshots
    - Extracts all text
    - Finds potential price selectors
    - Saves HTML
    """
    async with async_playwright() as p:
        print(f"\nResearching: {company_name}")
        print(f"URL: {url}\n")
        
        # Launch browser (non-headless for debugging)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate
            print("⏳ Loading page...")
            await page.goto(url, wait_until='load', timeout=30000)
            await asyncio.sleep(3)
            
            # Take screenshot
            screenshot_path = RESEARCH_DIR / f"{company_name}_screenshot.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Save HTML
            html_path = RESEARCH_DIR / f"{company_name}_source.html"
            html_content = await page.content()
            html_path.write_text(html_content, encoding='utf-8')
            print(f"💾 HTML: {html_path}")
            
            # Extract all text
            text = await page.evaluate('() => document.body.innerText')
            text_path = RESEARCH_DIR / f"{company_name}_text.txt"
            text_path.write_text(text, encoding='utf-8')
            print(f"📄 Text: {text_path}")
            
            # Find all elements with price-like content
            print("\n💰 Searching for price elements...")
            price_elements = await page.query_selector_all('*:has-text("$")')
            print(f"   Found {len(price_elements)} elements containing '$'")
            
            # Analyze price elements
            price_info = []
            for i, elem in enumerate(price_elements[:20]):  # First 20
                try:
                    tag_name = await elem.evaluate('el => el.tagName')
                    class_name = await elem.evaluate('el => el.className')
                    elem_text = await elem.inner_text()
                    
                    if '$' in elem_text and len(elem_text) < 100:
                        price_info.append({
                            'index': i,
                            'tag': tag_name,
                            'class': class_name,
                            'text': elem_text.strip()[:100]
                        })
                except:
                    pass
            
            # Save price analysis
            if price_info:
                price_path = RESEARCH_DIR / f"{company_name}_prices.json"
                price_path.write_text(json.dumps(price_info, indent=2), encoding='utf-8')
                print(f"   💎 Price elements: {price_path}")
                print(f"\n   Top price elements found:")
                for p in price_info[:5]:
                    print(f"      • {p['tag']}.{p['class'][:30]}: {p['text'][:60]}")
            
            # Find forms (booking/quote forms)
            print("\n📋 Searching for forms...")
            forms = await page.query_selector_all('form')
            print(f"   Found {len(forms)} forms")
            
            for i, form in enumerate(forms[:3]):
                try:
                    action = await form.get_attribute('action')
                    inputs = await form.query_selector_all('input, select')
                    print(f"   Form {i+1}: {len(inputs)} inputs, action={action}")
                except:
                    pass
            
            # Find buttons
            print("\n🔘 Searching for buttons...")
            buttons = await page.query_selector_all('button, input[type="submit"], a[class*="btn"]')
            button_texts = []
            for btn in buttons[:10]:
                try:
                    text = await btn.inner_text()
                    if text and len(text) < 50:
                        button_texts.append(text.strip())
                except:
                    pass
            if button_texts:
                print(f"   Buttons: {', '.join(button_texts[:5])}")
            
            # Suggest next steps
            print(f"\n✅ Research complete for {company_name}")
            print("\n📝 NEXT STEPS:")
            print(f"   1. Open screenshot: {screenshot_path}")
            print(f"   2. Review HTML: {html_path}")
            print(f"   3. Check prices found: {RESEARCH_DIR / f'{company_name}_prices.json'}")
            print("   4. Use Playwright Codegen to record interactions:")
            print(f"      python -m playwright codegen {url}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()


async def research_all_competitors():
    """Research all competitor websites"""
    competitors = [
        ("https://www.cruiseamerica.com/rv-reservations", "CruiseAmerica"),
        ("https://roadsurfer.com/rv-rental/prices/", "Roadsurfer"),
        ("https://www.apollocamper.com/", "Apollo"),
        ("https://www.elmonterv.com/", "ElMonteRV"),
        ("https://www.escapecampervans.com/", "EscapeCampervans"),
        ("https://www.jucyusa.com/", "JucyRentals"),
    ]
    
    for url, name in competitors:
        await research_website(url, name)
        print("\n" + "="*80 + "\n")
        await asyncio.sleep(2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        # Research specific site
        url = sys.argv[1]
        name = sys.argv[2]
        asyncio.run(research_website(url, name))
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        # Research all
        asyncio.run(research_all_competitors())
    else:
        print("Usage:")
        print("  Research one site:")
        print("    python research_tool.py <url> <company_name>")
        print("\n  Research all competitors:")
        print("    python research_tool.py all")
        print("\nExample:")
        print("  python research_tool.py https://www.cruiseamerica.com CruiseAmerica")
