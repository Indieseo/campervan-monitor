"""
Focused Competitive Intelligence Engine
Quality over quantity - Deep insights from 10-15 key competitors
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import List, Dict
import json
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
BASE_DIR = Path(__file__).parent.resolve()
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logger.add(
    LOGS_DIR / "intel_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO"
)


class CompetitiveIntelligenceEngine:
    """Main intelligence orchestration"""
    
    def __init__(self):
        self.results = []
        self.alerts = []
        self.insights = []
    
    async def run_tier_1_daily(self):
        """Run daily Tier 1 competitor monitoring"""
        logger.info("🎯 Starting Tier 1 Daily Intelligence Gathering")
        logger.info("=" * 60)
        
        from scrapers.tier1_scrapers import scrape_tier_1_competitors
        
        try:
            results = await scrape_tier_1_competitors()
            self.results = results
            
            # Analyze results
            await self.analyze_results()
            
            # Generate alerts
            await self.generate_alerts()
            
            # Save summary
            await self.save_summary()
            
            logger.info("✅ Daily intelligence gathering complete!")
            
        except Exception as e:
            logger.error(f"❌ Intelligence gathering failed: {e}")
            raise
    
    async def analyze_results(self):
        """Analyze collected data for insights"""
        logger.info("\n📊 Analyzing competitive data...")
        
        if not self.results:
            logger.warning("No results to analyze")
            return
        
        # Calculate market stats
        prices = [r['base_nightly_rate'] for r in self.results if r['base_nightly_rate']]
        
        if prices:
            market_stats = {
                'avg_price': sum(prices) / len(prices),
                'min_price': min(prices),
                'max_price': max(prices),
                'price_range': max(prices) - min(prices),
                'num_competitors': len(prices)
            }
            
            logger.info(f"Market Average: €{market_stats['avg_price']:.2f}/night")
            logger.info(f"Price Range: €{market_stats['min_price']} - €{market_stats['max_price']}")
            
            # Save to database
            from database.models import get_session, MarketIntelligence
            session = get_session()
            
            intel = MarketIntelligence(
                market_avg_price=market_stats['avg_price'],
                market_median_price=sorted(prices)[len(prices)//2],
                price_range_min=market_stats['min_price'],
                price_range_max=market_stats['max_price'],
                market_volatility=self._calculate_std_dev(prices),
                market_summary=f"Analyzed {len(prices)} competitors on {datetime.now().strftime('%Y-%m-%d')}"
            )
            
            session.add(intel)
            session.commit()
            session.close()
            
            logger.info("✅ Market intelligence saved")
    
    def _calculate_std_dev(self, numbers):
        """Calculate standard deviation"""
        if not numbers:
            return 0
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        return variance ** 0.5
    
    async def generate_alerts(self):
        """Generate price alerts and threats"""
        logger.info("\n🚨 Checking for alerts...")
        
        from database.models import get_session, PriceAlert
        
        # Check for significant price changes
        prices = [r['base_nightly_rate'] for r in self.results if r['base_nightly_rate']]
        
        if prices:
            avg_price = sum(prices) / len(prices)
            
            for result in self.results:
                if result['base_nightly_rate']:
                    price_diff_pct = ((result['base_nightly_rate'] - avg_price) / avg_price) * 100
                    
                    # Alert if significantly below market
                    if price_diff_pct < -15:  # 15% below market
                        alert = {
                            'type': 'price_undercut',
                            'severity': 'high',
                            'company': result['company_name'],
                            'message': f"{result['company_name']} is {abs(price_diff_pct):.1f}% below market average",
                            'recommended_action': f"Consider: Highlight value proposition vs {result['company_name']}"
                        }
                        
                        self.alerts.append(alert)
                        logger.warning(f"⚠️ {alert['message']}")
                        
                        # Save to database
                        session = get_session()
                        db_alert = PriceAlert(
                            alert_type=alert['type'],
                            severity=alert['severity'],
                            company_name=alert['company'],
                            new_value=result['base_nightly_rate'],
                            change_pct=price_diff_pct,
                            alert_message=alert['message'],
                            recommended_action=alert['recommended_action']
                        )
                        session.add(db_alert)
                        session.commit()
                        session.close()
                
                # Alert on new promotions
                if result.get('active_promotions'):
                    logger.info(f"📢 {result['company_name']}: {len(result['active_promotions'])} active promotions")
        
        if not self.alerts:
            logger.info("✅ No critical alerts detected")
    
    async def save_summary(self):
        """Save daily summary report"""
        summary_path = BASE_DIR / "data" / "daily_summaries"
        summary_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d')
        report = {
            'date': timestamp,
            'competitors_analyzed': len(self.results),
            'data_completeness_avg': sum(r['data_completeness_pct'] for r in self.results) / len(self.results) if self.results else 0,
            'alerts_generated': len(self.alerts),
            'results': self.results,
            'alerts': self.alerts
        }
        
        report_file = summary_path / f"intelligence_{timestamp}.json"
        report_file.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
        
        logger.info(f"📄 Summary saved: {report_file}")


async def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("🎯 COMPETITIVE INTELLIGENCE ENGINE - FOCUSED APPROACH")
    print("   Quality Over Quantity: Deep insights from key competitors")
    print("=" * 70)
    
    # Initialize database
    print("\n1️⃣ Initializing database...")
    from database.models import init_database
    init_database()
    
    # Run intelligence
    print("\n2️⃣ Gathering competitive intelligence...")
    engine = CompetitiveIntelligenceEngine()
    await engine.run_tier_1_daily()
    
    # Display summary
    print("\n" + "=" * 70)
    print("📊 INTELLIGENCE SUMMARY")
    print("=" * 70)
    
    if engine.results:
        print(f"\n✅ Analyzed {len(engine.results)} competitors")
        
        prices = [r['base_nightly_rate'] for r in engine.results if r['base_nightly_rate']]
        if prices:
            print(f"\n💰 Market Pricing:")
            print(f"   Average: €{sum(prices)/len(prices):.2f}/night")
            print(f"   Range: €{min(prices)} - €{max(prices)}")
        
        if engine.alerts:
            print(f"\n🚨 {len(engine.alerts)} Alerts Generated:")
            for alert in engine.alerts[:3]:
                print(f"   • {alert['message']}")
        else:
            print(f"\n✅ No critical alerts")
        
        # Data quality
        completeness = [r['data_completeness_pct'] for r in engine.results]
        avg_completeness = sum(completeness) / len(completeness)
        print(f"\n📈 Data Quality: {avg_completeness:.1f}% average completeness")
    
    print("\n" + "=" * 70)
    print("✅ Intelligence gathering complete!")
    print("   Next: Run dashboard with: streamlit run dashboard/app.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
