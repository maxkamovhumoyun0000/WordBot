"""
Backup and Restore functionality for Wordl bot.
Handles database backups, file archiving, and restoration.
"""

import os
import sqlite3
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import logging

log = logging.getLogger("quizbot")

# Configuration
BACKUP_DIR = os.getenv("BACKUP_DIR", "/tmp/wordl_backups")
MAX_BACKUPS = 5  # Keep last 5 backups
DB_PATH = os.getenv("DB_PATH", "/home/ubuntu/bot/bot.db")
GRAMMAR_DIR = os.getenv("GRAMMAR_DIR", "/home/ubuntu/bot/grammar")
IELTS_DIR = os.getenv("IELTS_DIR", "/home/ubuntu/bot/IELTS")

# Create backup directory if it doesn't exist
os.makedirs(BACKUP_DIR, exist_ok=True)


def get_backup_filename() -> str:
    """Generate backup filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"wordl_backup_{timestamp}.zip"


def cleanup_old_backups() -> None:
    """Keep only the last MAX_BACKUPS backups."""
    try:
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith("wordl_backup_") and f.endswith(".zip")],
            reverse=True
        )
        for old_backup in backups[MAX_BACKUPS:]:
            old_path = os.path.join(BACKUP_DIR, old_backup)
            os.remove(old_path)
            log.info(f"Removed old backup: {old_backup}")
    except Exception as e:
        log.error(f"Error cleaning up old backups: {e}")


def create_full_backup() -> Optional[str]:
    """
    Create a complete backup including database and important directories.
    
    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        backup_file = os.path.join(BACKUP_DIR, get_backup_filename())
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database
            if os.path.exists(DB_PATH):
                zipf.write(DB_PATH, arcname=os.path.basename(DB_PATH))
                log.info(f"Added database to backup: {DB_PATH}")
            
            # Add grammar files
            if os.path.exists(GRAMMAR_DIR):
                for root, dirs, files in os.walk(GRAMMAR_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(GRAMMAR_DIR))
                        zipf.write(file_path, arcname=arcname)
                log.info(f"Added grammar files to backup")
            
            # Add IELTS files
            if os.path.exists(IELTS_DIR):
                for root, dirs, files in os.walk(IELTS_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(IELTS_DIR))
                        zipf.write(file_path, arcname=arcname)
                log.info(f"Added IELTS files to backup")
            
            # Add metadata
            metadata = f"Backup created: {datetime.now().isoformat()}\n"
            metadata += f"Database: {DB_PATH}\n"
            metadata += f"Grammar dir: {GRAMMAR_DIR}\n"
            metadata += f"IELTS dir: {IELTS_DIR}\n"
            zipf.writestr("BACKUP_INFO.txt", metadata)
        
        # Cleanup old backups
        cleanup_old_backups()
        
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        log.info(f"✅ Backup created successfully: {backup_file} ({size_mb:.2f} MB)")
        return backup_file
        
    except Exception as e:
        log.error(f"❌ Error creating backup: {e}")
        return None


def create_user_data_backup(user_id: int) -> Optional[str]:
    """
    Create a backup of user's personal data (words, groups, settings).
    
    Args:
        user_id: Database user ID
        
    Returns:
        Path to backup file if successful, None otherwise
    """
    try:
        import word
        
        backup_file = os.path.join(BACKUP_DIR, f"user_{user_id}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Export user's words to XLSX
            with word.db() as conn:
                words = conn.execute(
                    "SELECT english, uzbek FROM words WHERE user_id=? ORDER BY created_at",
                    (user_id,)
                ).fetchall()
                
                settings = conn.execute(
                    "SELECT * FROM users WHERE id=?",
                    (user_id,)
                ).fetchone()
                
                groups = conn.execute(
                    "SELECT id, name FROM groups WHERE owner_id=?",
                    (user_id,)
                ).fetchall()
            
            # Create CSV of words
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["English", "Uzbek"])
            for word_row in words:
                writer.writerow([word_row["english"], word_row["uzbek"]])
            zipf.writestr("words.csv", output.getvalue())
            
            # Add metadata
            metadata = f"User ID: {user_id}\n"
            metadata += f"Backup created: {datetime.now().isoformat()}\n"
            if settings:
                metadata += f"Username: {settings['username']}\n"
                metadata += f"Points: {settings['points']}\n"
            metadata += f"Total words: {len(words)}\n"
            metadata += f"Groups: {len(groups)}\n"
            zipf.writestr("USER_INFO.txt", metadata)
        
        size_kb = os.path.getsize(backup_file) / 1024
        log.info(f"✅ User data backup created: {backup_file} ({size_kb:.2f} KB)")
        return backup_file
        
    except Exception as e:
        log.error(f"❌ Error creating user data backup: {e}")
        return None


