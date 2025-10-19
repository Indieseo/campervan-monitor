"""
Trend Analysis Engine
Detect pricing patterns, seasonality, and predict future trends
"""

import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from loguru import logger
from collections import defaultdict

BASE_DIR = Path(__file__).parent.resolve()

try:
    from core_config import config as sys_config
    DEFAULT_DB_PATH = str(sys_config.database.DATABASE_PATH)
except ImportError:
    DEFAULT_DB_PATH = str(BASE_DIR / "database" / "campervan_intelligence.db")


class TrendAnalyzer:
    """Analyze historical pricing trends and patterns"""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
    
    def analyze_price_trends(self, company: str = None, days: int = 30) -> Dict[str, Any]:
        """Comprehensive trend analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Build query
            where_clause = f"WHERE scrape_date >= date('now', '-{days} days')"
            if company:
                where_clause += f" AND company_name = '{company}'"
            
            df = pd.read_sql(f"""
                SELECT 
                    company_name,
                    base_price,
                    scrape_date,
                    vehicle_type
                FROM prices
                {where_clause}
                ORDER BY scrape_date
            """, conn)
            conn.close()
            
            if df.empty:
                return {'error': 'No data available'}
            
            # Convert date to datetime
            df['scrape_date'] = pd.to_datetime(df['scrape_date'])
            
            analysis = {
                'overall_trend': self._calculate_trend(df),
                'price_velocity': self._calculate_velocity(df),
                'volatility': self._calculate_volatility(df),
                'patterns': self._detect_patterns(df),
                'by_company': {}
            }
            
            # Per-company analysis
            for comp in df['company_name'].unique():
                comp_df = df[df['company_name'] == comp]
                analysis['by_company'][comp] = {
                    'avg_price': float(comp_df['base_price'].mean()),
                    'trend': self._calculate_trend(comp_df),
                    'price_change': self._calculate_price_change(comp_df),
                    'stability_score': self._calculate_stability(comp_df)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """Determine if prices are rising, falling, or stable"""
        if len(df) < 2:
            return 'insufficient_data'
        
        # Linear regression to find trend
        df = df.sort_values('scrape_date')
        x = np.arange(len(df))
        y = df['base_price'].values
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        if abs(slope) < 0.1:
            return 'stable'
        elif slope > 0:
            return 'rising'
        else:
            return 'falling'
    
    def _calculate_velocity(self, df: pd.DataFrame) -> float:
        """Calculate rate of price change (€/day)"""
        if len(df) < 2:
            return 0.0
        
        df = df.sort_values('scrape_date')
        first_price = df.iloc[0]['base_price']
        last_price = df.iloc[-1]['base_price']
        
        days_diff = (df.iloc[-1]['scrape_date'] - df.iloc[0]['scrape_date']).days
        
        if days_diff == 0:
            return 0.0
        
        return (last_price - first_price) / days_diff
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate price volatility (standard deviation)"""
        return float(df['base_price'].std())
    
    def _calculate_price_change(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate absolute and percentage price change"""
        if len(df) < 2:
            return {'absolute': 0, 'percentage': 0}
        
        df = df.sort_values('scrape_date')
        first_price = df.iloc[0]['base_price']
        last_price = df.iloc[-1]['base_price']
        
        absolute_change = last_price - first_price
        percentage_change = (absolute_change / first_price) * 100 if first_price > 0 else 0
        
        return {
            'absolute': float(absolute_change),
            'percentage': float(percentage_change)
        }
    
    def _calculate_stability(self, df: pd.DataFrame) -> float:
        """Calculate stability score (0-100, higher = more stable)"""
        if len(df) < 2:
            return 100.0
        
        # Based on coefficient of variation
        mean_price = df['base_price'].mean()
        std_price = df['base_price'].std()
        
        if mean_price == 0:
            return 0.0
        
        cv = (std_price / mean_price) * 100
        stability = max(0, 100 - cv)
        
        return float(stability)
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect pricing patterns"""
        patterns = []
        
        if len(df) < 7:
            return ['insufficient_data']
        
        df = df.sort_values('scrape_date')
        prices = df['base_price'].values
        
        # Detect spike
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        if any(prices > mean_price + 2 * std_price):
            patterns.append('price_spike_detected')
        
        # Detect drop
        if any(prices < mean_price - 2 * std_price):
            patterns.append('price_drop_detected')
        
        # Detect gradual increase
        if all(prices[i] <= prices[i+1] for i in range(len(prices)-1)):
            patterns.append('continuous_increase')
        
        # Detect gradual decrease
        if all(prices[i] >= prices[i+1] for i in range(len(prices)-1)):
            patterns.append('continuous_decrease')
        
        # Detect oscillation
        changes = np.diff(prices)
        if len(changes) > 2:
            sign_changes = sum(1 for i in range(len(changes)-1) if changes[i] * changes[i+1] < 0)
            if sign_changes > len(changes) * 0.5:
                patterns.append('oscillating_prices')
        
        return patterns if patterns else ['stable_pricing']
    
    def detect_seasonal_patterns(self, company: str = None) -> Dict[str, Any]:
        """Detect day-of-week and monthly patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            where_clause = ""
            if company:
                where_clause = f"WHERE company_name = '{company}'"
            
            df = pd.read_sql(f"""
                SELECT 
                    company_name,
                    base_price,
                    scrape_date
                FROM prices
                {where_clause}
            """, conn)
            conn.close()
            
            if df.empty:
                return {'error': 'No data available'}
            
            df['scrape_date'] = pd.to_datetime(df['scrape_date'])
            df['day_of_week'] = df['scrape_date'].dt.day_name()
            df['month'] = df['scrape_date'].dt.month_name()
            
            analysis = {
                'day_of_week_avg': df.groupby('day_of_week')['base_price'].mean().to_dict(),
                'monthly_avg': df.groupby('month')['base_price'].mean().to_dict(),
                'peak_day': df.groupby('day_of_week')['base_price'].mean().idxmax(),
                'lowest_day': df.groupby('day_of_week')['base_price'].mean().idxmin(),
                'peak_month': df.groupby('month')['base_price'].mean().idxmax(),
                'lowest_month': df.groupby('month')['base_price'].mean().idxmin()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Seasonal analysis failed: {e}")
            return {'error': str(e)}
    
    def predict_future_prices(self, company: str, days_ahead: int = 7) -> Dict[str, Any]:
        """Simple price prediction using moving average"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            df = pd.read_sql(f"""
                SELECT 
                    base_price,
                    scrape_date
                FROM prices
                WHERE company_name = '{company}'
                ORDER BY scrape_date DESC
                LIMIT 30
            """, conn)
            conn.close()
            
            if len(df) < 7:
                return {'error': 'Insufficient data for prediction'}
            
            df = df.sort_values('scrape_date')
            df['scrape_date'] = pd.to_datetime(df['scrape_date'])
            
            # Calculate moving average
            ma_7 = df['base_price'].rolling(window=7).mean().iloc[-1]
            
            # Calculate trend
            recent_prices = df['base_price'].values[-7:]
            trend = np.mean(np.diff(recent_prices))
            
            # Predict
            predictions = []
            last_date = df['scrape_date'].iloc[-1]
            
            for i in range(1, days_ahead + 1):
                pred_date = last_date + timedelta(days=i)
                pred_price = ma_7 + (trend * i)
                
                predictions.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'predicted_price': float(max(0, pred_price)),  # No negative prices
                    'confidence': 'low' if i > 3 else 'medium'
                })
            
            return {
                'company': company,
                'current_price': float(df['base_price'].iloc[-1]),
                'moving_avg_7d': float(ma_7),
                'trend': 'increasing' if trend > 0 else 'decreasing',
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"❌ Price prediction failed: {e}")
            return {'error': str(e)}
    
    def compare_competitors(self, days: int = 30) -> Dict[str, Any]:
        """Compare all competitors"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            df = pd.read_sql(f"""
                SELECT 
                    company_name,
                    AVG(base_price) as avg_price,
                    MIN(base_price) as min_price,
                    MAX(base_price) as max_price,
                    COUNT(*) as data_points
                FROM prices
                WHERE scrape_date >= date('now', '-{days} days')
                GROUP BY company_name
                ORDER BY avg_price ASC
            """, conn)
            conn.close()
            
            if df.empty:
                return {'error': 'No data available'}
            
            market_avg = df['avg_price'].mean()
            
            comparison = {
                'market_average': float(market_avg),
                'market_range': {
                    'min': float(df['min_price'].min()),
                    'max': float(df['max_price'].max())
                },
                'competitors': []
            }
            
            for _, row in df.iterrows():
                gap_to_avg = row['avg_price'] - market_avg
                percentile = (df[df['avg_price'] <= row['avg_price']].shape[0] / len(df)) * 100
                
                comparison['competitors'].append({
                    'company': row['company_name'],
                    'avg_price': float(row['avg_price']),
                    'price_range': f"€{row['min_price']:.0f} - €{row['max_price']:.0f}",
                    'gap_to_market': float(gap_to_avg),
                    'market_percentile': float(percentile),
                    'data_points': int(row['data_points'])
                })
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Competitor comparison failed: {e}")
            return {'error': str(e)}


# Test/CLI usage
if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    
    print("📈 Running Trend Analysis...\n")
    
    # Overall trends
    print("1️⃣ Overall Market Trends (Last 30 days)")
    print("=" * 50)
    trends = analyzer.analyze_price_trends(days=30)
    if 'error' not in trends:
        print(f"Overall Trend: {trends['overall_trend']}")
        print(f"Volatility: €{trends['volatility']:.2f}")
        print(f"Price Velocity: €{trends['price_velocity']:.2f}/day")
        print(f"Patterns: {', '.join(trends['patterns'])}")
    print()
    
    # Seasonal patterns
    print("2️⃣ Seasonal Patterns")
    print("=" * 50)
    seasonal = analyzer.detect_seasonal_patterns()
    if 'error' not in seasonal:
        print(f"Peak Day: {seasonal['peak_day']}")
        print(f"Lowest Day: {seasonal['lowest_day']}")
    print()
    
    # Competitor comparison
    print("3️⃣ Competitor Comparison")
    print("=" * 50)
    comparison = analyzer.compare_competitors(days=30)
    if 'error' not in comparison:
        print(f"Market Average: €{comparison['market_average']:.2f}")
        for comp in comparison['competitors'][:5]:
            print(f"  {comp['company']}: €{comp['avg_price']:.2f} ({comp['market_percentile']:.0f}th percentile)")
