"""
Database Optimization - Indexes, Cleanup, and Maintenance
"""

import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from loguru import logger


def create_database_indexes():
    """
    Create indexes for common queries.

    Improves query performance by 5-10x for:
    - Company name + timestamp lookups
    - Timestamp range queries
    - Tier-based filtering
    """
    from models import CompetitorPrice, engine
    from sqlalchemy import Index, inspect

    logger.info("Creating database indexes...")

    try:
        inspector = inspect(engine)
        existing_indexes = inspector.get_indexes('competitor_prices')
        existing_index_names = {idx['name'] for idx in existing_indexes}

        # Define indexes to create
        indexes_to_create = [
            Index('idx_company_timestamp', CompetitorPrice.company_name, CompetitorPrice.scrape_timestamp),
            Index('idx_timestamp', CompetitorPrice.scrape_timestamp),
            Index('idx_tier_timestamp', CompetitorPrice.tier, CompetitorPrice.scrape_timestamp),
            Index('idx_company', CompetitorPrice.company_name),
        ]

        # Create indexes if they don't exist
        created_count = 0
        for index in indexes_to_create:
            if index.name not in existing_index_names:
                try:
                    index.create(engine)
                    logger.info(f"✅ Created index: {index.name}")
                    created_count += 1
                except Exception as e:
                    logger.warning(f"Index {index.name} might already exist: {e}")
            else:
                logger.debug(f"Index {index.name} already exists")

        if created_count > 0:
            logger.info(f"✅ Created {created_count} database indexes")
        else:
            logger.info("All indexes already exist")

        return True

    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return False


def cleanup_old_data(days_to_keep: int = 90, dry_run: bool = False) -> dict:
    """
    Delete old scraping data to save space.

    Args:
        days_to_keep: Number of days of data to keep (default: 90)
        dry_run: If True, only count records without deleting

    Returns:
        Dict with cleanup statistics
    """
    from models import CompetitorPrice, get_session

    logger.info(f"Starting data cleanup (keep last {days_to_keep} days)...")

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    session = get_session()

    try:
        # Count records to delete
        old_records = session.query(CompetitorPrice).filter(
            CompetitorPrice.scrape_timestamp < cutoff_date
        )

        count = old_records.count()

        if dry_run:
            logger.info(f"[DRY RUN] Would delete {count} records older than {cutoff_date.date()}")
            return {
                'dry_run': True,
                'records_to_delete': count,
                'cutoff_date': cutoff_date,
                'deleted': 0
            }

        # Delete old records
        if count > 0:
            deleted = old_records.delete(synchronize_session=False)
            session.commit()
            logger.info(f"✅ Deleted {deleted} old price records")
        else:
            logger.info("No old records to delete")
            deleted = 0

        return {
            'dry_run': False,
            'records_to_delete': count,
            'cutoff_date': cutoff_date,
            'deleted': deleted
        }

    except Exception as e:
        session.rollback()
        logger.error(f"Cleanup failed: {e}")
        raise

    finally:
        session.close()


def vacuum_database():
    """
    Optimize database file (SQLite VACUUM command).

    Reclaims unused space and optimizes internal structure.
    Should be run after large deletions.
    """
    from models import engine

    logger.info("Running database VACUUM...")

    try:
        # VACUUM must be run outside a transaction
        with engine.begin() as connection:
            connection.execute("VACUUM")

        logger.info("✅ Database vacuumed successfully")
        return True

    except Exception as e:
        logger.error(f"VACUUM failed: {e}")
        return False


def backup_database(backup_dir: Optional[Path] = None, compress: bool = True) -> Optional[Path]:
    """
    Create database backup.

    Args:
        backup_dir: Directory to store backups (default: data/backups)
        compress: Whether to compress backup with gzip (default: True)

    Returns:
        Path to backup file, or None if failed
    """
    from core_config import config

    if backup_dir is None:
        backup_dir = Path('data/backups')

    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"campervan_intel_{timestamp}.db"
    backup_path = backup_dir / backup_name

    logger.info(f"Creating database backup: {backup_path}")

    try:
        # Get database path
        db_path = Path('data/campervan_intel.db')

        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            return None

        # Copy database
        shutil.copy2(db_path, backup_path)

        # Compress if requested
        if compress:
            compressed_path = Path(str(backup_path) + '.gz')

            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove uncompressed backup
            backup_path.unlink()
            backup_path = compressed_path

        # Get file size
        size_mb = backup_path.stat().st_size / (1024 * 1024)

        logger.info(f"✅ Backup created: {backup_path} ({size_mb:.2f} MB)")

        # Cleanup old backups (keep last 30 days)
        cleanup_old_backups(backup_dir, days_to_keep=30)

        return backup_path

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None


