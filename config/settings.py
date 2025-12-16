
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class AppConfig:
    """Application configuration"""
    BASE_DIR: str = r"C:\AndroidRootSuite_skeleton"
    TIMESTAMP: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Subdirectories
    SUBDIRS: Dict[str, str] = field(default_factory=lambda: {
        'backup_root': r"customer_backups",
        'boot_images': r"boot_images",
        'patched_boot': r"patched_boot",
        'magisk': r"magisk",
        'platform_tools': r"platform-tools",
        'scripts': r"scripts",
        'tools': r"tools",
        'driver_pack': r"driver_pack",
        'stock_firmware': r"stock_firmware",
        'samsung': r"samsung",
        'xiaomi': r"xiaomi",
        'qualcomm': r"qualcomm",
        'mtk': r"mtk",
        'scrcpy': r"scrcpy",
    })
    
    def __post_init__(self):
        """Initialize paths after dataclass creation"""
        self.PATHS = {key: os.path.join(self.BASE_DIR, value) for key, value in self.SUBDIRS.items()}
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        for path in self.PATHS.values():
            os.makedirs(path, exist_ok=True)
        os.makedirs(self.get_backup_folder(), exist_ok=True)
    
    def get_backup_folder(self) -> str:
        """Get current backup folder path"""
        return os.path.join(self.PATHS['backup_root'], f"newbackup_{self.TIMESTAMP}")

# Global configuration instance
config = AppConfig()
