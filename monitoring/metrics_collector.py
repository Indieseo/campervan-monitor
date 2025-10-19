"""
Metrics Collection System for Scraping Operations
Tracks success rates, performance, and data quality
"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
from loguru import logger


class ScrapeMetrics:
    """Track and aggregate scraping metrics"""

    def __init__(self):
        self.metrics = {
            'scrapes_total': 0,
            'scrapes_successful': 0,
            'scrapes_failed': 0,
            'scrapes_partial': 0,

            # Performance metrics
            'avg_duration_seconds': 0.0,
            'min_duration_seconds': float('inf'),
            'max_duration_seconds': 0.0,
            'total_duration_seconds': 0.0,

            # Data quality metrics
            'avg_data_completeness': 0.0,
            'prices_extracted': 0,
            'reviews_extracted': 0,
            'locations_extracted': 0,

            # Error tracking
            'error_types': {},
            'failures_by_competitor': {},

            # Rate metrics
            'success_rate': 0.0,
            'price_extraction_rate': 0.0,
            'review_extraction_rate': 0.0,
        }

        self.session_start = datetime.now()
        self.scrape_history = []

    def record_scrape(self, result: Dict, duration: float, competitor: str):
        """Record a scraping operation"""

        self.metrics['scrapes_total'] += 1

        # Determine success level
        completeness = result.get('data_completeness_pct', 0)
        has_price = result.get('base_nightly_rate') and result['base_nightly_rate'] > 0

        if has_price and completeness >= 50:
            self.metrics['scrapes_successful'] += 1
            status = 'success'
        elif has_price or completeness >= 30:
            self.metrics['scrapes_partial'] += 1
            status = 'partial'
        else:
            self.metrics['scrapes_failed'] += 1
            status = 'failed'

            # Track failure by competitor
            if competitor not in self.metrics['failures_by_competitor']:
                self.metrics['failures_by_competitor'][competitor] = 0
            self.metrics['failures_by_competitor'][competitor] += 1

        # Update performance metrics
        self.metrics['total_duration_seconds'] += duration
        self.metrics['avg_duration_seconds'] = (
            self.metrics['total_duration_seconds'] / self.metrics['scrapes_total']
        )
        self.metrics['min_duration_seconds'] = min(
            self.metrics['min_duration_seconds'], duration
        )
        self.metrics['max_duration_seconds'] = max(
            self.metrics['max_duration_seconds'], duration
        )

        # Update data quality metrics
        if has_price:
            self.metrics['prices_extracted'] += 1

        if result.get('customer_review_avg') or result.get('review_count'):
            self.metrics['reviews_extracted'] += 1

        if result.get('locations_available'):
            self.metrics['locations_extracted'] += 1

        # Update running averages
        self._update_rates()

        # Store in history
        self.scrape_history.append({
            'competitor': competitor,
            'status': status,
            'duration': duration,
            'completeness': completeness,
            'timestamp': datetime.now().isoformat(),
        })

        # Keep history manageable
        if len(self.scrape_history) > 1000:
            self.scrape_history = self.scrape_history[-500:]

        logger.info(
            f"Metrics updated: {competitor} - {status} - {duration:.1f}s - {completeness:.1f}% complete"
        )

    def record_error(self, error_type: str, competitor: str):
        """Record an error occurrence"""
        if error_type not in self.metrics['error_types']:
            self.metrics['error_types'][error_type] = 0
        self.metrics['error_types'][error_type] += 1

    def _update_rates(self):
        """Update calculated rate metrics"""
        total = self.metrics['scrapes_total']
        if total > 0:
            self.metrics['success_rate'] = self.metrics['scrapes_successful'] / total
            self.metrics['price_extraction_rate'] = self.metrics['prices_extracted'] / total
            self.metrics['review_extraction_rate'] = self.metrics['reviews_extracted'] / total

    def get_summary(self) -> Dict:
        """Get metrics summary"""
        runtime = (datetime.now() - self.session_start).total_seconds()

        return {
            **self.metrics,
            'session_runtime_seconds': runtime,
            'session_start': self.session_start.isoformat(),
            'scrapes_per_minute': self.metrics['scrapes_total'] / (runtime / 60) if runtime > 0 else 0,
        }

    def export_metrics(self, format='dict') -> Dict:
        """Export metrics for monitoring"""
        summary = self.get_summary()
        summary['timestamp'] = datetime.now().isoformat()

        if format == 'json':
            return json.dumps(summary, indent=2)
        return summary

    def save_to_file(self, filepath: Optional[Path] = None):
        """Save metrics to JSON file"""
        if filepath is None:
            filepath = Path('data/metrics') / f"scrape_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(self.export_metrics(), f, indent=2)

        logger.info(f"Metrics saved to {filepath}")

    def print_summary(self):
        """Print formatted metrics summary"""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("SCRAPING METRICS SUMMARY")
        print("=" * 60)

        print(f"\nOperations:")
        print(f"  Total Scrapes: {summary['scrapes_total']}")
        print(f"  Successful: {summary['scrapes_successful']} ({summary['success_rate']*100:.1f}%)")
        print(f"  Partial: {summary['scrapes_partial']}")
        print(f"  Failed: {summary['scrapes_failed']}")

        print(f"\nPerformance:")
        print(f"  Avg Duration: {summary['avg_duration_seconds']:.1f}s")
        print(f"  Min Duration: {summary['min_duration_seconds']:.1f}s")
        print(f"  Max Duration: {summary['max_duration_seconds']:.1f}s")
        print(f"  Scrapes/min: {summary['scrapes_per_minute']:.2f}")

        print(f"\nData Extraction:")
        print(f"  Prices Extracted: {summary['prices_extracted']} ({summary['price_extraction_rate']*100:.1f}%)")
        print(f"  Reviews Extracted: {summary['reviews_extracted']} ({summary['review_extraction_rate']*100:.1f}%)")
        print(f"  Locations Extracted: {summary['locations_extracted']}")

        if summary['error_types']:
            print(f"\nErrors:")
            for error_type, count in summary['error_types'].items():
                print(f"  {error_type}: {count}")

        if summary['failures_by_competitor']:
            print(f"\nFailures by Competitor:")
            for comp, count in summary['failures_by_competitor'].items():
                print(f"  {comp}: {count}")

        print("=" * 60 + "\n")


class StructuredLogger:
    """Enhanced structured logging"""

    @staticmethod
    def log_scrape_start(competitor: str, tier: int):
        """Log scrape start with context"""
        logger.bind(
            competitor=competitor,
            tier=tier,
            event='scrape_start'
        ).info(f"Starting scrape: {competitor}")

    @staticmethod
    def log_scrape_complete(competitor: str, result: Dict, duration: float):
        """Log scrape completion with metrics"""
        logger.bind(
            competitor=competitor,
            duration=duration,
            completeness=result.get('data_completeness_pct', 0),
            has_price=bool(result.get('base_nightly_rate')),
            has_reviews=bool(result.get('customer_review_avg')),
            event='scrape_complete'
        ).info(
            f"Scrape complete: {competitor} - "
            f"{duration:.1f}s - {result.get('data_completeness_pct', 0):.1f}% complete"
        )

    @staticmethod
    def log_extraction_success(field: str, value, method: str):
        """Log successful data extraction"""
        logger.bind(
            field=field,
            method=method,
            event='extraction_success'
        ).info(f"Extracted {field}: {value} (method: {method})")

    @staticmethod
    def log_extraction_failure(field: str, reason: str):
        """Log extraction failure"""
        logger.bind(
            field=field,
            reason=reason,
            event='extraction_failure'
        ).warning(f"Failed to extract {field}: {reason}")


# Global metrics instance
_global_metrics = None

def get_metrics() -> ScrapeMetrics:
    """Get global metrics instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = ScrapeMetrics()
    return _global_metrics


if __name__ == "__main__":
    print("Metrics Collection System")
    print("=" * 50)

    # Example usage
    metrics = ScrapeMetrics()

    # Simulate some scrapes
    test_result = {
        'base_nightly_rate': 85.0,
        'customer_review_avg': 4.3,
        'data_completeness_pct': 65.0,
        'locations_available': ['Munich', 'Berlin'],
    }

    metrics.record_scrape(test_result, 25.3, "Roadsurfer")
    metrics.record_scrape(test_result, 30.1, "McRent")

    # Print summary
    metrics.print_summary()
