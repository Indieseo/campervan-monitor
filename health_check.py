"""
System Health Check and Monitoring
Provides comprehensive health status of all system components
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        # Try to set console to UTF-8
        os.system('chcp 65001 > nul 2>&1')
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    from core_config import config
except ImportError:
    config = None

try:
    from database.models import get_session, CompetitorPrice, PriceAlert
except ImportError as e:
    print(f"Warning: Could not import database models: {e}")
    get_session = None
    CompetitorPrice = None
    PriceAlert = None


class HealthCheck:
    """
    Comprehensive system health monitoring
    
    Checks:
    - Database connectivity and health
    - Recent scraping activity
    - Data freshness
    - Alert system status
    - Disk space
    - Configuration validity
    """
    
    def __init__(self):
        self.checks = []
        self.status = "unknown"
        self.timestamp = datetime.now()
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks and return comprehensive report
        
        Returns:
            dict: Health check report with status and details
        """
        report = {
            'timestamp': self.timestamp.isoformat(),
            'overall_status': 'unknown',
            'checks': {},
            'summary': {},
            'recommendations': []
        }
        
        # Run individual checks
        report['checks']['database'] = self.check_database()
        report['checks']['scraping'] = self.check_scraping_activity()
        report['checks']['data_freshness'] = self.check_data_freshness()
        report['checks']['alerts'] = self.check_alert_system()
        report['checks']['disk_space'] = self.check_disk_space()
        report['checks']['configuration'] = self.check_configuration()
        
        # Calculate overall status
        statuses = [check['status'] for check in report['checks'].values()]
        if all(s == 'healthy' for s in statuses):
            report['overall_status'] = 'healthy'
        elif any(s == 'critical' for s in statuses):
            report['overall_status'] = 'critical'
        elif any(s == 'warning' for s in statuses):
            report['overall_status'] = 'warning'
        else:
            report['overall_status'] = 'unknown'
        
        # Generate summary
        report['summary'] = {
            'total_checks': len(report['checks']),
            'healthy': sum(1 for s in statuses if s == 'healthy'),
            'warnings': sum(1 for s in statuses if s == 'warning'),
            'critical': sum(1 for s in statuses if s == 'critical'),
            'unknown': sum(1 for s in statuses if s == 'unknown')
        }
        
        # Generate recommendations
        report['recommendations'] = self.generate_recommendations(report['checks'])
        
        return report
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        check = {
            'name': 'Database',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            # Get database path
            if config:
                db_path = config.database.DATABASE_PATH
            else:
                db_path = BASE_DIR / "database" / "campervan_intelligence.db"
            
            # Check if database exists
            if not db_path.exists():
                check['status'] = 'critical'
                check['message'] = 'Database file does not exist'
                check['details']['path'] = str(db_path)
                return check
            
            # Check database connectivity
            session = get_session()
            
            # Check table counts
            price_count = session.query(CompetitorPrice).count()
            alert_count = session.query(PriceAlert).count()
            
            session.close()
            
            # Database is healthy if it has data
            if price_count > 0:
                check['status'] = 'healthy'
                check['message'] = f'Database operational with {price_count} price records'
            else:
                check['status'] = 'warning'
                check['message'] = 'Database is empty - no price records found'
            
            check['details'] = {
                'path': str(db_path),
                'size_mb': db_path.stat().st_size / (1024 * 1024),
                'price_records': price_count,
                'alerts': alert_count
            }
            
        except Exception as e:
            check['status'] = 'critical'
            check['message'] = f'Database error: {str(e)}'
        
        return check
    
    def check_scraping_activity(self) -> Dict[str, Any]:
        """Check recent scraping activity"""
        check = {
            'name': 'Scraping Activity',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            session = get_session()
            
            # Get most recent scrape
            latest_price = session.query(CompetitorPrice)\
                .order_by(CompetitorPrice.scrape_timestamp.desc())\
                .first()
            
            if not latest_price:
                check['status'] = 'warning'
                check['message'] = 'No scraping activity found'
                session.close()
                return check
            
            # Check how recent the last scrape was
            time_since_last = datetime.now() - latest_price.scrape_timestamp
            hours_since = time_since_last.total_seconds() / 3600
            
            if hours_since < 24:
                check['status'] = 'healthy'
                check['message'] = f'Recent scraping activity ({hours_since:.1f}h ago)'
            elif hours_since < 48:
                check['status'] = 'warning'
                check['message'] = f'Scraping activity is stale ({hours_since:.1f}h ago)'
            else:
                check['status'] = 'critical'
                check['message'] = f'No recent scraping activity ({hours_since:.1f}h ago)'
            
            # Count scraped companies in last 24h
            recent_count = session.query(CompetitorPrice)\
                .filter(CompetitorPrice.scrape_timestamp >= datetime.now() - timedelta(hours=24))\
                .count()
            
            check['details'] = {
                'last_scrape': latest_price.scrape_timestamp.isoformat(),
                'hours_since': round(hours_since, 1),
                'recent_companies': recent_count,
                'latest_company': latest_price.company_name
            }
            
            session.close()
            
        except Exception as e:
            check['status'] = 'critical'
            check['message'] = f'Error checking scraping activity: {str(e)}'
        
        return check
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """Check data freshness and quality"""
        check = {
            'name': 'Data Freshness',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            session = get_session()
            
            # Get all prices from last 7 days
            recent_prices = session.query(CompetitorPrice)\
                .filter(CompetitorPrice.scrape_timestamp >= datetime.now() - timedelta(days=7))\
                .all()
            
            if not recent_prices:
                check['status'] = 'critical'
                check['message'] = 'No fresh data (>7 days old)'
                session.close()
                return check
            
            # Calculate average data completeness
            completeness_scores = [
                p.data_completeness_pct for p in recent_prices 
                if p.data_completeness_pct is not None
            ]
            
            avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
            
            # Determine status based on completeness
            if avg_completeness >= 80:
                check['status'] = 'healthy'
                check['message'] = f'Data quality excellent ({avg_completeness:.1f}% complete)'
            elif avg_completeness >= 60:
                check['status'] = 'warning'
                check['message'] = f'Data quality acceptable ({avg_completeness:.1f}% complete)'
            else:
                check['status'] = 'critical'
                check['message'] = f'Data quality poor ({avg_completeness:.1f}% complete)'
            
            check['details'] = {
                'records_last_7_days': len(recent_prices),
                'avg_completeness': round(avg_completeness, 1),
                'companies_tracked': len(set(p.company_name for p in recent_prices))
            }
            
            session.close()
            
        except Exception as e:
            check['status'] = 'critical'
            check['message'] = f'Error checking data freshness: {str(e)}'
        
        return check
    
    def check_alert_system(self) -> Dict[str, Any]:
        """Check alert system status"""
        check = {
            'name': 'Alert System',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            session = get_session()
            
            # Get active alerts
            active_alerts = session.query(PriceAlert)\
                .filter(PriceAlert.is_acknowledged == False)\
                .all()
            
            critical_count = sum(1 for a in active_alerts if a.severity in ['critical', 'high'])
            
            if critical_count > 0:
                check['status'] = 'warning'
                check['message'] = f'{critical_count} critical alerts require attention'
            else:
                check['status'] = 'healthy'
                check['message'] = 'No critical alerts'
            
            check['details'] = {
                'active_alerts': len(active_alerts),
                'critical_alerts': critical_count,
                'alert_system_configured': config.alerts.ENABLE_EMAIL_ALERTS if config else False
            }
            
            session.close()
            
        except Exception as e:
            check['status'] = 'warning'
            check['message'] = f'Unable to check alerts: {str(e)}'
        
        return check
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        check = {
            'name': 'Disk Space',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            import shutil
            
            # Check disk space for project directory
            total, used, free = shutil.disk_usage(BASE_DIR)
            
            # Convert to GB
            free_gb = free / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            percent_free = (free / total) * 100
            
            if percent_free > 20:
                check['status'] = 'healthy'
                check['message'] = f'{free_gb:.1f} GB free ({percent_free:.1f}%)'
            elif percent_free > 10:
                check['status'] = 'warning'
                check['message'] = f'Disk space low: {free_gb:.1f} GB free ({percent_free:.1f}%)'
            else:
                check['status'] = 'critical'
                check['message'] = f'Disk space critical: {free_gb:.1f} GB free ({percent_free:.1f}%)'
            
            check['details'] = {
                'total_gb': round(total_gb, 1),
                'used_gb': round((total - free) / (1024 ** 3), 1),
                'free_gb': round(free_gb, 1),
                'percent_free': round(percent_free, 1)
            }
            
        except Exception as e:
            check['status'] = 'unknown'
            check['message'] = f'Unable to check disk space: {str(e)}'
        
        return check
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check system configuration"""
        check = {
            'name': 'Configuration',
            'status': 'unknown',
            'message': '',
            'details': {}
        }
        
        try:
            if config:
                # Validate configuration
                is_valid, issues = config.validate()
                
                if is_valid:
                    check['status'] = 'healthy'
                    check['message'] = 'Configuration is valid'
                else:
                    check['status'] = 'warning'
                    check['message'] = f'{len(issues)} configuration issues found'
                    check['details']['issues'] = issues
                
                check['details']['browserless_configured'] = bool(config.scraping.BROWSERLESS_API_KEY)
                check['details']['email_alerts_enabled'] = config.alerts.ENABLE_EMAIL_ALERTS
                check['details']['slack_alerts_enabled'] = config.alerts.ENABLE_SLACK_ALERTS
                
            else:
                check['status'] = 'warning'
                check['message'] = 'Configuration module not available'
            
        except Exception as e:
            check['status'] = 'warning'
            check['message'] = f'Configuration check failed: {str(e)}'
        
        return check
    
    def generate_recommendations(self, checks: Dict[str, Dict]) -> List[str]:
        """Generate recommendations based on health check results"""
        recommendations = []
        
        # Database recommendations
        if checks['database']['status'] == 'critical':
            recommendations.append('⚠️  Initialize database with: python -c "from database.models import init_database; init_database()"')
        elif checks['database']['status'] == 'warning':
            recommendations.append('💡 Run scrapers to populate database with data')
        
        # Scraping recommendations
        if checks['scraping']['status'] in ['critical', 'warning']:
            recommendations.append('🔄 Run intelligence gathering: python run_intelligence.py')
        
        # Data freshness recommendations
        if checks['data_freshness']['status'] == 'critical':
            recommendations.append('📊 Data is stale - run scrapers immediately')
        elif checks['data_freshness']['status'] == 'warning':
            recommendations.append('📈 Consider increasing scraping frequency for better data quality')
        
        # Alert recommendations
        if checks['alerts']['details'].get('critical_alerts', 0) > 0:
            recommendations.append('🚨 Review and acknowledge critical alerts in dashboard')
        
        # Disk space recommendations
        if checks['disk_space']['status'] in ['critical', 'warning']:
            recommendations.append('💾 Clean up old data: python data_validator.py --cleanup')
        
        # Configuration recommendations
        if checks['configuration']['status'] == 'warning':
            if checks['configuration']['details'].get('issues'):
                recommendations.append(f"⚙️  Fix configuration issues: {', '.join(checks['configuration']['details']['issues'][:2])}")
        
        # If everything is healthy
        if not recommendations:
            recommendations.append('✅ System is healthy - no action required')
        
        return recommendations
    
    def print_report(self, report: Dict[str, Any]):
        """Print health check report in a readable format"""
        print("\n" + "=" * 70)
        print("🏥 SYSTEM HEALTH CHECK REPORT")
        print("=" * 70)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"🎯 Overall Status: {report['overall_status'].upper()}")
        print("=" * 70)
        
        # Print summary
        summary = report['summary']
        print(f"\n📊 Summary:")
        print(f"   Total Checks: {summary['total_checks']}")
        print(f"   ✅ Healthy: {summary['healthy']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        print(f"   ❌ Critical: {summary['critical']}")
        
        # Print individual checks
        print(f"\n🔍 Detailed Checks:")
        print("-" * 70)
        
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️ ',
            'critical': '❌',
            'unknown': '❓'
        }
        
        for check_name, check_data in report['checks'].items():
            icon = status_icons.get(check_data['status'], '❓')
            print(f"\n{icon} {check_data['name']}: {check_data['status'].upper()}")
            print(f"   {check_data['message']}")
            
            if check_data.get('details'):
                for key, value in check_data['details'].items():
                    if not isinstance(value, (list, dict)):
                        print(f"   • {key}: {value}")
        
        # Print recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            print("-" * 70)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
        
        print("\n" + "=" * 70 + "\n")


def quick_health_check() -> bool:
    """
    Quick health check - returns True if system is healthy
    
    Returns:
        bool: True if healthy, False otherwise
    """
    checker = HealthCheck()
    report = checker.run_all_checks()
    return report['overall_status'] in ['healthy', 'warning']


def main():
    """Main execution - run health check and print report"""
    print("\n🏥 Running comprehensive system health check...")
    
    checker = HealthCheck()
    report = checker.run_all_checks()
    
    # Print human-readable report
    checker.print_report(report)
    
    # Save JSON report
    report_file = BASE_DIR / "health_check_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    if report['overall_status'] == 'critical':
        return 2
    elif report['overall_status'] == 'warning':
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

