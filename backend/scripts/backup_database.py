#!/usr/bin/env python3
"""
Database Backup Script
Creates a timestamped backup of the PostgreSQL database
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path


def create_backup():
    """Create a PostgreSQL database backup"""
    
    # Configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return False
    
    # Parse database URL
    # Format: postgresql://user:password@host:port/dbname
    try:
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        db_user = user_pass[0]
        db_password = user_pass[1] if len(user_pass) > 1 else ""
        db_host = host_port[0]
        db_port = host_port[1] if len(host_port) > 1 else "5432"
        db_name = host_db[1]
    except Exception as e:
        print(f"❌ Failed to parse DATABASE_URL: {e}")
        return False
    
    # Create backups directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{db_name}_{timestamp}.sql"
    
    print(f"📦 Creating backup: {backup_file}")
    
    # Set password environment variable for pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    
    # Run pg_dump
    try:
        cmd = [
            "pg_dump",
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-F", "c",  # Custom format (compressed)
            "-b",  # Include large objects
            "-v",  # Verbose
            "-f", str(backup_file),
            db_name
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Backup created successfully: {backup_file}")
        print(f"📊 Size: {backup_file.stat().st_size / (1024*1024):.2f} MB")
        
        # Cleanup old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, keep_days=7)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ pg_dump command not found. Please install PostgreSQL client tools.")
        return False


def cleanup_old_backups(backup_dir: Path, keep_days: int = 7):
    """Remove backups older than keep_days"""
    import time
    
    cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
    removed_count = 0
    
    for backup_file in backup_dir.glob("backup_*.sql"):
        if backup_file.stat().st_mtime < cutoff_time:
            backup_file.unlink()
            removed_count += 1
            print(f"🗑️  Removed old backup: {backup_file.name}")
    
    if removed_count > 0:
        print(f"✅ Cleaned up {removed_count} old backup(s)")


def restore_backup(backup_file: str):
    """Restore from a backup file"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return False
    
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"⚠️  WARNING: This will restore the database from {backup_file}")
    print("   This may overwrite existing data!")
    confirm = input("   Type 'yes' to continue: ")
    
    if confirm.lower() != "yes":
        print("❌ Restore cancelled")
        return False
    
    # Parse DATABASE_URL (same as create_backup)
    try:
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        db_user = user_pass[0]
        db_password = user_pass[1] if len(user_pass) > 1 else ""
        db_host = host_port[0]
        db_port = host_port[1] if len(host_port) > 1 else "5432"
        db_name = host_db[1]
    except Exception as e:
        print(f"❌ Failed to parse DATABASE_URL: {e}")
        return False
    
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    
    print(f"📥 Restoring backup...")
    
    try:
        cmd = [
            "pg_restore",
            "-h", db_host,
            "-p", db_port,
            "-U", db_user,
            "-d", db_name,
            "-c",  # Clean (drop) database objects before recreating
            "-v",  # Verbose
            str(backup_path)
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
        print(f"✅ Database restored from: {backup_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) < 3:
            print("Usage: python backup_database.py restore <backup-file>")
            sys.exit(1)
        
        success = restore_backup(sys.argv[2])
    else:
        success = create_backup()
    
    sys.exit(0 if success else 1)