def restore_full_backup(backup_file: str) -> Tuple[bool, str]:
    """
    Restore a full backup.
    
    Args:
        backup_file: Path to backup ZIP file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if not os.path.exists(backup_file):
            return False, f"❌ Backup file not found: {backup_file}"
        
        if not backup_file.endswith('.zip'):
            return False, "❌ Invalid backup file format (must be .zip)"
        
        # Create backup of current data first
        current_backup = create_full_backup()
        
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            # Extract to temporary directory first
            temp_dir = os.path.join(BACKUP_DIR, "temp_restore")
            os.makedirs(temp_dir, exist_ok=True)
            
            zipf.extractall(temp_dir)
            
            # Restore database
            db_file = os.path.basename(DB_PATH)
            temp_db = os.path.join(temp_dir, db_file)
            if os.path.exists(temp_db):
                # Verify database integrity
                try:
                    conn = sqlite3.connect(temp_db)
                    conn.execute("SELECT 1")
                    conn.close()
                    # Restore
                    shutil.copy2(temp_db, DB_PATH)
                    log.info(f"✅ Database restored from backup")
                except sqlite3.DatabaseError:
                    return False, "❌ Backup database is corrupted"
            
            # Restore grammar files
            temp_grammar = os.path.join(temp_dir, "grammar")
            if os.path.exists(temp_grammar):
                if os.path.exists(GRAMMAR_DIR):
                    shutil.rmtree(GRAMMAR_DIR)
                shutil.copytree(temp_grammar, GRAMMAR_DIR)
                log.info(f"✅ Grammar files restored")
            
            # Restore IELTS files
            temp_ielts = os.path.join(temp_dir, "IELTS")
            if os.path.exists(temp_ielts):
                if os.path.exists(IELTS_DIR):
                    shutil.rmtree(IELTS_DIR)
                shutil.copytree(temp_ielts, IELTS_DIR)
                log.info(f"✅ IELTS files restored")
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
        
        return True, f"✅ Backup restored successfully!\n💾 Current data backed up as: {os.path.basename(current_backup)}"
        
    except Exception as e:
        log.error(f"❌ Error restoring backup: {e}")
        return False, f"❌ Error during restore: {str(e)}"


def list_backups() -> list:
    """
    List all available backups.
    
    Returns:
        List of (filename, size_mb, created_time) tuples
    """
    try:
        backups = []
        for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if filename.startswith("wordl_backup_") and filename.endswith(".zip"):
                filepath = os.path.join(BACKUP_DIR, filename)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                # Extract timestamp from filename
                ts_str = filename.replace("wordl_backup_", "").replace(".zip", "")
                backups.append((filename, size_mb, ts_str))
        return backups
    except Exception as e:
        log.error(f"Error listing backups: {e}")
        return []


def get_backup_size_info() -> str:
    """Get total size of backups."""
    try:
        total_size = sum(
            os.path.getsize(os.path.join(BACKUP_DIR, f)) / (1024 * 1024)
            for f in os.listdir(BACKUP_DIR)
            if f.startswith("wordl_backup_") and f.endswith(".zip")
        )
        return f"📊 Backup storage: {total_size:.2f} MB"
    except Exception as e:
        log.error(f"Error calculating backup size: {e}")
        return "📊 Backup storage: unknown"
