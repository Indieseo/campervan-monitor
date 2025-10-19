"""
Progress Monitor
Real-time monitoring and reporting of scraping progress
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class ProgressMonitor:
    def __init__(self):
        self.state_file = "output/scraping_state.json"
        self.progress_file = "output/live_progress.json"
        self.monitor_file = "output/progress_monitor.json"
        self.target_companies = [
            'Roadsurfer', 'Camperdays', 'Goboony', 'Outdoorsy', 'RVshare',
            'McRent', 'Yescapa', 'Cruise America'
        ]
        self.target_days = 365
        
    def load_state(self) -> Dict:
        """Load current scraping state"""
        if Path(self.state_file).exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        return {}
    
    def get_current_progress(self) -> Dict:
        """Get current progress status"""
        state = self.load_state()
        
        progress = {
            'timestamp': datetime.now().isoformat(),
            'overall_completion': 0.0,
            'companies_status': {},
            'summary': {
                'total_companies': len(self.target_companies),
                'complete_companies': 0,
                'total_days_scraped': 0,
                'total_target_days': len(self.target_companies) * self.target_days,
                'estimated_completion_time': 'Unknown'
            },
            'trends': {
                'completion_rate_per_hour': 0.0,
                'companies_completed_last_hour': 0,
                'days_scraped_last_hour': 0
            }
        }
        
        total_days_scraped = 0
        complete_companies = 0
        
        for company in self.target_companies:
            company_data = state.get(company, {})
            daily_prices = company_data.get('daily_prices', [])
            vehicles = company_data.get('vehicles', [])
            
            days_scraped = len(daily_prices)
            completion_percentage = (days_scraped / self.target_days) * 100
            
            is_complete = (
                days_scraped >= self.target_days and
                len(vehicles) > 0 and
                company_data.get('success', False)
            )
            
            if is_complete:
                complete_companies += 1
            
            total_days_scraped += days_scraped
            
            progress['companies_status'][company] = {
                'complete': is_complete,
                'days_scraped': days_scraped,
                'target_days': self.target_days,
                'completion_percentage': completion_percentage,
                'vehicles_found': len(vehicles),
                'last_updated': company_data.get('last_updated'),
                'success': company_data.get('success', False),
                'scraping_attempts': company_data.get('scraping_attempts', 0)
            }
        
        # Calculate overall completion
        progress['overall_completion'] = (total_days_scraped / progress['summary']['total_target_days']) * 100
        
        # Update summary
        progress['summary']['complete_companies'] = complete_companies
        progress['summary']['total_days_scraped'] = total_days_scraped
        
        # Estimate completion time
        progress['summary']['estimated_completion_time'] = self.estimate_completion_time(progress)
        
        return progress
    
    def estimate_completion_time(self, progress: Dict) -> str:
        """Estimate time to completion based on current progress"""
        completion = progress['overall_completion']
        
        if completion >= 100:
            return "COMPLETE"
        
        # Simple estimation based on completion percentage
        remaining_percentage = 100 - completion
        
        if completion >= 90:
            return f"{remaining_percentage * 0.1:.1f} hours"
        elif completion >= 75:
            return f"{remaining_percentage * 0.2:.1f} hours"
        elif completion >= 50:
            return f"{remaining_percentage * 0.5:.1f} hours"
        else:
            return f"{remaining_percentage * 1.0:.1f} hours"
    
    def monitor_progress(self, duration_minutes: int = 60):
        """Monitor progress for specified duration"""
        logger.info(f"📊 STARTING PROGRESS MONITORING FOR {duration_minutes} MINUTES")
        logger.info("="*60)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        monitoring_data = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'progress_snapshots': [],
            'summary': {
                'initial_completion': 0.0,
                'final_completion': 0.0,
                'completion_gained': 0.0,
                'companies_completed': 0,
                'days_scraped': 0
            }
        }
        
        # Get initial progress
        initial_progress = self.get_current_progress()
        monitoring_data['summary']['initial_completion'] = initial_progress['overall_completion']
        monitoring_data['progress_snapshots'].append(initial_progress)
        
        logger.info(f"📈 Initial completion: {initial_progress['overall_completion']:.1f}%")
        
        # Monitor loop
        snapshot_count = 0
        while datetime.now() < end_time:
            time.sleep(300)  # Wait 5 minutes between snapshots
            
            current_progress = self.get_current_progress()
            monitoring_data['progress_snapshots'].append(current_progress)
            snapshot_count += 1
            
            # Log progress
            logger.info(f"📊 Snapshot {snapshot_count}: {current_progress['overall_completion']:.1f}% complete")
            
            # Log company status
            for company, status in current_progress['companies_status'].items():
                if status['complete']:
                    logger.info(f"  ✅ {company}: COMPLETE")
                else:
                    logger.info(f"  ⏳ {company}: {status['days_scraped']}/{status['target_days']} days ({status['completion_percentage']:.1f}%)")
        
        # Get final progress
        final_progress = self.get_current_progress()
        monitoring_data['summary']['final_completion'] = final_progress['overall_completion']
        monitoring_data['summary']['completion_gained'] = (
            final_progress['overall_completion'] - initial_progress['overall_completion']
        )
        
        # Calculate trends
        if len(monitoring_data['progress_snapshots']) > 1:
            first_snapshot = monitoring_data['progress_snapshots'][0]
            last_snapshot = monitoring_data['progress_snapshots'][-1]
            
            completion_gained = last_snapshot['overall_completion'] - first_snapshot['overall_completion']
            hours_monitored = duration_minutes / 60
            
            monitoring_data['trends'] = {
                'completion_rate_per_hour': completion_gained / hours_monitored if hours_monitored > 0 else 0,
                'companies_completed': last_snapshot['summary']['complete_companies'] - first_snapshot['summary']['complete_companies'],
                'days_scraped': last_snapshot['summary']['total_days_scraped'] - first_snapshot['summary']['total_days_scraped']
            }
        
        # Save monitoring data
        with open(self.monitor_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2, default=str)
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("MONITORING SUMMARY")
        logger.info("="*60)
        logger.info(f"Initial completion: {monitoring_data['summary']['initial_completion']:.1f}%")
        logger.info(f"Final completion: {monitoring_data['summary']['final_completion']:.1f}%")
        logger.info(f"Completion gained: {monitoring_data['summary']['completion_gained']:.1f}%")
        
        if 'trends' in monitoring_data:
            logger.info(f"Completion rate: {monitoring_data['trends']['completion_rate_per_hour']:.1f}% per hour")
            logger.info(f"Companies completed: {monitoring_data['trends']['companies_completed']}")
            logger.info(f"Days scraped: {monitoring_data['trends']['days_scraped']}")
        
        logger.info(f"💾 Monitoring data saved to: {self.monitor_file}")
        
        return monitoring_data
    
    def generate_progress_report(self) -> Dict:
        """Generate comprehensive progress report"""
        logger.info("📊 GENERATING PROGRESS REPORT")
        logger.info("="*40)
        
        current_progress = self.get_current_progress()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_progress': current_progress,
            'status': self.get_overall_status(current_progress),
            'next_actions': self.get_next_actions(current_progress),
            'alerts': self.check_alerts(current_progress),
            'recommendations': self.get_recommendations(current_progress)
        }
        
        # Save report
        report_file = "output/progress_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"💾 Progress report saved to: {report_file}")
        
        return report
    
    def get_overall_status(self, progress: Dict) -> str:
        """Get overall status based on progress"""
        completion = progress['overall_completion']
        
        if completion >= 100:
            return "COMPLETE"
        elif completion >= 90:
            return "NEARLY_COMPLETE"
        elif completion >= 75:
            return "IN_PROGRESS"
        elif completion >= 50:
            return "HALFWAY"
        elif completion >= 25:
            return "EARLY_STAGE"
        else:
            return "JUST_STARTED"
    
    def get_next_actions(self, progress: Dict) -> List[str]:
        """Get recommended next actions"""
        actions = []
        
        for company, status in progress['companies_status'].items():
            if not status['complete']:
                if status['days_scraped'] == 0:
                    actions.append(f"Start scraping {company}")
                elif status['days_scraped'] < status['target_days']:
                    missing_days = status['target_days'] - status['days_scraped']
                    actions.append(f"Complete {missing_days} missing days for {company}")
                
                if status['vehicles_found'] == 0:
                    actions.append(f"Extract vehicle information for {company}")
        
        return actions
    
    def check_alerts(self, progress: Dict) -> List[Dict]:
        """Check for alerts and issues"""
        alerts = []
        
        # Check for stuck companies
        for company, status in progress['companies_status'].items():
            if not status['complete'] and status['scraping_attempts'] > 5:
                alerts.append({
                    'type': 'STUCK_COMPANY',
                    'company': company,
                    'message': f"{company} has {status['scraping_attempts']} failed attempts",
                    'severity': 'HIGH'
                })
        
        # Check for slow progress
        if progress['overall_completion'] < 10 and len(progress['companies_status']) > 0:
            alerts.append({
                'type': 'SLOW_PROGRESS',
                'message': f"Overall completion is only {progress['overall_completion']:.1f}%",
                'severity': 'MEDIUM'
            })
        
        # Check for data quality issues
        for company, status in progress['companies_status'].items():
            if status['days_scraped'] > 0 and status['vehicles_found'] == 0:
                alerts.append({
                    'type': 'MISSING_VEHICLES',
                    'company': company,
                    'message': f"{company} has pricing data but no vehicles",
                    'severity': 'MEDIUM'
                })
        
        return alerts
    
    def get_recommendations(self, progress: Dict) -> List[str]:
        """Get recommendations for improvement"""
        recommendations = []
        
        # Check completion status
        if progress['overall_completion'] < 50:
            recommendations.append("Focus on getting basic data for all companies first")
        
        # Check for incomplete companies
        incomplete_companies = [company for company, status in progress['companies_status'].items() if not status['complete']]
        if len(incomplete_companies) > 0:
            recommendations.append(f"Prioritize completing: {', '.join(incomplete_companies)}")
        
        # Check for stuck companies
        stuck_companies = [company for company, status in progress['companies_status'].items() if status['scraping_attempts'] > 5]
        if len(stuck_companies) > 0:
            recommendations.append(f"Investigate stuck companies: {', '.join(stuck_companies)}")
        
        return recommendations
    
    def display_live_progress(self):
        """Display live progress in terminal"""
        try:
            while True:
                # Clear screen (works on most terminals)
                print('\033[2J\033[H', end='')
                
                progress = self.get_current_progress()
                
                print("="*80)
                print("🚀 LIVE SCRAPING PROGRESS MONITOR")
                print("="*80)
                print(f"📊 Overall Completion: {progress['overall_completion']:.1f}%")
                print(f"📅 Total Days Scraped: {progress['summary']['total_days_scraped']}/{progress['summary']['total_target_days']}")
                print(f"🏢 Complete Companies: {progress['summary']['complete_companies']}/{progress['summary']['total_companies']}")
                print(f"⏱️  Estimated Time to Complete: {progress['summary']['estimated_completion_time']}")
                print("="*80)
                
                for company, status in progress['companies_status'].items():
                    if status['complete']:
                        print(f"✅ {company:15} | COMPLETE | {status['days_scraped']:3d} days | {status['vehicles_found']:2d} vehicles")
                    else:
                        print(f"⏳ {company:15} | {status['completion_percentage']:5.1f}% | {status['days_scraped']:3d}/{status['target_days']:3d} days | {status['vehicles_found']:2d} vehicles")
                
                print("="*80)
                print(f"🕐 Last Updated: {progress['timestamp']}")
                print("Press Ctrl+C to stop monitoring")
                
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")

if __name__ == "__main__":
    monitor = ProgressMonitor()
    
    # Generate progress report
    report = monitor.generate_progress_report()
    
    # Start live monitoring
    print("Starting live progress monitoring...")
    monitor.display_live_progress()



