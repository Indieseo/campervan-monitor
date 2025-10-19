"""
Validation System
Comprehensive validation and verification for 365-day scraping
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class ValidationSystem:
    def __init__(self):
        self.target_companies = [
            'Roadsurfer', 'Camperdays', 'Goboony', 'Outdoorsy', 'RVshare',
            'McRent', 'Yescapa', 'Cruise America'
        ]
        self.target_days = 365
        self.state_file = "output/scraping_state.json"
        self.validation_file = "output/validation_results.json"
        
    def load_scraping_state(self) -> Dict:
        """Load current scraping state"""
        if Path(self.state_file).exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        return {}
    
    def validate_all_data(self) -> Dict:
        """Validate all scraped data"""
        logger.info("🔍 STARTING COMPREHENSIVE VALIDATION")
        logger.info("="*60)
        
        state = self.load_scraping_state()
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_completion': 0.0,
            'companies_validation': {},
            'summary': {
                'total_companies': len(self.target_companies),
                'complete_companies': 0,
                'total_days_scraped': 0,
                'total_target_days': len(self.target_companies) * self.target_days,
                'data_quality_score': 0.0
            }
        }
        
        total_completion = 0
        total_quality_score = 0
        
        for company in self.target_companies:
            logger.info(f"\n🔍 Validating: {company}")
            
            company_data = state.get(company, {})
            company_validation = self.validate_company_data(company, company_data)
            
            validation_results['companies_validation'][company] = company_validation
            
            # Update summary
            if company_validation['complete']:
                validation_results['summary']['complete_companies'] += 1
            
            validation_results['summary']['total_days_scraped'] += company_validation['days_scraped']
            
            total_completion += company_validation['completion_percentage']
            total_quality_score += company_validation['quality_score']
            
            # Log results
            status = "✅ COMPLETE" if company_validation['complete'] else "❌ INCOMPLETE"
            logger.info(f"  {status} - {company_validation['days_scraped']}/{self.target_days} days - Quality: {company_validation['quality_score']:.1f}%")
        
        # Calculate overall metrics
        validation_results['overall_completion'] = total_completion / len(self.target_companies)
        validation_results['summary']['data_quality_score'] = total_quality_score / len(self.target_companies)
        
        # Save validation results
        with open(self.validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Overall Completion: {validation_results['overall_completion']:.1f}%")
        logger.info(f"Complete Companies: {validation_results['summary']['complete_companies']}/{validation_results['summary']['total_companies']}")
        logger.info(f"Total Days Scraped: {validation_results['summary']['total_days_scraped']}/{validation_results['summary']['total_target_days']}")
        logger.info(f"Data Quality Score: {validation_results['summary']['data_quality_score']:.1f}%")
        
        return validation_results
    
    def validate_company_data(self, company: str, data: Dict) -> Dict:
        """Validate data for specific company"""
        validation = {
            'company': company,
            'complete': False,
            'days_scraped': 0,
            'target_days': self.target_days,
            'completion_percentage': 0.0,
            'quality_score': 0.0,
            'checks': {
                'has_data': False,
                'has_vehicles': False,
                'has_365_days': False,
                'has_valid_prices': False,
                'has_currency': False,
                'has_timestamps': False,
                'has_continuous_dates': False,
                'price_range_valid': False
            },
            'issues': [],
            'recommendations': []
        }
        
        # Check if data exists
        if not data:
            validation['issues'].append("No data found")
            validation['recommendations'].append("Run scraping for this company")
            return validation
        
        validation['checks']['has_data'] = True
        
        # Check vehicles
        vehicles = data.get('vehicles', [])
        if len(vehicles) > 0:
            validation['checks']['has_vehicles'] = True
        else:
            validation['issues'].append("No vehicles found")
            validation['recommendations'].append("Extract vehicle information")
        
        # Check daily prices
        daily_prices = data.get('daily_prices', [])
        validation['days_scraped'] = len(daily_prices)
        
        if len(daily_prices) >= self.target_days:
            validation['checks']['has_365_days'] = True
        else:
            missing_days = self.target_days - len(daily_prices)
            validation['issues'].append(f"Missing {missing_days} days of data")
            validation['recommendations'].append(f"Scrape {missing_days} more days")
        
        # Check price validity
        if daily_prices:
            prices = [day.get('price', 0) for day in daily_prices if isinstance(day, dict)]
            valid_prices = [p for p in prices if p > 0]
            
            if len(valid_prices) > 0:
                validation['checks']['has_valid_prices'] = True
                
                # Check price range
                min_price = min(valid_prices)
                max_price = max(valid_prices)
                
                # Reasonable price ranges
                if company in ['Roadsurfer', 'Camperdays', 'Goboony', 'McRent', 'Yescapa']:
                    # EUR companies
                    if 10 <= min_price <= 1000 and 10 <= max_price <= 1000:
                        validation['checks']['price_range_valid'] = True
                    else:
                        validation['issues'].append(f"Invalid price range: €{min_price}-€{max_price}")
                else:
                    # USD companies
                    if 20 <= min_price <= 2000 and 20 <= max_price <= 2000:
                        validation['checks']['price_range_valid'] = True
                    else:
                        validation['issues'].append(f"Invalid price range: ${min_price}-${max_price}")
            else:
                validation['issues'].append("No valid prices found")
                validation['recommendations'].append("Check price extraction logic")
        
        # Check currency
        currency = data.get('currency', '')
        if currency in ['EUR', 'USD']:
            validation['checks']['has_currency'] = True
        else:
            validation['issues'].append(f"Invalid or missing currency: {currency}")
            validation['recommendations'].append("Set correct currency")
        
        # Check timestamps
        if daily_prices:
            timestamps = [day.get('timestamp') for day in daily_prices if isinstance(day, dict)]
            valid_timestamps = [ts for ts in timestamps if ts]
            
            if len(valid_timestamps) > 0:
                validation['checks']['has_timestamps'] = True
            else:
                validation['issues'].append("Missing timestamps")
                validation['recommendations'].append("Add timestamps to daily prices")
        
        # Check date continuity
        if daily_prices and len(daily_prices) > 1:
            dates = []
            for day in daily_prices:
                if isinstance(day, dict) and 'date' in day:
                    try:
                        dates.append(datetime.fromisoformat(day['date'].replace('Z', '+00:00')))
                    except:
                        pass
            
            if len(dates) > 1:
                dates.sort()
                gaps = []
                for i in range(1, len(dates)):
                    gap = (dates[i] - dates[i-1]).days
                    if gap > 1:
                        gaps.append(gap)
                
                if not gaps:
                    validation['checks']['has_continuous_dates'] = True
                else:
                    validation['issues'].append(f"Date gaps found: {gaps}")
                    validation['recommendations'].append("Fill missing dates")
        
        # Calculate completion percentage
        validation['completion_percentage'] = (len(daily_prices) / self.target_days) * 100
        
        # Calculate quality score
        checks_passed = sum(validation['checks'].values())
        total_checks = len(validation['checks'])
        validation['quality_score'] = (checks_passed / total_checks) * 100
        
        # Determine if complete
        validation['complete'] = (
            validation['checks']['has_data'] and
            validation['checks']['has_vehicles'] and
            validation['checks']['has_365_days'] and
            validation['checks']['has_valid_prices'] and
            validation['checks']['has_currency'] and
            validation['quality_score'] >= 80.0
        )
        
        return validation
    
    def find_missing_data(self) -> Dict:
        """Find specific missing data points"""
        logger.info("🔍 FINDING MISSING DATA")
        logger.info("="*40)
        
        state = self.load_scraping_state()
        missing_data = {
            'timestamp': datetime.now().isoformat(),
            'missing_companies': [],
            'missing_days': {},
            'missing_vehicles': [],
            'data_quality_issues': []
        }
        
        for company in self.target_companies:
            company_data = state.get(company, {})
            
            # Check if company data exists
            if not company_data:
                missing_data['missing_companies'].append(company)
                logger.warning(f"❌ {company}: No data found")
                continue
            
            # Check missing days
            daily_prices = company_data.get('daily_prices', [])
            if len(daily_prices) < self.target_days:
                missing_days = self.target_days - len(daily_prices)
                missing_data['missing_days'][company] = missing_days
                logger.warning(f"⚠️ {company}: Missing {missing_days} days")
            
            # Check missing vehicles
            vehicles = company_data.get('vehicles', [])
            if len(vehicles) == 0:
                missing_data['missing_vehicles'].append(company)
                logger.warning(f"⚠️ {company}: No vehicles found")
            
            # Check data quality
            validation = self.validate_company_data(company, company_data)
            if validation['quality_score'] < 80:
                missing_data['data_quality_issues'].append({
                    'company': company,
                    'quality_score': validation['quality_score'],
                    'issues': validation['issues']
                })
                logger.warning(f"⚠️ {company}: Quality score {validation['quality_score']:.1f}%")
        
        # Save missing data report
        missing_file = "output/missing_data_report.json"
        with open(missing_file, 'w') as f:
            json.dump(missing_data, f, indent=2, default=str)
        
        logger.info(f"💾 Missing data report saved to: {missing_file}")
        
        return missing_data
    
    def generate_completion_report(self) -> Dict:
        """Generate comprehensive completion report"""
        logger.info("📊 GENERATING COMPLETION REPORT")
        logger.info("="*40)
        
        validation_results = self.validate_all_data()
        missing_data = self.find_missing_data()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'INCOMPLETE',
            'completion_percentage': validation_results['overall_completion'],
            'summary': validation_results['summary'],
            'companies_status': validation_results['companies_validation'],
            'missing_data': missing_data,
            'next_actions': self.generate_next_actions(validation_results, missing_data),
            'estimated_completion_time': self.estimate_completion_time(validation_results)
        }
        
        # Determine overall status
        if validation_results['overall_completion'] >= 100.0:
            report['overall_status'] = 'COMPLETE'
        elif validation_results['overall_completion'] >= 80.0:
            report['overall_status'] = 'NEARLY_COMPLETE'
        elif validation_results['overall_completion'] >= 50.0:
            report['overall_status'] = 'IN_PROGRESS'
        else:
            report['overall_status'] = 'EARLY_STAGE'
        
        # Save report
        report_file = "output/completion_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"💾 Completion report saved to: {report_file}")
        
        return report
    
    def generate_next_actions(self, validation_results: Dict, missing_data: Dict) -> List[str]:
        """Generate list of next actions needed"""
        actions = []
        
        # Add missing companies
        for company in missing_data['missing_companies']:
            actions.append(f"Scrape data for {company}")
        
        # Add missing days
        for company, missing_days in missing_data['missing_days'].items():
            actions.append(f"Complete {missing_days} missing days for {company}")
        
        # Add missing vehicles
        for company in missing_data['missing_vehicles']:
            actions.append(f"Extract vehicle information for {company}")
        
        # Add quality improvements
        for issue in missing_data['data_quality_issues']:
            company = issue['company']
            actions.append(f"Improve data quality for {company} (current: {issue['quality_score']:.1f}%)")
        
        return actions
    
    def estimate_completion_time(self, validation_results: Dict) -> str:
        """Estimate time to completion"""
        completion = validation_results['overall_completion']
        
        if completion >= 100:
            return "COMPLETE"
        elif completion >= 90:
            return "1-2 hours"
        elif completion >= 75:
            return "2-4 hours"
        elif completion >= 50:
            return "4-8 hours"
        else:
            return "8+ hours"
    
    def verify_100_percent_completion(self) -> bool:
        """Verify that 100% completion has been achieved"""
        logger.info("🔍 VERIFYING 100% COMPLETION")
        logger.info("="*40)
        
        validation_results = self.validate_all_data()
        
        # Check overall completion
        if validation_results['overall_completion'] < 100.0:
            logger.error(f"❌ Overall completion: {validation_results['overall_completion']:.1f}% (target: 100%)")
            return False
        
        # Check all companies are complete
        incomplete_companies = []
        for company, validation in validation_results['companies_validation'].items():
            if not validation['complete']:
                incomplete_companies.append(company)
        
        if incomplete_companies:
            logger.error(f"❌ Incomplete companies: {incomplete_companies}")
            return False
        
        # Check data quality
        if validation_results['summary']['data_quality_score'] < 90.0:
            logger.error(f"❌ Data quality score: {validation_results['summary']['data_quality_score']:.1f}% (target: 90%+)")
            return False
        
        logger.info("✅ 100% COMPLETION VERIFIED!")
        logger.info(f"✅ All {len(self.target_companies)} companies complete")
        logger.info(f"✅ {validation_results['summary']['total_days_scraped']} days scraped")
        logger.info(f"✅ Data quality: {validation_results['summary']['data_quality_score']:.1f}%")
        
        return True

if __name__ == "__main__":
    validator = ValidationSystem()
    
    # Run validation
    validation_results = validator.validate_all_data()
    
    # Find missing data
    missing_data = validator.find_missing_data()
    
    # Generate completion report
    report = validator.generate_completion_report()
    
    # Verify completion
    is_complete = validator.verify_100_percent_completion()
    
    if is_complete:
        logger.info("🎉 MISSION ACCOMPLISHED - 100% COMPLETION ACHIEVED!")
    else:
        logger.info("⚠️ WORK IN PROGRESS - CONTINUE SCRAPING")