def cleanup_old_backups(backup_dir: Path, days_to_keep: int = 30):
    """
    Delete old backup files.

    Args:
        backup_dir: Directory containing backups
        days_to_keep: Number of days of backups to keep (default: 30)
    """
    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    cutoff_timestamp = cutoff_time.timestamp()

    deleted_count = 0

    for backup_file in backup_dir.glob("campervan_intel_*.db*"):
        if backup_file.stat().st_mtime < cutoff_timestamp:
            try:
                backup_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old backup: {backup_file.name}")
            except Exception as e:
                logger.warning(f"Failed to delete {backup_file.name}: {e}")

    if deleted_count > 0:
        logger.info(f"✅ Deleted {deleted_count} old backups")


def get_database_stats() -> dict:
    """
    Get database statistics.

    Returns:
        Dict with database stats
    """
    from models import CompetitorPrice, get_session

    session = get_session()

    try:
        # Count total records
        total_records = session.query(CompetitorPrice).count()

        # Count by company
        company_counts = {}
        companies = session.query(CompetitorPrice.company_name).distinct().all()

        for (company,) in companies:
            count = session.query(CompetitorPrice).filter(
                CompetitorPrice.company_name == company
            ).count()
            company_counts[company] = count

        # Get date range
        oldest = session.query(CompetitorPrice).order_by(
            CompetitorPrice.scrape_timestamp.asc()
        ).first()

        newest = session.query(CompetitorPrice).order_by(
            CompetitorPrice.scrape_timestamp.desc()
        ).first()

        # Get database file size
        db_path = Path('data/campervan_intel.db')
        size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0

        return {
            'total_records': total_records,
            'company_counts': company_counts,
            'oldest_record': oldest.scrape_timestamp if oldest else None,
            'newest_record': newest.scrape_timestamp if newest else None,
            'database_size_mb': size_mb,
        }

    finally:
        session.close()


def print_database_stats():
    """Print database statistics"""
    stats = get_database_stats()

    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)

    print(f"\nTotal Records: {stats['total_records']:,}")
    print(f"Database Size: {stats['database_size_mb']:.2f} MB")

    if stats['oldest_record'] and stats['newest_record']:
        date_range = (stats['newest_record'] - stats['oldest_record']).days
        print(f"\nDate Range:")
        print(f"  Oldest: {stats['oldest_record'].date()}")
        print(f"  Newest: {stats['newest_record'].date()}")
        print(f"  Span: {date_range} days")

    print(f"\nRecords by Company:")
    for company, count in sorted(stats['company_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count:,}")

    print("=" * 60 + "\n")


def run_maintenance(
    create_indexes: bool = True,
    cleanup_data: bool = True,
    backup: bool = True,
    vacuum: bool = True,
    days_to_keep: int = 90
) -> dict:
    """
    Run full database maintenance.

    Args:
        create_indexes: Create missing indexes
        cleanup_data: Delete old data
        backup: Create backup
        vacuum: Run VACUUM
        days_to_keep: Days of data to keep

    Returns:
        Dict with maintenance results
    """
    logger.info("=" * 60)
    logger.info("STARTING DATABASE MAINTENANCE")
    logger.info("=" * 60)

    results = {
        'started_at': datetime.now(),
        'indexes_created': False,
        'data_cleaned': False,
        'backup_created': False,
        'vacuumed': False,
    }

    # Create indexes
    if create_indexes:
        results['indexes_created'] = create_database_indexes()

    # Cleanup old data
    if cleanup_data:
        cleanup_result = cleanup_old_data(days_to_keep=days_to_keep)
        results['data_cleaned'] = cleanup_result['deleted'] > 0
        results['records_deleted'] = cleanup_result['deleted']

    # Create backup
    if backup:
        backup_path = backup_database()
        results['backup_created'] = backup_path is not None
        results['backup_path'] = str(backup_path) if backup_path else None

    # Vacuum database
    if vacuum and results['data_cleaned']:
        results['vacuumed'] = vacuum_database()

    results['completed_at'] = datetime.now()
    results['duration'] = (results['completed_at'] - results['started_at']).total_seconds()

    logger.info("=" * 60)
    logger.info("DATABASE MAINTENANCE COMPLETE")
    logger.info(f"Duration: {results['duration']:.2f}s")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    print("Database Optimization Tools")
    print("=" * 60)

    # Show current stats
    print_database_stats()

    # Run maintenance
    print("\nRunning maintenance...")
    results = run_maintenance()

    print("\nMaintenance Results:")
    print(f"  Indexes Created: {results['indexes_created']}")
    print(f"  Data Cleaned: {results['data_cleaned']}")
    if 'records_deleted' in results:
        print(f"  Records Deleted: {results['records_deleted']}")
    print(f"  Backup Created: {results['backup_created']}")
    print(f"  Database Vacuumed: {results['vacuumed']}")
    print(f"  Duration: {results['duration']:.2f}s")

    # Show updated stats
    print_database_stats()
