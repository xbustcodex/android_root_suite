"""
Device management operations
"""

import re
from typing import Dict, List, Optional, Tuple
from .adb_manager import ADBManager
from config.constants import DEVICE_PROPERTIES_BASIC, DEVICE_PROPERTIES_ADVANCED

class DeviceManager:
    """Manages device-specific operations"""
    
    def __init__(self, adb_manager: ADBManager):
        self.adb = adb_manager
    
    def get_detailed_device_info(self) -> Dict[str, Dict[str, str]]:
        """Get comprehensive device information"""
        info = {
            'basic': {},
            'advanced': {},
            'storage': {},
            'network': {},
            'battery': {},
        }
        
        # Get basic properties
        info['basic'] = self.adb.get_device_props(DEVICE_PROPERTIES_BASIC)
        
        # Get advanced properties
        info['advanced'] = self.adb.get_device_props(DEVICE_PROPERTIES_ADVANCED)
        
        # Get storage info
        info['storage'] = self.get_storage_info()
        
        # Get battery info
        info['battery'] = self.get_battery_info()
        
        return info
    
    def get_storage_info(self) -> Dict[str, str]:
        """Get storage information"""
        storage_info = {}
        
        # Get internal storage
        cmd = "df -h /data | tail -1"
        result = self.adb.run_command(['shell', cmd])
        if result.success:
            parts = result.stdout.strip().split()
            if len(parts) >= 5:
                storage_info['internal_total'] = parts[1]
                storage_info['internal_used'] = parts[2]
                storage_info['internal_available'] = parts[3]
                storage_info['internal_use_percent'] = parts[4]
        
        # Get RAM info
        cmd = "cat /proc/meminfo | grep MemTotal"
        result = self.adb.run_command(['shell', cmd])
        if result.success:
            match = re.search(r'MemTotal:\s+(\d+)\s+kB', result.stdout)
            if match:
                ram_kb = int(match.group(1))
                storage_info['ram_total_mb'] = str(ram_kb // 1024)
        
        return storage_info
    
    def get_battery_info(self) -> Dict[str, str]:
        """Get battery information"""
        battery_info = {}
        
        # Try different methods to get battery info
        cmds = [
            "dumpsys battery",
            "cat /sys/class/power_supply/battery/capacity",
        ]
        
        for cmd in cmds:
            result = self.adb.run_command(['shell', cmd])
            if result.success:
                output = result.stdout
                
                # Parse dumpsys battery output
                if "dumpsys" in cmd:
                    level_match = re.search(r'level:\s+(\d+)', output)
                    if level_match:
                        battery_info['level'] = level_match.group(1)
                    
                    status_match = re.search(r'status:\s+(\d+)', output)
                    if status_match:
                        status_map = {1: "Unknown", 2: "Charging", 3: "Discharging", 4: "Not charging", 5: "Full"}
                        status_code = int(status_match.group(1))
                        battery_info['status'] = status_map.get(status_code, "Unknown")
                
                # Parse capacity file
                elif "capacity" in cmd:
                    battery_info['level'] = output.strip()
        
        return battery_info
    
    def check_root_status(self) -> Tuple[bool, str, Optional[str]]:
        """Check if device is rooted and determine root method"""
        # Check for su binary
        result = self.adb.run_command(['shell', 'which su'])
        if not result.success or not result.stdout.strip():
            return False, "Not rooted", None
        
        # Check for Magisk
        magisk_result = self.adb.run_command(['shell', 'su -c "magisk -v"'])
        if magisk_result.success:
            version = magisk_result.stdout.strip()
            return True, "Rooted", f"Magisk {version}"
        
        # Check for KernelSU
        kernelsu_result = self.adb.run_command(['shell', 'su -c "ksud"'])
        if kernelsu_result.success:
            return True, "Rooted", "KernelSU"
        
        # Check for SuperSU
        supersu_result = self.adb.run_command(['shell', 'su -c "su --version"'])
        if supersu_result.success:
            return True, "Rooted", "SuperSU"
        
        return True, "Rooted", "Unknown"
    
    def get_installed_apps(self, system_only: bool = False) -> List[str]:
        """Get list of installed apps"""
        cmd = "pm list packages"
        if system_only:
            cmd += " -s"
        
        result = self.adb.run_command(['shell', cmd])
        if not result.success:
            return []
        
        apps = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                apps.append(line.replace('package:', '').strip())
        
        return apps
    
    def get_boot_image(self, backup_path: str) -> bool:
        """Extract boot image from device"""
        for partition in BOOT_PARTITION_PATHS:
            cmd = f'su -c "dd if={partition} of=/sdcard/boot_backup.img bs=4096 count=32768"'
            result = self.adb.run_command(['shell', cmd])
            
            if result.success:
                # Pull the file
                pull_result = self.adb.pull_file('/sdcard/boot_backup.img', 
                                                f'{backup_path}/ogboot.img')
                
                # Clean up
                self.adb.run_command(['shell', 'rm', '/sdcard/boot_backup.img'])
                
                return pull_result.success
        
        return False
