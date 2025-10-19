"""
Automated Database Backup System
Handles database backups, restoration, and retention
"""

import sys
import shutil
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import json

# Add parent directory to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    from core_config import config
    DATABASE_PATH = config.database.DATABASE_PATH
    BACKUP_DIR = BASE_DIR / "backups"
except ImportError:
    DATABASE_PATH = BASE_DIR / "database" / "campervan_intelligence.db"
    BACKUP_DIR = BASE_DIR / "backups"

# Ensure backup directory exists
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


class DatabaseBackup:
    """
    Database backup manager
    
    Features:
    - Automated backups with compression
    - Multiple backup retention policies
    - Easy restoration
    - Backup verification
    - Rotation based on age
    """
    
    def __init__(self, backup_dir: Optional[Path] = None):
        self.backup_dir = backup_dir or BACKUP_DIR
        self.database_path = DATABASE_PATH
        
        # Backup retention policy
        self.retention_policy = {
            'hourly': {'keep': 24, 'interval': timedelta(hours=1)},      # Keep 24 hourly
            'daily': {'keep': 7, 'interval': timedelta(days=1)},          # Keep 7 daily
            'weekly': {'keep': 4, 'interval': timedelta(weeks=1)},        # Keep 4 weekly
            'monthly': {'keep': 12, 'interval': timedelta(days=30)},      # Keep 12 monthly
        }
    
    def create_backup(self, compress: bool = True, backup_type: str = 'manual') -> Optional[Path]:
        """
        Create a backup of the database
        
        Args:
            compress: Whether to compress the backup with gzip
            backup_type: Type of backup ('manual', 'hourly', 'daily', 'weekly', 'monthly')
        
        Returns:
            Path to backup file or None if failed
        """
        if not self.database_path.exists():
            print(f"❌ Database not found: {self.database_path}")
            return None
        
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{backup_type}_{timestamp}.db"
            
            if compress:
                backup_filename += ".gz"
            
            backup_path = self.backup_dir / backup_filename
            
            # Create backup
            if compress:
                # Copy and compress
                with open(self.database_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Simple copy
                shutil.copy2(self.database_path, backup_path)
            
            # Verify backup
            if backup_path.exists():
                size_mb = backup_path.stat().st_size / (1024 * 1024)
                print(f"✅ Backup created: {backup_path.name} ({size_mb:.2f} MB)")
                
                # Create backup metadata
                self._save_backup_metadata(backup_path, backup_type, compress)
                
                return backup_path
            else:
                print("❌ Backup creation failed")
                return None
                
        except Exception as e:
            print(f"❌ Backup error: {e}")
            return None
    
    def restore_backup(self, backup_path: Path, force: bool = False) -> bool:
        """
        Restore database from a backup
        
        Args:
            backup_path: Path to backup file
            force: Skip confirmation prompt
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        # Confirmation
        if not force:
            print(f"⚠️  This will overwrite the current database: {self.database_path}")
            response = input("Continue? (yes/no): ").lower()
            if response != 'yes':
                print("❌ Restore cancelled")
                return False
        
        try:
            # Create backup of current database before restoring
            if self.database_path.exists():
                current_backup = self.create_backup(compress=True, backup_type='pre_restore')
                print(f"📦 Current database backed up to: {current_backup.name}")
            
            # Restore from backup
            if backup_path.name.endswith('.gz'):
                # Decompress and restore
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.database_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Simple copy
                shutil.copy2(backup_path, self.database_path)
            
            print(f"✅ Database restored from: {backup_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Restore error: {e}")
            return False
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Tuple[Path, dict]]:
        """
        List all available backups with metadata
        
        Args:
            backup_type: Filter by backup type (optional)
        
        Returns:
            List of (path, metadata) tuples
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*.db*"), reverse=True):
            metadata = self._load_backup_metadata(backup_file)
            
            if backup_type and metadata.get('type') != backup_type:
                continue
            
            backups.append((backup_file, metadata))
        
        return backups
    
    def cleanup_old_backups(self, dry_run: bool = False) -> int:
        """
        Clean up old backups according to retention policy
        
        Args:
            dry_run: If True, only show what would be deleted
        
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        backups_by_type = {}
        
        # Group backups by type
        for backup_file in self.backup_dir.glob("backup_*.db*"):
            metadata = self._load_backup_metadata(backup_file)
            backup_type = metadata.get('type', 'manual')
            
            if backup_type not in backups_by_type:
                backups_by_type[backup_type] = []
            
            backups_by_type[backup_type].append((backup_file, metadata))
        
        # Apply retention policy for each type
        for backup_type, backups in backups_by_type.items():
            policy = self.retention_policy.get(backup_type)
            
            if not policy:
                continue  # No retention policy for this type
            
            # Sort by date (newest first)
            backups.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
            
            # Keep only the specified number
            to_delete = backups[policy['keep']:]
            
            for backup_file, metadata in to_delete:
                if dry_run:
                    print(f"Would delete: {backup_file.name}")
                else:
                    backup_file.unlink()
                    metadata_file = backup_file.with_suffix(backup_file.suffix + '.meta')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    print(f"🗑️  Deleted old backup: {backup_file.name}")
                
                deleted_count += 1
        
        return deleted_count
    
    def verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup integrity
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            bool: True if backup is valid, False otherwise
        """
        if not backup_path.exists():
            return False
        
        try:
            # Check if it's compressed
            if backup_path.name.endswith('.gz'):
                # Try to open compressed file
                with gzip.open(backup_path, 'rb') as f:
                    # Read first few bytes to verify it's valid
                    data = f.read(100)
                    if not data:
                        return False
            else:
                # For uncompressed, just check size
                if backup_path.stat().st_size == 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_backup_info(self, backup_path: Path) -> dict:
        """Get detailed information about a backup"""
        if not backup_path.exists():
            return {}
        
        metadata = self._load_backup_metadata(backup_path)
        
        info = {
            'filename': backup_path.name,
            'path': str(backup_path),
            'size_mb': backup_path.stat().st_size / (1024 * 1024),
            'created': datetime.fromtimestamp(backup_path.stat().st_mtime),
            'compressed': backup_path.name.endswith('.gz'),
            'valid': self.verify_backup(backup_path),
            **metadata
        }
        
        return info
    
    def _save_backup_metadata(self, backup_path: Path, backup_type: str, compressed: bool):
        """Save backup metadata"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'type': backup_type,
            'compressed': compressed,
            'original_size': self.database_path.stat().st_size,
            'backup_size': backup_path.stat().st_size
        }
        
        metadata_file = backup_path.with_suffix(backup_path.suffix + '.meta')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_backup_metadata(self, backup_path: Path) -> dict:
        """Load backup metadata"""
        metadata_file = backup_path.with_suffix(backup_path.suffix + '.meta')
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Return basic metadata from file stats
        return {
            'timestamp': datetime.fromtimestamp(backup_path.stat().st_mtime).isoformat(),
            'type': 'unknown',
            'compressed': backup_path.name.endswith('.gz')
        }
    
    def schedule_backup(self, backup_type: str = 'daily') -> Optional[Path]:
        """
        Schedule a backup (called by automation)
        
        Args:
            backup_type: Type of backup to create
        
        Returns:
            Path to backup file
        """
        # Check if we need to create a backup
        existing_backups = self.list_backups(backup_type=backup_type)
        
        if existing_backups:
            last_backup_path, last_backup_meta = existing_backups[0]
            last_backup_time = datetime.fromisoformat(last_backup_meta['timestamp'])
            
            # Get interval for this backup type
            policy = self.retention_policy.get(backup_type)
            if policy:
                time_since_last = datetime.now() - last_backup_time
                
                if time_since_last < policy['interval']:
                    print(f"ℹ️  Skipping {backup_type} backup - last backup was {time_since_last} ago")
                    return None
        
        # Create backup
        backup_path = self.create_backup(compress=True, backup_type=backup_type)
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        return backup_path


def main():
    """Main execution - run backup operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Manager')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'info'],
                       help='Action to perform')
    parser.add_argument('--file', type=str, help='Backup file for restore/info')
    parser.add_argument('--type', type=str, choices=['manual', 'hourly', 'daily', 'weekly', 'monthly'],
                       default='manual', help='Backup type')
    parser.add_argument('--force', action='store_true', help='Force restore without confirmation')
    parser.add_argument('--dry-run', action='store_true', help='Dry run for cleanup')
    
    args = parser.parse_args()
    
    manager = DatabaseBackup()
    
    if args.action == 'backup':
        print(f"\n💾 Creating {args.type} backup...")
        backup_path = manager.create_backup(compress=True, backup_type=args.type)
        if backup_path:
            print(f"\n✅ Backup complete: {backup_path}")
    
    elif args.action == 'restore':
        if not args.file:
            print("❌ Error: --file required for restore")
            sys.exit(1)
        
        backup_path = Path(args.file)
        if not backup_path.is_absolute():
            backup_path = manager.backup_dir / backup_path
        
        print(f"\n🔄 Restoring from: {backup_path.name}")
        success = manager.restore_backup(backup_path, force=args.force)
        
        if success:
            print("\n✅ Restore complete")
        else:
            print("\n❌ Restore failed")
            sys.exit(1)
    
    elif args.action == 'list':
        print("\n📋 Available Backups:")
        print("=" * 80)
        
        backups = manager.list_backups(backup_type=args.type if args.type != 'manual' else None)
        
        if not backups:
            print("No backups found")
        else:
            for backup_path, metadata in backups:
                info = manager.get_backup_info(backup_path)
                print(f"\n📦 {info['filename']}")
                print(f"   Type: {info.get('type', 'unknown')}")
                print(f"   Size: {info['size_mb']:.2f} MB")
                print(f"   Created: {info['created']}")
                print(f"   Valid: {'✅' if info['valid'] else '❌'}")
    
    elif args.action == 'cleanup':
        print(f"\n🧹 Cleaning up old backups{' (DRY RUN)' if args.dry_run else ''}...")
        deleted = manager.cleanup_old_backups(dry_run=args.dry_run)
        print(f"\n{'Would delete' if args.dry_run else 'Deleted'} {deleted} old backup(s)")
    
    elif args.action == 'info':
        if not args.file:
            print("❌ Error: --file required for info")
            sys.exit(1)
        
        backup_path = Path(args.file)
        if not backup_path.is_absolute():
            backup_path = manager.backup_dir / backup_path
        
        info = manager.get_backup_info(backup_path)
        
        if not info:
            print(f"❌ Backup not found: {backup_path}")
            sys.exit(1)
        
        print("\n📊 Backup Information:")
        print("=" * 60)
        for key, value in info.items():
            if key != 'path':
                print(f"{key:.<30} {value}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - create a manual backup
        manager = DatabaseBackup()
        manager.create_backup(compress=True, backup_type='manual')
    else:
        main()


