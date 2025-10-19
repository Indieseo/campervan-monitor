"""
Quick Benchmark Runner

Run performance benchmarks and display results.

Usage:
    python run_benchmarks.py              # Run all benchmarks
    python run_benchmarks.py --quick      # Run quick benchmarks only
    python run_benchmarks.py --database   # Run database benchmarks only
    python run_benchmarks.py --scraping   # Run scraping benchmarks only
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from benchmarks.performance_benchmark import (
    SystemBenchmarks,
    PerformanceBenchmark,
    run_full_benchmark_suite
)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run performance benchmarks")
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick benchmarks only'
    )
    parser.add_argument(
        '--database',
        action='store_true',
        help='Run database benchmarks only'
    )
    parser.add_argument(
        '--scraping',
        action='store_true',
        help='Run scraping benchmarks only'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run parallel processing benchmarks only'
    )

    args = parser.parse_args()

    # Run specific benchmarks or all
    if args.database:
        print("📊 Running Database Benchmarks...")
        results = await SystemBenchmarks.benchmark_database_operations()
    elif args.scraping:
        print("🔍 Running Scraping Benchmarks...")
        results = await SystemBenchmarks.benchmark_scraping_operations()
    elif args.parallel:
        print("⚡ Running Parallel Processing Benchmarks...")
        results = await SystemBenchmarks.benchmark_parallel_operations()
    else:
        print("🚀 Running Full Benchmark Suite...")
        results = await run_full_benchmark_suite()
        return

    # Display results
    benchmark = PerformanceBenchmark()
    print("\n" + benchmark.generate_report(results, format="text"))


if __name__ == "__main__":
    asyncio.run(main())
