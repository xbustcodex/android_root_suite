import os
import shutil
from datetime import datetime
from typing import Optional, List

def get_directory_size(path: str) -> int:
    """Calculate total size of directory in bytes"""
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total += os.path.getsize(file_path)
    return total

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def cleanup_old_backups(backup_dir: str, keep_count: int = 5) -> int:
    """Clean up old backups, keep only specified number"""
    if not os.path.exists(backup_dir):
        return 0
    
    # Get backup folders
    backups = []
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.isdir(item_path) and item.startswith('newbackup_'):
            ctime = os.path.getctime(item_path)
            backups.append((item, ctime, item_path))
    
    # Sort by creation time (newest first)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Delete old backups
    deleted = 0
    for i, (name, _, path) in enumerate(backups):
        if i >= keep_count:
            try:
                shutil.rmtree(path)
                deleted += 1
            except Exception as e:
                print(f"Failed to delete {name}: {e}")
    
    return deleted

def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """Find files with specific extensions in directory"""
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                found_files.append(os.path.join(root, file))
    return found_files
