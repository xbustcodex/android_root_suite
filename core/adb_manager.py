import os
import subprocess
import time
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass

@dataclass
class CommandResult:
    """Container for command execution results"""
    returncode: int
    stdout: str
    stderr: str
    success: bool = False
    
    def __post_init__(self):
        self.success = self.returncode == 0

class ADBManager:
    """Manages ADB and Fastboot operations"""
    
    def __init__(self, config):
        self.config = config
        self.adb_path = os.path.join(config.PATHS['platform_tools'], 'adb.exe')
        self.fastboot_path = os.path.join(config.PATHS['platform_tools'], 'fastboot.exe')
        self.current_device: Optional[str] = None
    
    def run_command(self, cmd: List[str], wait: bool = True, shell: bool = False) -> CommandResult:
        """Run a command and return structured result"""
        try:
            if wait:
                result = subprocess.run(
                    cmd,
                    shell=shell,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                return CommandResult(
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
            else:
                subprocess.Popen(cmd, shell=shell)
                return CommandResult(0, "", "")
        except Exception as e:
            return CommandResult(-1, "", str(e))
    
    def check_adb(self) -> Tuple[bool, str]:
        """Check if ADB is available"""
        if os.path.exists(self.adb_path):
            return True, "ADB found"
        
        # Check universal drivers
        universal_adb = os.path.join(self.config.PATHS['driver_pack'], 'universal_adb_driver', 'adb.exe')
        if os.path.exists(universal_adb):
            self.adb_path = universal_adb
            return True, "ADB found in universal drivers"
        
        return False, "ADB not found"
    
    def start_adb_server(self) -> CommandResult:
        """Start ADB server"""
        self.run_command([self.adb_path, 'kill-server'])
        time.sleep(1)
        return self.run_command([self.adb_path, 'start-server'])
    
    def get_devices(self) -> List[Dict[str, str]]:
        """Get list of connected devices"""
        result = self.run_command([self.adb_path, 'devices'])
        
        devices = []
        for line in result.stdout.strip().split('\n')[1:]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) == 2:
                    devices.append({'serial': parts[0], 'status': parts[1]})
        
        if devices:
            self.current_device = devices[0]['serial']
        else:
            self.current_device = None
            
        return devices
    
    def get_device_props(self, prop_names: List[str]) -> Dict[str, str]:
        """Get device properties"""
        props = {}
        for prop in prop_names:
            result = self.run_command([self.adb_path, 'shell', 'getprop', prop])
            if result.success and result.stdout.strip():
                props[prop] = result.stdout.strip()
        return props
    
    def reboot_device(self, mode: str = "") -> CommandResult:
        """Reboot device to specified mode"""
        cmd = [self.adb_path, 'reboot']
        if mode:
            cmd.append(mode)
        return self.run_command(cmd)
    
    def pull_file(self, remote_path: str, local_path: str) -> CommandResult:
        """Pull file from device"""
        return self.run_command([self.adb_path, 'pull', remote_path, local_path])
    
    def push_file(self, local_path: str, remote_path: str) -> CommandResult:
        """Push file to device"""
        return self.run_command([self.adb_path, 'push', local_path, remote_path])
