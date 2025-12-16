"""
Backup management operations
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .adb_manager import ADBManager
from config.settings import config
from utils.file_utils import get_directory_size, format_file_size

class BackupManager:
    """Manages backup operations"""
    
    def __init__(self, adb_manager: ADBManager):
        self.adb = adb_manager
        self.config = config
    
    def create_backup_folder(self) -> str:
        """Create a new backup folder"""
        backup_folder = self.config.get_backup_folder()
        os.makedirs(backup_folder, exist_ok=True)
        return backup_folder
    
    def backup_device_info(self, backup_folder: str) -> bool:
        """Backup device information"""
        try:
            # Get device properties
            from config.constants import DEVICE_PROPERTIES_BASIC
            props = self.adb.get_device_props(DEVICE_PROPERTIES_BASIC)
            
            # Save to file
            props_file = os.path.join(backup_folder, "device_properties.txt")
            with open(props_file, 'w', encoding='utf-8') as f:
                for prop, value in props.items():
                    f.write(f"{prop}={value}\n")
            
            # Create backup summary
            summary_file = os.path.join(backup_folder, "backup_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(f"Device Backup - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Device: {props.get('ro.product.manufacturer', 'Unknown')} ")
                f.write(f"{props.get('ro.product.model', 'Unknown')}\n")
                f.write(f"Android: {props.get('ro.build.version.release', 'Unknown')}\n")
                f.write(f"Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return True
        except Exception as e:
            print(f"Error backing up device info: {e}")
            return False
    
    def backup_boot_image(self, backup_folder: str) -> Tuple[bool, str]:
        """Backup boot image"""
        from core.device_manager import DeviceManager
        device_manager = DeviceManager(self.adb)
        
        boot_file = os.path.join(backup_folder, "ogboot.img")
        
        if device_manager.get_boot_image(backup_folder):
            if os.path.exists(boot_file):
                size = os.path.getsize(boot_file)
                return True, f"Boot image backed up ({format_file_size(size)})"
        
        return False, "Failed to backup boot image"
    
    def backup_app(self, package_name: str, backup_folder: str, include_apk: bool = True) -> bool:
        """Backup a single app"""
        try:
            backup_file = os.path.join(backup_folder, f"{package_name}.ab")
            
            cmd = ['backup', '-f', backup_file, package_name]
            if include_apk:
                cmd.append('-apk')
            
            result = self.adb.run_command(cmd)
            
            if result.success and os.path.exists(backup_file):
                return True
            
            return False
        except Exception as e:
            print(f"Error backing up app {package_name}: {e}")
            return False
    
    def backup_user_data(self, backup_folder: str, folders: List[Tuple[str, str]]) -> Dict[str, int]:
        """Backup user data folders"""
        results = {}
        user_data_folder = os.path.join(backup_folder, "User_Data")
        os.makedirs(user_data_folder, exist_ok=True)
        
        for name, remote_path in folders:
            self.adb.update_status(f"Backing up {name}...")
            dest_folder = os.path.join(user_data_folder, name)
            os.makedirs(dest_folder, exist_ok=True)
            
            # Check if folder exists on device
            result = self.adb.run_command(['shell', f'ls {remote_path}'])
            if result.success:
                pull_result = self.adb.pull_file(remote_path, dest_folder)
                if pull_result.success:
                    # Count files
                    file_count = 0
                    for root, dirs, files in os.walk(dest_folder):
                        file_count += len(files)
                    results[name] = file_count
        
        return results
    
    def get_backup_info(self, backup_path: str) -> Dict[str, str]:
        """Get information about a backup"""
        info = {
            'name': os.path.basename(backup_path),
            'path': backup_path,
            'size': '0 B',
            'file_count': 0,
            'created': datetime.fromtimestamp(os.path.getctime(backup_path)).strftime("%Y-%m-%d %H:%M"),
            'modified': datetime.fromtimestamp(os.path.getmtime(backup_path)).strftime("%Y-%m-%d %H:%M"),
        }
        
        if os.path.exists(backup_path):
            # Calculate size
            total_size = get_directory_size(backup_path)
            info['size'] = format_file_size(total_size)
            
            # Count files
            file_count = 0
            for root, dirs, files in os.walk(backup_path):
                file_count += len(files)
            info['file_count'] = file_count
        
        return info
    
    def list_backups(self) -> List[Dict[str, str]]:
        """List all available backups"""
        backups = []
        backup_root = self.config.PATHS['backup_root']
        
        if not os.path.exists(backup_root):
            return backups
        
        for item in os.listdir(backup_root):
            item_path = os.path.join(backup_root, item)
            if os.path.isdir(item_path) and item.startswith('newbackup_'):
                info = self.get_backup_info(item_path)
                backups.append(info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup"""
        backup_path = os.path.join(self.config.PATHS['backup_root'], backup_name)
        
        if not os.path.exists(backup_path):
            return False
        
        try:
            shutil.rmtree(backup_path)
            return True
        except Exception as e:
            print(f"Error deleting backup {backup_name}: {e}")
            return False
