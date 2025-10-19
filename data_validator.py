"""
Data Quality Validator
Validate, clean, and ensure quality of scraped data
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from loguru import logger
import re

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_DIR = Path(__file__).parent.resolve()

try:
    from core_config import config as sys_config
    DEFAULT_DB_PATH = str(sys_config.database.DATABASE_PATH)
except ImportError:
    DEFAULT_DB_PATH = str(BASE_DIR / "database" / "campervan_intelligence.db")


class DataValidator:
    """Validate and maintain data quality"""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # Quality thresholds
        self.min_price = 20  # Minimum realistic price (€/night)
        self.max_price = 500  # Maximum realistic price (€/night)
        self.max_discount = 90  # Maximum discount percentage
        self.staleness_days = 7  # Data older than this is stale
    
    def validate_price_data(self, price_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate scraped price data before insertion
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Required fields
        required_fields = ['company_name', 'base_price']
        for field in required_fields:
            if field not in price_data or not price_data[field]:
                issues.append(f"Missing required field: {field}")
        
        if issues:
            return False, issues
        
        # Price range validation
        price = price_data.get('base_price', 0)
        if price < self.min_price:
            issues.append(f"Price too low: €{price} (min: €{self.min_price})")
        elif price > self.max_price:
            issues.append(f"Price too high: €{price} (max: €{self.max_price})")
        
        # Discount validation
        discount = price_data.get('discount_percentage', 0)
        if discount < 0:
            issues.append(f"Negative discount: {discount}%")
        elif discount > self.max_discount:
            issues.append(f"Unrealistic discount: {discount}% (max: {self.max_discount}%)")
        
        # Company name validation
        company = price_data.get('company_name', '')
        if len(company) < 2:
            issues.append(f"Invalid company name: '{company}'")
        
        # Date validation
        if 'scrape_date' in price_data:
            try:
                scrape_date = datetime.fromisoformat(price_data['scrape_date'])
                if scrape_date > datetime.now():
                    issues.append("Scrape date is in the future")
            except:
                issues.append("Invalid date format")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def check_for_duplicates(self, price_data: Dict[str, Any]) -> bool:
        """Check if this exact data already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM prices
                WHERE company_name = ?
                AND base_price = ?
                AND scrape_date = date(?)
            """, (
                price_data.get('company_name'),
                price_data.get('base_price'),
                price_data.get('scrape_date', datetime.now().strftime('%Y-%m-%d'))
            ))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}")
            return False
    
    def detect_anomalies(self, company: str = None) -> List[Dict[str, Any]]:
        """Detect price anomalies (outliers)"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            where_clause = ""
            if company:
                where_clause = f"WHERE company_name = '{company}'"
            
            query = f"""
                SELECT 
                    id,
                    company_name,
                    base_price,
                    scrape_date,
                    discount_percentage
                FROM prices
                {where_clause}
                ORDER BY scrape_date DESC
                LIMIT 100
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return []
            
            # Calculate statistics per company
            company_stats = {}
            for row in rows:
                comp = row[1]
                price = row[2]
                
                if comp not in company_stats:
                    company_stats[comp] = {'prices': [], 'rows': []}
                
                company_stats[comp]['prices'].append(price)
                company_stats[comp]['rows'].append(row)
            
            # Detect anomalies (prices > 2 std deviations)
            anomalies = []
            for comp, data in company_stats.items():
                if len(data['prices']) < 3:
                    continue
                
                mean_price = sum(data['prices']) / len(data['prices'])
                variance = sum((x - mean_price) ** 2 for x in data['prices']) / len(data['prices'])
                std_dev = variance ** 0.5
                
                for row in data['rows']:
                    price = row[2]
                    z_score = (price - mean_price) / std_dev if std_dev > 0 else 0
                    
                    if abs(z_score) > 2:
                        anomalies.append({
                            'id': row[0],
                            'company': row[1],
                            'price': row[2],
                            'date': row[3],
                            'z_score': round(z_score, 2),
                            'mean_price': round(mean_price, 2),
                            'deviation': round(price - mean_price, 2),
                            'severity': 'HIGH' if abs(z_score) > 3 else 'MEDIUM'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """Check how fresh the data is for each company"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    company_name,
                    MAX(scrape_date) as last_scrape,
                    COUNT(*) as total_records
                FROM prices
                GROUP BY company_name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            now = datetime.now()
            freshness_report = {
                'fresh': [],
                'stale': [],
                'very_stale': []
            }
            
            for row in rows:
                company = row[0]
                last_scrape = datetime.fromisoformat(row[1])
                days_old = (now - last_scrape).days
                
                entry = {
                    'company': company,
                    'last_scraped': row[1],
                    'days_old': days_old,
                    'total_records': row[2]
                }
                
                if days_old <= 1:
                    freshness_report['fresh'].append(entry)
                elif days_old <= self.staleness_days:
                    freshness_report['stale'].append(entry)
                else:
                    freshness_report['very_stale'].append(entry)
            
            return freshness_report
            
        except Exception as e:
            logger.error(f"Freshness check failed: {e}")
            return {'error': str(e)}
    
    def clean_old_data(self, days_to_keep: int = 90) -> int:
        """Remove data older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                DELETE FROM prices
                WHERE scrape_date < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️  Cleaned {deleted_count} old records (older than {days_to_keep} days)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            return 0
    
    def calculate_quality_score(self) -> Dict[str, Any]:
        """Calculate overall data quality score (0-100)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM prices")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                return {'score': 0, 'message': 'No data available'}
            
            # Recent data (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM prices
                WHERE scrape_date >= date('now', '-7 days')
            """)
            recent_records = cursor.fetchone()[0]
            
            # Companies with data
            cursor.execute("SELECT COUNT(DISTINCT company_name) FROM prices")
            companies_with_data = cursor.fetchone()[0]
            
            # Valid price range
            cursor.execute(f"""
                SELECT COUNT(*) FROM prices
                WHERE base_price BETWEEN {self.min_price} AND {self.max_price}
            """)
            valid_prices = cursor.fetchone()[0]
            
            conn.close()
            
            # Calculate scores
            freshness_score = min(100, (recent_records / total_records) * 100 * 2)  # Weight freshness
            completeness_score = min(100, (companies_with_data / 15) * 100)  # Assume 15 target companies
            validity_score = (valid_prices / total_records) * 100
            
            overall_score = (freshness_score * 0.4 + completeness_score * 0.3 + validity_score * 0.3)
            
            quality_report = {
                'overall_score': round(overall_score, 1),
                'grade': self._score_to_grade(overall_score),
                'metrics': {
                    'freshness_score': round(freshness_score, 1),
                    'completeness_score': round(completeness_score, 1),
                    'validity_score': round(validity_score, 1)
                },
                'details': {
                    'total_records': total_records,
                    'recent_records': recent_records,
                    'companies_tracked': companies_with_data,
                    'valid_price_ratio': round(valid_prices / total_records * 100, 1)
                }
            }
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return {'error': str(e)}
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Fair)'
        elif score >= 60:
            return 'D (Poor)'
        else:
            return 'F (Critical)'
    
    def generate_quality_report(self) -> str:
        """Generate comprehensive quality report"""
        report_lines = [
            "=" * 60,
            "📊 DATA QUALITY REPORT",
            "=" * 60,
            ""
        ]
        
        # Quality score
        quality = self.calculate_quality_score()
        if 'error' not in quality:
            report_lines.extend([
                f"Overall Quality Score: {quality['overall_score']}/100 ({quality['grade']})",
                "",
                "Metrics:",
                f"  • Freshness: {quality['metrics']['freshness_score']}/100",
                f"  • Completeness: {quality['metrics']['completeness_score']}/100",
                f"  • Validity: {quality['metrics']['validity_score']}/100",
                "",
                "Details:",
                f"  • Total Records: {quality['details']['total_records']}",
                f"  • Recent Records (7d): {quality['details']['recent_records']}",
                f"  • Companies Tracked: {quality['details']['companies_tracked']}",
                ""
            ])
        
        # Freshness
        freshness = self.check_data_freshness()
        if 'error' not in freshness:
            report_lines.extend([
                "Data Freshness:",
                f"  • Fresh (≤1 day): {len(freshness['fresh'])} companies",
                f"  • Stale (2-7 days): {len(freshness['stale'])} companies",
                f"  • Very Stale (>7 days): {len(freshness['very_stale'])} companies",
                ""
            ])
        
        # Anomalies
        anomalies = self.detect_anomalies()
        if anomalies:
            report_lines.extend([
                f"⚠️  Anomalies Detected: {len(anomalies)}",
                ""
            ])
            for anom in anomalies[:5]:
                report_lines.append(
                    f"  • {anom['company']}: €{anom['price']} "
                    f"(deviation: €{anom['deviation']}, {anom['severity']})"
                )
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


# Test/CLI usage
if __name__ == "__main__":
    validator = DataValidator()
    
    print(validator.generate_quality_report())
    
    # Test validation
    print("\n🧪 Testing Price Validation:\n")
    
    test_cases = [
        {'company_name': 'Roadsurfer', 'base_price': 95},  # Valid
        {'company_name': 'TestCo', 'base_price': 5},  # Too low
        {'company_name': 'TestCo', 'base_price': 600},  # Too high
        {'company_name': '', 'base_price': 100},  # Missing company
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        is_valid, issues = validator.validate_price_data(test_data)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"{i}. {status}: {test_data}")
        if issues:
            for issue in issues:
                print(f"   - {issue}")
