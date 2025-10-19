"""
🚀 LIVE CRAWL DEMO - Real-time Competitive Intelligence
Shows live progress as we scrape all 8 Tier 1 competitors
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScrap,
    YescapaScraper, CamperdaysScraper,
    OutdoorsyScraper, RVshareScraper, CruiseAmericaScraper
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class LiveCrawlDemo:
    """Real-time competitive intelligence crawl with live updates"""
    
    def __init__(self, use_browserless: bool = False):
        self.use_browserless = use_browserless
        self.results: List[Dict] = []
        self.start_time = datetime.now()
        
        # Initialize all 8 scrapers
        self.scrapers = [
            # European Competitors
            RoadsurferScraper(use_browserless=use_browserless),
            GoboonyScrap(use_browserless=use_browserless),
            YescapaScraper(use_browserless=use_browserless),
            McRentScraper(use_browserless=use_browserless),
            CamperdaysScraper(use_browserless=use_browserless),
            # US Competitors
            OutdoorsyScraper(use_browserless=use_browserless),
            RVshareScraper(use_browserless=use_browserless),
            CruiseAmericaScraper(use_browserless=use_browserless)
        ]
    
    def print_header(self):
        """Print impressive header"""
        print("\n" + "="*80)
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 LIVE COMPETITIVE INTELLIGENCE CRAWL{Colors.END}")
        print("="*80)
        print(f"{Colors.BLUE}📊 Monitoring: 8 Tier 1 Competitors (5 European + 3 US){Colors.END}")
        print(f"{Colors.BLUE}🕐 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.BLUE}🌐 Mode: {'Cloud (Browserless)' if self.use_browserless else 'Local Browser'}{Colors.END}")
        print("="*80 + "\n")
    
    def print_scraper_start(self, scraper, index: int, total: int):
        """Print when starting a scraper"""
        region = "🇪🇺 EUROPE" if scraper.company_name in ['Roadsurfer', 'McRent', 'Camperdays', 'Goboony', 'Yescapa'] else "🇺🇸 USA"
        
        print(f"\n{Colors.BOLD}{'─'*80}{Colors.END}")
        print(f"{Colors.YELLOW}⏳ [{index}/{total}] Crawling: {scraper.company_name} {region}{Colors.END}")
        print(f"{Colors.CYAN}   URL: {scraper.config['urls']['homepage']}{Colors.END}")
        print(f"   Strategy: {scraper.config.get('scraping_strategy', 'standard')}")
        print(f"{'─'*80}")
    
    def print_progress_indicator(self):
        """Print a simple progress indicator"""
        print(f"{Colors.CYAN}   ● Launching browser...{Colors.END}", end='\r')
    
    def print_scraper_success(self, data: Dict, duration: float):
        """Print successful scrape results"""
        print(f"\n{Colors.GREEN}✅ SUCCESS - {data['company_name']}{Colors.END}")
        print(f"{Colors.GREEN}{'─'*80}{Colors.END}")
        
        # Key metrics
        print(f"{Colors.BOLD}📈 KEY METRICS:{Colors.END}")
        print(f"   💰 Base Rate:      {data['currency']} {data['base_nightly_rate'] or 'N/A'}/night")
        
        if data.get('is_estimated'):
            print(f"      {Colors.YELLOW}(Industry estimate - method: {data.get('extraction_method', 'N/A')}){Colors.END}")
        else:
            print(f"      {Colors.GREEN}(Extracted - method: {data.get('extraction_method', 'direct')}){Colors.END}")
        
        print(f"   ⭐ Reviews:        {data['customer_review_avg'] or 'N/A'} ({data['review_count'] or 0} reviews)")
        print(f"   📍 Locations:      {len(data['locations_available']) if data['locations_available'] else 0}")
        print(f"   🚐 Fleet Est:      {data['fleet_size_estimate'] or 'N/A'}")
        
        # Additional details
        print(f"\n{Colors.BOLD}💼 OPERATIONAL:{Colors.END}")
        print(f"   🛡️  Insurance:      {data['currency']} {data['insurance_cost_per_day'] or 'N/A'}/day")
        print(f"   🧼 Cleaning:       {data['currency']} {data['cleaning_fee'] or 'N/A'}")
        print(f"   📏 Mileage:        {data['mileage_limit_km'] if data['mileage_limit_km'] is not None else 'Unlimited'} km/day")
        print(f"   🔄 One-way:        {'✓ Yes' if data['one_way_rental_allowed'] else '✗ No'}")
        
        # Competitive intelligence
        print(f"\n{Colors.BOLD}🎯 INTELLIGENCE:{Colors.END}")
        print(f"   🎁 Promotions:     {len(data.get('active_promotions', []))} active")
        print(f"   💳 Payment:        {len(data['payment_options'])} methods")
        print(f"   🎫 Discounts:      {'✓ Available' if data['discount_code_available'] else '✗ None'}")
        print(f"   ⛽ Fuel Policy:    {data['fuel_policy'] or 'N/A'}")
        
        # Quality metrics
        print(f"\n{Colors.BOLD}📊 DATA QUALITY:{Colors.END}")
        completeness = data['data_completeness_pct']
        color = Colors.GREEN if completeness >= 60 else Colors.YELLOW if completeness >= 50 else Colors.RED
        print(f"   {color}● Completeness:    {completeness:.1f}%{Colors.END}")
        print(f"   ⏱️  Scrape Time:     {duration:.1f}s")
        
        if data.get('notes'):
            print(f"   📝 Notes:          {data['notes']}")
        
        print(f"{Colors.GREEN}{'─'*80}{Colors.END}")
    
    def print_scraper_error(self, scraper, error: Exception, duration: float):
        """Print scraper error"""
        print(f"\n{Colors.RED}❌ FAILED - {scraper.company_name}{Colors.END}")
        print(f"{Colors.RED}{'─'*80}{Colors.END}")
        print(f"   Error: {str(error)[:200]}")
        print(f"   Duration: {duration:.1f}s")
        print(f"{Colors.RED}{'─'*80}{Colors.END}")
    
    async def scrape_competitor(self, scraper, index: int, total: int) -> Dict:
        """Scrape a single competitor with live updates"""
        self.print_scraper_start(scraper, index, total)
        self.print_progress_indicator()
        
        start = datetime.now()
        try:
            data = await scraper.scrape()
            duration = (datetime.now() - start).total_seconds()
            self.print_scraper_success(data, duration)
            return data
        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            self.print_scraper_error(scraper, e, duration)
            return {
                'company_name': scraper.company_name,
                'data_completeness_pct': 0,
                'notes': f"Error: {str(e)[:100]}",
                'failed': True
            }
    
    async def run(self):
        """Execute the live crawl"""
        self.print_header()
        
        total = len(self.scrapers)
        
        # Scrape each competitor sequentially for live updates
        for index, scraper in enumerate(self.scrapers, 1):
            data = await self.scrape_competitor(scraper, index, total)
            self.results.append(data)
            
            # Small delay between scrapers
            if index < total:
                await asyncio.sleep(1)
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print("\n\n" + "="*80)
        print(f"{Colors.BOLD}{Colors.CYAN}📊 LIVE CRAWL COMPLETE - MARKET SUMMARY{Colors.END}")
        print("="*80 + "\n")
        
        # Regional breakdown
        european = [r for r in self.results if r.get('company_name') in ['Roadsurfer', 'McRent', 'Camperdays', 'Goboony', 'Yescapa']]
        us = [r for r in self.results if r.get('company_name') in ['Outdoorsy', 'RVshare', 'Cruise America']]
        
        print(f"{Colors.BOLD}🇪🇺 EUROPEAN MARKET (5 competitors):{Colors.END}")
        self.print_regional_summary(european)
        
        print(f"\n{Colors.BOLD}🇺🇸 US MARKET (3 competitors):{Colors.END}")
        self.print_regional_summary(us)
        
        # Global summary
        print(f"\n{Colors.BOLD}🌍 GLOBAL SUMMARY:{Colors.END}")
        print("─"*80)
        
        # Price analysis
        prices = [r['base_nightly_rate'] for r in self.results if r.get('base_nightly_rate') and not r.get('failed')]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            print(f"\n💰 {Colors.BOLD}PRICING INTELLIGENCE:{Colors.END}")
            print(f"   Average Market Price:  EUR {avg_price:.0f}/night")
            print(f"   Price Range:           EUR {min_price:.0f} - {max_price:.0f}")
            print(f"   Price Spread:          EUR {max_price - min_price:.0f} ({(max_price-min_price)/min_price*100:.0f}% variance)")
        
        # Quality metrics
        successful = len([r for r in self.results if not r.get('failed')])
        failed = len([r for r in self.results if r.get('failed')])
        avg_completeness = sum(r.get('data_completeness_pct', 0) for r in self.results) / len(self.results)
        high_quality = len([r for r in self.results if r.get('data_completeness_pct', 0) >= 60])
        
        print(f"\n📊 {Colors.BOLD}DATA QUALITY:{Colors.END}")
        success_color = Colors.GREEN if successful == len(self.scrapers) else Colors.YELLOW
        print(f"   {success_color}Success Rate:          {successful}/{len(self.scrapers)} ({successful/len(self.scrapers)*100:.0f}%){Colors.END}")
        print(f"   Average Completeness:  {avg_completeness:.1f}%")
        print(f"   High Quality (≥60%):   {high_quality}/{len(self.scrapers)} scrapers")
        
        # Performance
        print(f"\n⚡ {Colors.BOLD}PERFORMANCE:{Colors.END}")
        print(f"   Total Time:            {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"   Average per Scraper:   {elapsed/len(self.scrapers):.1f}s")
        
        # Top performers
        print(f"\n🏆 {Colors.BOLD}TOP PERFORMERS (Data Quality):{Colors.END}")
        sorted_results = sorted(
            [r for r in self.results if not r.get('failed')],
            key=lambda x: x.get('data_completeness_pct', 0),
            reverse=True
        )[:3]
        
        for i, result in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"   {medal} {result['company_name']:20s} {result.get('data_completeness_pct', 0):.1f}%")
        
        # Price leaders
        if prices:
            print(f"\n💵 {Colors.BOLD}PRICE POSITIONING:{Colors.END}")
            price_sorted = sorted(
                [r for r in self.results if r.get('base_nightly_rate') and not r.get('failed')],
                key=lambda x: x['base_nightly_rate']
            )
            
            print(f"   🔻 Lowest Price:       {price_sorted[0]['company_name']} - EUR {price_sorted[0]['base_nightly_rate']}/night")
            print(f"   🔺 Highest Price:      {price_sorted[-1]['company_name']} - EUR {price_sorted[-1]['base_nightly_rate']}/night")
            
            if len(price_sorted) >= 2:
                price_gap = price_sorted[-1]['base_nightly_rate'] - price_sorted[0]['base_nightly_rate']
                print(f"   📊 Price Gap:          EUR {price_gap:.0f} ({price_gap/price_sorted[0]['base_nightly_rate']*100:.0f}%)")
        
        # Actionable insights
        print(f"\n💡 {Colors.BOLD}ACTIONABLE INSIGHTS:{Colors.END}")
        insights = self.generate_insights()
        for insight in insights:
            print(f"   • {insight}")
        
        print("\n" + "="*80)
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Competitive intelligence gathering complete!{Colors.END}")
        print(f"{Colors.CYAN}Next: View dashboard → streamlit run dashboard/app.py{Colors.END}")
        print("="*80 + "\n")
    
    def print_regional_summary(self, results: List[Dict]):
        """Print summary for a region"""
        if not results:
            return
        
        for r in results:
            pct = r.get('data_completeness_pct', 0)
            status = "✅" if pct >= 60 and not r.get('failed') else "⚠️" if pct >= 50 else "❌"
            price = f"EUR {r.get('base_nightly_rate', 'N/A')}" if r.get('base_nightly_rate') else "N/A"
            
            name_display = f"{r.get('company_name', 'Unknown'):15s}"
            price_display = f"{price:12s}"
            pct_display = f"{pct:5.1f}%"
            
            color = Colors.GREEN if pct >= 60 else Colors.YELLOW if pct >= 50 else Colors.RED
            print(f"   {status} {name_display} {color}{pct_display}{Colors.END}  {price_display}")
    
    def generate_insights(self) -> List[str]:
        """Generate actionable insights from crawl data"""
        insights = []
        
        # Check success rate
        successful = len([r for r in self.results if not r.get('failed')])
        if successful == len(self.scrapers):
            insights.append("All scrapers operational - full market visibility achieved ✓")
        elif successful >= len(self.scrapers) * 0.75:
            insights.append(f"Good coverage: {successful}/{len(self.scrapers)} competitors monitored")
        else:
            insights.append(f"Limited coverage: Only {successful}/{len(self.scrapers)} scrapers succeeded - review failed sources")
        
        # Price insights
        prices = [r['base_nightly_rate'] for r in self.results if r.get('base_nightly_rate') and not r.get('failed')]
        if prices:
            avg = sum(prices) / len(prices)
            variance = max(prices) - min(prices)
            
            if variance > avg * 0.5:
                insights.append("High price variance detected - opportunity for dynamic pricing strategy")
            
            # Check for promotions
            promotions = sum(len(r.get('active_promotions', [])) for r in self.results)
            if promotions > 3:
                insights.append(f"{promotions} active promotions in market - competitive pressure high")
        
        # Data quality
        avg_completeness = sum(r.get('data_completeness_pct', 0) for r in self.results) / len(self.results)
        if avg_completeness >= 60:
            insights.append("High data quality enables confident strategic decisions")
        elif avg_completeness < 50:
            insights.append("Consider enhancing scrapers for better competitive intelligence")
        
        return insights


async def main():
    """Main entry point"""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print(f"\n{Colors.CYAN}Starting live competitive crawl...{Colors.END}")
    print(f"{Colors.YELLOW}This will take 5-10 minutes. Sit back and watch the magic!{Colors.END}\n")
    
    # Use local browser for better reliability
    demo = LiveCrawlDemo(use_browserless=False)
    await demo.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Crawl interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error: {e}{Colors.END}")

