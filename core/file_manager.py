"""
File management operations
"""

import os
import shutil
from typing import List, Optional, Tuple
from pathlib import Path

from utils.file_utils import find_files_by_extension

class FileManager:
    """Manages file operations"""
    
    def __init__(self, config):
        self.config = config
    
    def find_boot_images(self) -> List[str]:
        """Find boot images in backup folders"""
        boot_images = []
        
        # Check backup folders
        backup_root = self.config.PATHS['backup_root']
        if os.path.exists(backup_root):
            for folder in os.listdir(backup_root):
                folder_path = os.path.join(backup_root, folder)
                if os.path.isdir(folder_path):
                    images = find_files_by_extension(folder_path, ['.img'])
                    boot_images.extend(images)
        
        # Check boot_images folder
        boot_img_folder = self.config.PATHS['boot_images']
        if os.path.exists(boot_img_folder):
            images = find_files_by_extension(boot_img_folder, ['.img'])
            boot_images.extend(images)
        
        # Check patched_boot folder
        patched_folder = self.config.PATHS['patched_boot']
        if os.path.exists(patched_folder):
            images = find_files_by_extension(patched_folder, ['.img'])
            boot_images.extend(images)
        
        return boot_images
    
    def find_magisk_files(self) -> List[str]:
        """Find Magisk-related files"""
        magisk_files = []
        magisk_folder = self.config.PATHS['magisk']
        
        if os.path.exists(magisk_folder):
            # Find APK files
            apks = find_files_by_extension(magisk_folder, ['.apk'])
            magisk_files.extend(apks)
            
            # Find ZIP files (modules)
            zips = find_files_by_extension(magisk_folder, ['.zip'])
            magisk_files.extend(zips)
        
        return magisk_files
    
    def find_recovery_images(self) -> List[str]:
        """Find recovery images"""
        tools_folder = self.config.PATHS['tools']
        recovery_folder = os.path.join(tools_folder, 'recovery')
        
        if os.path.exists(recovery_folder):
            return find_files_by_extension(recovery_folder, ['.img'])
        
        return []
    
    def find_firmware_files(self) -> Dict[str, List[str]]:
        """Find firmware files by brand"""
        firmware_files = {}
        
        # Check stock firmware folder
        stock_folder = self.config.PATHS['stock_firmware']
        if os.path.exists(stock_folder):
            for file in os.listdir(stock_folder):
                if any(file.endswith(ext) for ext in ['.zip', '.tar', '.tar.md5', '.bin']):
                    brand = self._detect_brand_from_filename(file)
                    if brand not in firmware_files:
                        firmware_files[brand] = []
                    firmware_files[brand].append(os.path.join(stock_folder, file))
        
        return firmware_files
    
    def _detect_brand_from_filename(self, filename: str) -> str:
        """Detect brand from filename"""
        filename_lower = filename.lower()
        
        if 'samsung' in filename_lower or any(x in filename_lower for x in ['sm-', 'g9', 'note', 's2']):
            return 'samsung'
        elif 'xiaomi' in filename_lower or 'miui' in filename_lower or any(x in filename_lower for x in ['mi ', 'redmi', 'poco']):
            return 'xiaomi'
        elif 'oneplus' in filename_lower or 'op_' in filename_lower:
            return 'oneplus'
        elif 'google' in filename_lower or 'pixel' in filename_lower:
            return 'google'
        elif 'nokia' in filename_lower:
            return 'nokia'
        elif 'sony' in filename_lower:
            return 'sony'
        elif 'lg' in filename_lower:
            return 'lg'
        else:
            return 'generic'
    
    def copy_file_to_backup(self, source_file: str, description: str = "") -> Tuple[bool, str]:
        """Copy a file to the current backup folder"""
        try:
            backup_folder = self.config.get_backup_folder()
            
            if not os.path.exists(source_file):
                return False, f"Source file not found: {source_file}"
            
            # Create backup folder if it doesn't exist
            os.makedirs(backup_folder, exist_ok=True)
            
            # Copy file
            filename = os.path.basename(source_file)
            dest_file = os.path.join(backup_folder, filename)
            
            shutil.copy2(source_file, dest_file)
            
            # Add to backup summary
            summary_file = os.path.join(backup_folder, "backup_summary.txt")
            mode = 'a' if os.path.exists(summary_file) else 'w'
            with open(summary_file, mode, encoding='utf-8') as f:
                if mode == 'w':
                    f.write("Backup Files Summary\n")
                    f.write("=" * 50 + "\n\n")
                
                file_size = os.path.getsize(dest_file)
                from utils.file_utils import format_file_size
                size_str = format_file_size(file_size)
                
                f.write(f"{filename} ({size_str})")
                if description:
                    f.write(f" - {description}")
                f.write("\n")
            
            return True, f"File backed up: {filename}"
        
        except Exception as e:
            return False, f"Error copying file: {str(e)}"
